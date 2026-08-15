"""AI bridge — Phase 3 (`Development_roadmap.txt`'s "AI Integration").

This used to call straight into `ai-data`'s services as a stand-in for
real agent orchestration (see git history / `ai-agents/README.md` for the
full story). It now delegates to `ai_agents.orchestrator.AgentOrchestrator`
— the AI Agent Engineer's actual multi-agent implementation — while
keeping the exact same function signatures and `Api_design.txt` §8
response contracts, so the route layer (`app/api/routes/ai.py`) and the
frontend didn't need to change.

This module's remaining job is exactly the boundary-crossing work it
always did: build `ai_data.models.assessment.QuestionResponse` /
`ai_data.models.student.Student` objects from this backend's own
`Answer`/`Question`/`StudentProfile` rows, hand them to the orchestrator,
and translate the structured result back into `app/schemas/ai.py` shapes.
"""

from __future__ import annotations

from functools import lru_cache
from uuid import UUID

from sqlalchemy.orm import Session

from ai_data.models.assessment import QuestionResponse as AIQuestionResponse
from ai_data.models.enums import ConfidenceLevel as AIConfidenceLevel
from ai_data.models.enums import DifficultyLevel as AIDifficultyLevel
from ai_data.models.enums import Subject as AISubject
from ai_data.models.student import Student as AIStudent

from ai_agents.config import AgentConfig
from ai_agents.errors import NoTeachingMaterialError
from ai_agents.llm.client import build_llm_client
from ai_agents.orchestrator import AgentOrchestrator

from app.config.settings import settings
from app.models.assessment import Answer
from app.models.question import Question
from app.models.student import StudentProfile
from app.models.study_plan import StudyPlan
from app.schemas.ai import CoachResponse, DiagnoseResponse, StudyPlanItem, StudyPlanResponse
from app.utils.errors import NotFoundError, ValidationAPIError

# 3 confidence buckets (Database_design.txt stores confidence as an
# Integer 1-5-ish per the API's `"confidence": 3` example) mapped onto
# ai-data's low/medium/high enum — a lossy but reasonable bridge.
_CONFIDENCE_MAP = {1: AIConfidenceLevel.LOW, 2: AIConfidenceLevel.LOW, 3: AIConfidenceLevel.MEDIUM,
                    4: AIConfidenceLevel.HIGH, 5: AIConfidenceLevel.HIGH}

# ai-data's DifficultyLevel is a 1-5 IntEnum matching questions.difficulty
# directly, so no lossy mapping needed there.


def _to_ai_subject(subject: str) -> AISubject:
    try:
        return AISubject(subject.lower())
    except ValueError:
        # Anything outside math/reading/writing (see ai_data.models.enums.
        # Subject) falls back to reading rather than raising — a demo
        # question bank miscategorized as e.g. "verbal" shouldn't break
        # the whole diagnosis.
        return AISubject.READING


@lru_cache
def _get_llm_client():
    """Cached because building it is the part worth not repeating on every
    request (config read + client construction) — `AI_API_KEY` doesn't
    change during a process's lifetime in practice, same assumption
    `config/settings.py`'s own `@lru_cache`d `get_settings()` already
    makes. Reads from `settings` (not raw `os.environ`) so it respects
    `.env`-file configuration the same way every other backend setting
    does — `ai_agents.config.load_config()`'s own env-var reading is for
    standalone/`ai-agents`-only use, not for this backend.
    """
    config = AgentConfig(api_key=settings.ai_api_key, enabled=bool(settings.ai_api_key))
    return build_llm_client(config)


def _get_orchestrator() -> AgentOrchestrator:
    """Built fresh per call (cheap — just wiring, no I/O) rather than also
    cached, deliberately: unlike the API key, `settings.database_url` is
    monkeypatched per-test in `app/tests/conftest.py`'s `client` fixture,
    and reading it live here (like `memory_bridge.py` already does) is
    what makes decision logging land in the same database the rest of a
    given test/request is using, instead of freezing onto whichever
    database happened to be active the first time this was ever called.
    """
    return AgentOrchestrator(llm_client=_get_llm_client(), database_url=settings.database_url)


def _to_ai_student(profile: StudentProfile) -> AIStudent:
    return AIStudent(
        student_id=profile.id,
        target_score=profile.target_score,
        current_score=profile.current_score,
        exam_date=profile.exam_date,
        study_time_daily_minutes=profile.study_time_daily,
        confidence_level=profile.confidence_level,
        learning_style=profile.learning_style,
    )


def _student_profile_row(db: Session, student_id: UUID) -> StudentProfile:
    profile = db.query(StudentProfile).filter_by(id=student_id).first()
    if profile is None:
        # Shouldn't happen in practice — every caller already resolved
        # `student_id` from `student_service.get_profile`, which would
        # have 404'd first. Guarding here anyway rather than letting
        # `_to_ai_student` blow up on `None`.
        raise NotFoundError("Student profile not found")
    return profile


def _student_responses(db: Session, student_id: UUID) -> list[AIQuestionResponse]:
    """Builds ai-data's `QuestionResponse` list from this backend's
    `Answer` + `Question` rows — the actual boundary crossing between the
    two packages' data models.
    """
    rows = (
        db.query(Answer, Question)
        .join(Question, Answer.question_id == Question.id)
        .filter(Answer.student_id == student_id)
        .order_by(Answer.answered_at)
        .all()
    )
    responses = []
    for answer, question in rows:
        responses.append(
            AIQuestionResponse(
                response_id=answer.id,
                student_id=student_id,
                question_id=question.id,
                topic=question.topic,
                subject=_to_ai_subject(question.subject),
                difficulty=AIDifficultyLevel(question.difficulty),
                answer_given=answer.answer_given,
                correct=answer.correct,
                confidence=_CONFIDENCE_MAP.get(answer.confidence, AIConfidenceLevel.MEDIUM),
                response_time_seconds=answer.response_time,
                answered_at=answer.answered_at,
            )
        )
    return responses


def diagnose(db: Session, student_id: UUID) -> DiagnoseResponse:
    responses = _student_responses(db, student_id)
    if not responses:
        raise ValidationAPIError("No answered questions yet — complete an assessment first")

    student = _to_ai_student(_student_profile_row(db, student_id))
    result = _get_orchestrator().diagnose(student, responses)

    return DiagnoseResponse(
        weaknesses=result.weaknesses,
        strengths=result.strengths,
        recommendation=result.recommendation,
    )


def generate_study_plan(db: Session, student_id: UUID) -> StudyPlanResponse:
    responses = _student_responses(db, student_id)
    if not responses:
        raise ValidationAPIError("No answered questions yet — complete an assessment first")

    student = _to_ai_student(_student_profile_row(db, student_id))
    result = _get_orchestrator().plan(student, responses)
    if not result.items:
        raise ValidationAPIError("Not enough data yet to build a study plan — keep practicing")

    items = [
        StudyPlanItem(topic=item.topic, time=f"{item.duration_minutes} minutes", reason=item.reason)
        for item in result.items
    ]

    plan_row = StudyPlan(
        student_id=student_id,
        activity=[item.model_dump() for item in items],
        status="pending",
    )
    db.add(plan_row)
    db.commit()

    return StudyPlanResponse(plan=items)


def coach(db: Session, student_id: UUID, question: str) -> CoachResponse:
    """Delegates to the Coaching Agent (`ai_agents.agents.coaching_agent`),
    which follows the Explain/Guide/Practice/Confirm framework
    (Prompt_strategy.txt §8: "guide, don't just answer") whether or not an
    LLM is configured — see `ai-agents/README.md` for the LLM-first,
    deterministic-fallback design.
    """
    responses = _student_responses(db, student_id)
    student = _to_ai_student(_student_profile_row(db, student_id))

    try:
        result = _get_orchestrator().coach(student, responses, question)
    except NoTeachingMaterialError as exc:
        raise NotFoundError(f"No teaching material found for {exc.topic!r} yet") from exc

    return CoachResponse(explanation=result.explanation, next_question=result.next_question)


def suggest_mission_topic(db: Session, student_id: UUID) -> str | None:
    """Used by `session_service.start_session` to give a learning session
    a meaningful `mission` label (Api_design.txt §9's
    `"mission": "Reading inference practice"` example) instead of a
    generic placeholder. Delegates to the Planning Agent's weak-topic
    priority; returns None if there isn't enough answer history yet,
    callers fall back to a generic mission.
    """
    responses = _student_responses(db, student_id)
    return _get_orchestrator().suggest_mission_topic(responses)

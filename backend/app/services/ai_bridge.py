"""AI bridge — Phase 3 (`Development_roadmap.txt`'s "AI Integration").

As flagged in the README: real agent orchestration is the AI Agent
Engineer's role, not Backend's. Until that exists, this module calls
straight into `ai-data`'s services and shapes the result into the
`Api_design.txt` §8 response contracts, so `/ai/*` routes work end-to-end
today. Swap the internals of these three functions for real agent calls
later — the route layer and response schemas don't need to change.
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from ai_data.models.assessment import QuestionResponse as AIQuestionResponse
from ai_data.models.enums import ConfidenceLevel as AIConfidenceLevel
from ai_data.models.enums import DifficultyLevel as AIDifficultyLevel
from ai_data.models.enums import Subject as AISubject
from ai_data.knowledge.loader import get_concepts_for_topic
from ai_data.services.performance_analyzer import identify_strong_topics, identify_weak_topics
from ai_data.services.recommendation_context import generate_topic_recommendations

from app.models.assessment import Answer
from app.models.question import Question
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

    weak = identify_weak_topics(responses)
    strong = identify_strong_topics(responses)
    recommendations = generate_topic_recommendations(responses, max_recommendations=1)

    recommendation_text = (
        recommendations[0].reason if recommendations else "Keep practicing across all topics evenly."
    )

    return DiagnoseResponse(weaknesses=weak, strengths=strong, recommendation=recommendation_text)


def generate_study_plan(db: Session, student_id: UUID) -> StudyPlanResponse:
    responses = _student_responses(db, student_id)
    if not responses:
        raise ValidationAPIError("No answered questions yet — complete an assessment first")

    recommendations = generate_topic_recommendations(responses)
    if not recommendations:
        raise ValidationAPIError("Not enough data yet to build a study plan — keep practicing")

    # Simple time allocation: higher-priority (lower `priority` number)
    # recommendations get more minutes. Real scheduling against
    # `StudentProfile.study_time_daily` is a reasonable next refinement,
    # not attempted here to avoid overbuilding past the MVP.
    minutes_by_priority = {1: 20, 2: 15, 3: 10, 4: 5, 5: 5}
    items = [
        StudyPlanItem(
            topic=rec.topic or "General Review",
            time=f"{minutes_by_priority.get(rec.priority, 10)} minutes",
            reason=rec.reason,
        )
        for rec in recommendations
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
    """Placeholder Coaching Agent behavior: looks up the student's current
    weakest topic and returns its stored explanation + a worked-example
    prompt as a follow-up question, in the Socratic style
    Prompt_strategy.txt §8 asks for ("guide, don't just answer"). This is
    NOT a real LLM-backed coach — it's a deterministic stand-in so the
    `/ai/coach` endpoint returns something coherent until the AI Agent
    Engineer's real Coaching Agent exists.
    """
    responses = _student_responses(db, student_id)
    weak_topics = identify_weak_topics(responses) if responses else []

    if not weak_topics:
        return CoachResponse(
            explanation=(
                "I don't have enough practice history yet to tailor this — "
                "try a few more questions first, or ask about a specific topic."
            ),
            next_question=None,
        )

    topic = weak_topics[0]
    concepts = get_concepts_for_topic(topic)
    if not concepts:
        raise NotFoundError(f"No teaching material found for {topic!r} yet")

    concept = concepts[0]
    next_question = concept.examples[0].prompt if concept.examples else None
    return CoachResponse(explanation=concept.explanation, next_question=next_question)

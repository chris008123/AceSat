"""Evaluator — hackathon prompt section 11, Phase 8.

Loads the scenario JSON files in `datasets/` and checks whether
`identify_weak_topics()` / `generate_topic_recommendations()` produce the
expected, scenario-defined outcome. This tests *this module's*
personalization logic end to end (synthetic responses -> weak topic ->
recommendation) — the hackathon prompt frames evaluation as testing "the AI
agents," but since agent orchestration belongs to the AI Agent Engineer and
doesn't exist yet, this is the piece of that pipeline that's actually
testable right now. Re-run the same datasets once agents exist to check
their behavior too.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path
from uuid import uuid4

from pydantic import BaseModel

from ai_data.models.assessment import QuestionResponse
from ai_data.models.enums import ConfidenceLevel, DifficultyLevel, Subject
from ai_data.services.performance_analyzer import identify_weak_topics
from ai_data.services.recommendation_context import generate_topic_recommendations

_DEFAULT_DATASETS_DIR = Path(__file__).parent / "datasets"


class EvaluationResult(BaseModel):
    scenario: str
    expected_weakness: str | None
    actual_weak_topics: list[str]
    weakness_matched: bool
    expected_recommendation_action: str | None
    actual_recommendation_actions: list[str]
    recommendation_matched: bool

    @property
    def passed(self) -> bool:
        return self.weakness_matched and self.recommendation_matched


def load_scenarios(datasets_dir: Path | None = None) -> list[dict]:
    directory = datasets_dir or _DEFAULT_DATASETS_DIR
    scenarios = []
    for path in sorted(directory.glob("*.json")):
        with open(path) as f:
            scenarios.append(json.load(f))
    return scenarios


def synthesize_responses(topics: dict) -> list[QuestionResponse]:
    """Turns a scenario's `topics` block into a `QuestionResponse` list,
    in chronological order, so trend detection (which depends on order)
    behaves the same as it would for a real student.
    """
    student_id = uuid4()
    responses: list[QuestionResponse] = []
    for topic, spec in topics.items():
        subject = Subject(spec["subject"])
        difficulty = DifficultyLevel(spec["difficulty"])
        sequence = spec["correct_sequence"]
        n = len(sequence)
        for i, correct in enumerate(sequence):
            responses.append(
                QuestionResponse(
                    response_id=uuid4(),
                    student_id=student_id,
                    question_id=uuid4(),
                    topic=topic,
                    subject=subject,
                    difficulty=difficulty,
                    answer_given="A",
                    correct=correct,
                    confidence=ConfidenceLevel.MEDIUM,
                    response_time_seconds=45,
                    answered_at=datetime.utcnow() - timedelta(days=(n - i)),
                )
            )
    return responses


def run_scenario(scenario: dict) -> EvaluationResult:
    responses = synthesize_responses(scenario["topics"])
    weak_topics = identify_weak_topics(responses)
    recommendations = generate_topic_recommendations(responses)
    recommendation_actions = [r.action.value for r in recommendations]

    expected_weakness = scenario.get("expected_weakness")
    weakness_matched = expected_weakness is None or expected_weakness in weak_topics

    expected_action = scenario.get("expected_recommendation_action")
    recommendation_matched = expected_action is None or expected_action in recommendation_actions

    return EvaluationResult(
        scenario=scenario["scenario"],
        expected_weakness=expected_weakness,
        actual_weak_topics=weak_topics,
        weakness_matched=weakness_matched,
        expected_recommendation_action=expected_action,
        actual_recommendation_actions=recommendation_actions,
        recommendation_matched=recommendation_matched,
    )


def run_all(datasets_dir: Path | None = None) -> list[EvaluationResult]:
    return [run_scenario(s) for s in load_scenarios(datasets_dir)]

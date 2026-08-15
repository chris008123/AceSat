from __future__ import annotations

import pytest

from ai_agents.orchestrator import AgentOrchestrator


def test_orchestrator_diagnose_matches_agent_output(demo_student, declining_reading_inference_responses):
    orchestrator = AgentOrchestrator(llm_client=None)
    result = orchestrator.diagnose(demo_student, declining_reading_inference_responses)

    assert "Reading Inference" in result.weaknesses


def test_orchestrator_plan_matches_agent_output(demo_student, declining_reading_inference_responses):
    orchestrator = AgentOrchestrator(llm_client=None)
    result = orchestrator.plan(demo_student, declining_reading_inference_responses)

    assert result.items[0].topic == "Reading Inference"


def test_orchestrator_coach_matches_agent_output(demo_student, declining_reading_inference_responses):
    orchestrator = AgentOrchestrator(llm_client=None)
    result = orchestrator.coach(demo_student, declining_reading_inference_responses, "help")

    assert result.explanation


def test_orchestrator_suggest_mission_topic(demo_student, declining_reading_inference_responses):
    orchestrator = AgentOrchestrator(llm_client=None)
    assert orchestrator.suggest_mission_topic(declining_reading_inference_responses) == "Reading Inference"


def test_orchestrator_analyze(demo_student, mixed_responses):
    orchestrator = AgentOrchestrator(llm_client=None)
    result = orchestrator.analyze(demo_student, mixed_responses)

    assert result.trend in {"improving", "declining", "steady"}


def test_orchestrator_motivate_and_reflect(demo_student):
    orchestrator = AgentOrchestrator(llm_client=None)

    assert "3" in orchestrator.motivate(streak=3).message
    assert orchestrator.reflect("Grammar").question


def test_orchestrator_without_database_url_skips_logging_silently(
    demo_student, declining_reading_inference_responses
):
    """No `database_url` configured is a normal state (e.g. local dev
    without Postgres wired up yet) — logging must be skipped, not raise.
    """
    orchestrator = AgentOrchestrator(llm_client=None, database_url=None)
    result = orchestrator.diagnose(demo_student, declining_reading_inference_responses)
    assert result is not None


def test_orchestrator_from_env_with_no_api_key_is_fully_deterministic(monkeypatch):
    monkeypatch.delenv("AI_API_KEY", raising=False)
    monkeypatch.delenv("GROQ_API_KEY", raising=False)

    orchestrator = AgentOrchestrator.from_env()

    assert orchestrator.llm_client is None


@pytest.fixture
def isolated_ai_data_db(tmp_path, monkeypatch):
    """Resets ai-data's cached sessionmaker (`ai_data.models.db.
    _SessionLocal` is a module-level singleton, first-call-wins) so this
    test's `database_url` is actually the one used, rather than whatever
    URL a different test happened to initialize it with first.
    """
    import ai_data.models.db as ai_data_db

    monkeypatch.setattr(ai_data_db, "_SessionLocal", None)
    db_url = f"sqlite:///{tmp_path}/test_ai_agents_logs.db"
    ai_data_db.init_db(db_url)
    return db_url


def test_orchestrator_logs_decision_when_database_url_configured(
    demo_student, declining_reading_inference_responses, isolated_ai_data_db
):
    from ai_data.models.db import get_session
    from ai_data.models.memory import AILogRecord

    orchestrator = AgentOrchestrator(llm_client=None, database_url=isolated_ai_data_db)
    orchestrator.diagnose(demo_student, declining_reading_inference_responses)

    with get_session(isolated_ai_data_db) as session:
        logs = session.query(AILogRecord).filter_by(student_id=demo_student.student_id).all()

    assert len(logs) == 1
    assert logs[0].agent_name == "Diagnostic Agent"
    assert "Reading Inference" in logs[0].output_data["weaknesses"]


def test_orchestrator_logging_failure_does_not_break_diagnosis(
    demo_student, declining_reading_inference_responses
):
    """A bogus database_url must degrade gracefully — logging is
    diagnostic, never load-bearing.
    """
    orchestrator = AgentOrchestrator(llm_client=None, database_url="not-a-real-connection-string")
    result = orchestrator.diagnose(demo_student, declining_reading_inference_responses)
    assert "Reading Inference" in result.weaknesses

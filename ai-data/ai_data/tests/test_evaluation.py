from __future__ import annotations

import pytest

from ai_data.evaluation.evaluator import load_scenarios, run_all, run_scenario


def test_five_scenarios_present():
    scenarios = load_scenarios()
    names = {s["scenario"] for s in scenarios}
    assert len(scenarios) == 5
    assert "Student with weak reading inference" in names
    assert "Student with weak algebra" in names
    assert "Student improving rapidly" in names
    assert "Student with inconsistent performance" in names
    assert "Student who repeatedly makes the same mistake" in names


@pytest.mark.parametrize("result", run_all(), ids=lambda r: r.scenario)
def test_scenario_matches_expected_personalization(result):
    assert result.weakness_matched, (
        f"{result.scenario}: expected weakness {result.expected_weakness!r}, "
        f"got weak topics {result.actual_weak_topics!r}"
    )
    assert result.recommendation_matched, (
        f"{result.scenario}: expected action {result.expected_recommendation_action!r}, "
        f"got {result.actual_recommendation_actions!r}"
    )

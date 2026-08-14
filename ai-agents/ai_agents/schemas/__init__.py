"""Agent output contracts — Phase 1.

These are the four structured outputs the hackathon prompt's Phase 1 asks
for: DiagnosticResult, StudyPlan, CoachingResponse, AnalyticsResult. Import
from here (`from ai_agents.schemas import DiagnosticResult`) rather than
the submodules directly.
"""

from __future__ import annotations

from ai_agents.schemas.analytics import AnalyticsResult, TopicTrend
from ai_agents.schemas.coaching import CoachingResponse
from ai_agents.schemas.diagnostic import DiagnosticResult
from ai_agents.schemas.enums import AnalyticsStatus, CoachingResponseType, InterventionUrgency
from ai_agents.schemas.planning import StudyPlan, StudyPlanItem

__all__ = [
    "AnalyticsResult",
    "TopicTrend",
    "CoachingResponse",
    "DiagnosticResult",
    "StudyPlan",
    "StudyPlanItem",
    "AnalyticsStatus",
    "CoachingResponseType",
    "InterventionUrgency",
]

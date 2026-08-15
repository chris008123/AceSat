"""Agent Orchestrator — the AI Agent Engineer's actual deliverable
(Team_assignments.txt §6, Project_modules.txt §6).

This is the piece backend/README.md's "Agent orchestration — a
placeholder, not the real thing" section flagged as missing:
`app/services/ai_bridge.py` previously called straight into ai-data's
analysis functions. It now delegates to `AgentOrchestrator` instead —
same three call sites, same return shapes, real multi-agent reasoning
underneath.

Coordinates the six specialized agents (Diagnostic, Planning, Coaching,
Analytics, Motivation, Reflection — `Agents.txt`) into the
Observe -> Understand -> Decide -> Act -> Evaluate -> Improve loop
described in Agent_workflows.txt §1 and AI_Agent_architecture.txt §2:

    Student Data -> Observation -> Reasoning -> Planning -> Action -> Feedback -> Adaptation

Deliberately DB-agnostic beyond decision logging: callers (the backend)
own fetching `Student`/`QuestionResponse` rows from Postgres and pass them
in — this package only reasons over data it's given, matching ai-data's
own "no DB/API calls in the analysis layer" convention. Decision logging
is the one exception, and mirrors `app/services/memory_bridge.py`'s
pattern of opening its own session against the shared `DATABASE_URL`.
"""

from __future__ import annotations

from uuid import UUID

from ai_data.models.assessment import QuestionResponse
from ai_data.models.student import Student

from ai_agents.agents.analytics_agent import AnalyticsAgent
from ai_agents.agents.coaching_agent import CoachingAgent
from ai_agents.agents.diagnostic_agent import DiagnosticAgent
from ai_agents.agents.motivation_agent import MotivationAgent
from ai_agents.agents.planning_agent import PlanningAgent
from ai_agents.agents.reflection_agent import ReflectionAgent
from ai_agents.config import load_config
from ai_agents.context import build_context
from ai_agents.llm.client import GeminiClient, build_llm_client
from ai_agents.logging import log_decision
from ai_agents.schemas import (
    AnalyticsResult,
    CoachResult,
    DiagnosticResult,
    MotivationResult,
    ReflectionPrompt,
    StudyPlanResult,
)


class AgentOrchestrator:
    def __init__(self, llm_client: GeminiClient | None = None, database_url: str | None = None) -> None:
        self.llm_client = llm_client
        self.database_url = database_url

        self.diagnostic_agent = DiagnosticAgent(llm_client)
        self.planning_agent = PlanningAgent(llm_client)
        self.coaching_agent = CoachingAgent(llm_client)
        self.analytics_agent = AnalyticsAgent(llm_client)
        self.motivation_agent = MotivationAgent(llm_client)
        self.reflection_agent = ReflectionAgent(llm_client)

    @classmethod
    def from_env(cls, database_url: str | None = None) -> "AgentOrchestrator":
        """Builds an orchestrator using `AI_API_KEY`/`GOOGLE_API_KEY` from
        the environment if present (Deployment_architecture.txt §5), or a
        fully deterministic one (zero LLM calls, zero network) if not.
        Safe to call with no key configured at all — every agent degrades
        to its rule-based fallback rather than raising, which is what
        keeps local dev, CI, and the hackathon demo's backup plan working
        with no credentials.
        """
        return cls(llm_client=build_llm_client(load_config()), database_url=database_url)

    def _log(self, agent_name: str, student_id: UUID, input_payload, output_payload) -> None:
        if not self.database_url:
            return
        try:
            input_data = (
                input_payload if isinstance(input_payload, dict) else input_payload.model_dump(mode="json")
            )
            log_decision(
                self.database_url,
                student_id,
                agent_name,
                input_data,
                output_payload.model_dump(mode="json"),
            )
        except Exception:
            # Logging is diagnostic, never load-bearing — a missing/broken
            # ai_logs table should never take down a diagnosis, plan, or
            # coaching response.
            pass

    def diagnose(self, student: Student, responses: list[QuestionResponse]) -> DiagnosticResult:
        context = build_context(student, responses)
        result = self.diagnostic_agent.run(context, responses)
        self._log(self.diagnostic_agent.name, student.student_id, context, result)
        return result

    def plan(self, student: Student, responses: list[QuestionResponse]) -> StudyPlanResult:
        context = build_context(student, responses)
        result = self.planning_agent.run(context, responses)
        self._log(self.planning_agent.name, student.student_id, context, result)
        return result

    def coach(self, student: Student, responses: list[QuestionResponse], question: str) -> CoachResult:
        context = build_context(student, responses)
        result = self.coaching_agent.run(context, responses, question)
        self._log(self.coaching_agent.name, student.student_id, context, result)
        return result

    def analyze(self, student: Student, responses: list[QuestionResponse]) -> AnalyticsResult:
        result = self.analytics_agent.run(responses)
        self._log(self.analytics_agent.name, student.student_id, {"response_count": len(responses)}, result)
        return result

    def motivate(self, streak: int, recent_improvement: str | None = None) -> MotivationResult:
        return self.motivation_agent.run(streak, recent_improvement)

    def reflect(self, topic: str | None = None) -> ReflectionPrompt:
        return self.reflection_agent.run(topic)

    def suggest_mission_topic(self, responses: list[QuestionResponse]) -> str | None:
        """Used for `sessions.mission` (Api_design.txt §9) — delegates to
        the Planning Agent, since "what should today's session be about"
        is a planning decision, not a diagnostic one.
        """
        return self.planning_agent.suggest_mission_topic(responses)

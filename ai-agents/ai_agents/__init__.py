"""AceMentor AI — AI Agent Engineer module.

Owns the agentic intelligence layer: Diagnostic, Planning, Coaching, and
Analytics agents, plus the orchestrator that connects them. Consumes
`ai-data`'s `StudentContext` / `MemoryService` / knowledge base as inputs
(see `ai-data/README.md` for that boundary) and produces the structured
outputs defined in `ai_agents.schemas`.

Phase 1 (this phase): schemas only, no agent logic or LLM calls yet.
"""

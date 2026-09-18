# 10-slide PPT outline

Use one idea per slide. Do not paste policy dumps.

1. **Title** — AeroResolve: an agentic airline disruption resolution system. AIONOS Assignment 3. Simulated prototype.
2. **Problem** — After a delay/cancel, the passenger is forced to become a policy expert under time pressure. They need: what happened, what I’m due, what you can do, who takes over.
3. **Journey compression** — Uncertainty → queue → retell → negotiate → wait. AeroResolve: identify → options → authorized action or human packet.
4. **Product principle** — Chat is the front door. The product is UNDERSTAND → GROUND → DECIDE → ACT → ESCALATE → AUDIT. Unknown ≠ allowed.
5. **Context engineering** — Per-turn packet: retrieve this passenger only; compute policy in code; forbid other customers and raw policy text. Two prompts: extract vs respond.
6. **Architecture** — Next.js customer UI + FastAPI + policy engine + Elasticsearch/JSON KB. LLM optional. Diagram from docs/architecture.md.
7. **Scenario 1 Priya** — Cancelled SK-204. Refund allowed. Business upgrade not in policy → escalate. Gold = priority rebook only. Return unaffected.
8. **Scenario 2 Arvind** — 4h delay. Meal + lounge. Hotel denied (threshold is more than 5 hours). Frustration does not create an exception.
9. **Scenario 3 Meher + manager desk** — 6h: delayed-hours hotel, not full night. ₹2,000 > ₹1,500 → supervisor. Desk shows packet + knowledge graph.
10. **Limits and tools** — Data pack only. Simulated actions. Inputs/sources/assumptions. Cursor used for build; policy tests prove the model does not own decisions. Ask me to walk the context panel live.

Speaker note for every scenario slide: show the context panel (decision / why / source), not just the chat bubble.

# AeroResolve

Policy-governed **airline disruption resolution agent** for the AIONOS.AI Agentic AI Factory Internship — Assignment 3.

This is not a generic LLM chatbot. The model talks. Deterministic code decides.

**Product thesis:** during a disruption, passengers need a trusted resolution layer that translates policy into options, takes authorized action, and knows when a human must take over.

> Simulated prototype. It does not book real flights, pay refunds, or reserve hotels.

## Run locally (one command path)

```bash
# 1) Backend
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# 2) Passenger platform (AERO Resolve)
cd frontend
npm install
npm run dev
# http://localhost:3000

# 3) Supervisor CRM (AERO OPS) — separate app
cd frontend-manager
npm install
npm run dev
# http://localhost:3001
```

These are two products. The passenger app has no CRM navigation. Supervisors work only in AERO OPS. Both UIs are built from `packages/ui` via a **platform factory** (`createPlatform("customer" | "manager")`).

Optional Elasticsearch (passenger knowledge base). Without Docker, the same JSON data pack is used:

```bash
docker compose up -d elasticsearch
# restart uvicorn so it can ping localhost:9200
```

Optional LLM phrasing: copy `.env.example` to `backend/.env` and set `OPENAI_API_KEY`. Demos work with no key (heuristic extract + template reply).

```bash
cd backend && pytest -q
```

## What reviewers should try

Sign in on AERO Resolve (`http://localhost:3000/login`). Priya Nair, Arvind Kulkarni, and Meher Kaur are **already enrolled members**, not demo chips. Shared prototype password: `Aero2026!`.

1. **Priya Nair** (`priya.nair@example.com`) — cancellation: refund allowed; business-class upgrade not in policy → escalate. Return flight remains unaffected. Gold ≠ extra compensation.
2. **Arvind Kulkarni** (`arvind.kulkarni@example.com`) — 4h delay: meal voucher + lounge; hotel denied (not more than 5 hours).
3. **Meher Kaur** (`meher.kaur@example.com`) — 6h delay: delayed-hours hotel allowed, full night denied; ₹2,000 fare waiver escalates (limit ₹1,500).

Open a new account from **Join** to confirm dynamic onboarding. New members start as Standard and must add their own trip — the agent will not invent a flight number.

The right-hand **This turn's context** panel is the product: identity, retrieved facts, missing slots, decision JSON with reason and source.

Optional Elasticsearch (passenger knowledge base). Without Docker, the same JSON data pack is used:

LLMs handle ambiguity and wording. Deterministic systems handle policy, authority, and irreversible actions.

See [docs/architecture.md](docs/architecture.md).

## Inputs, sources, and assumptions

**Inputs / sources (only these):**

- Assignment 3 data pack: customer profiles, bookings, five service rules, allowed vs prohibited actions, three mandatory scenarios.
- Scenario fixture: Meher’s ₹2,000 fare difference is from section 6 of the data pack, not from the booking table. No alternative flight number is supplied.
- Sample conversations A–C are tone/style only. They are not policy and not facts about Priya, Arvind, or Meher.

**Assumptions (documented, not silent policy):**

- Delay bands are independent thresholds: more than 5 hours is also more than 3 hours, so lounge still applies at 6 hours.
- ₹500 is stated only for delays **under 3 hours**. Longer delays receive a meal voucher with no amount invented.
- No next-available inventory is supplied; 24-hour rebooking is simulated without inventing a flight number.
- Unknown ≠ allowed. Missing benefits are denied or escalated.

External airline research informed UX only (progress per interaction, human backup). It did **not** become compensation rules.

## AI tools used

- **Cursor (Grok)** — architecture, context-engineering design, code generation, tests, README, PPT/demo outlines.
- **Optional OpenAI API** — extract JSON and polish replies if `OPENAI_API_KEY` is set. Policy outcomes are never taken from the model.
- All policy numbers, customers, and escalation thresholds were copied from the supplied data pack and covered by pytest.

## Context engineering (customer agent)

Each turn builds a `CustomerAgentContext` packet:

| Kind | Contents |
| --- | --- |
| Plan | Which slices this turn needs — a status question fetches no fixture, no other legs, no policy |
| Retrieve | This passenger, this booking, this session, plus queried policy clauses, recalled turns, remembered facts |
| Compute | Entitlements, deny, escalate |
| Narrate | Decisions as prose, each carrying the clause that justifies it |
| Forbid | Other passengers, whole rule bodies for the model to reinterpret, invented flights |

Two narrow prompts: **extract** (no eligibility fields) and **respond** (explain an already-decided result from grounded facts).

`policies.json` is indexed at clause granularity, so a six-hour delay cites only the
more-than-five-hours clause and never sees the ₹500 under-three-hours band. Replacing the raw
context dump with narrated facts plus citations cut the respond prompt by about 65 percent
across the three scenarios (roughly 5,000 to 1,800 tokens).

Retrieval grounds and cites. It never decides — `policy/engine.py` keeps its own constants,
and `pytest` asserts retrieval cannot move a policy outcome.

## Repository

- `backend/data/` — verbatim pack
- `backend/policy/engine.py` — deterministic rules
- `backend/agent/planner.py` — decides which slices a turn retrieves
- `backend/agent/retrieve.py` — runs the plan against the knowledge store
- `backend/agent/context.py` — context assembler and grounded narration
- `backend/products/knowledge/corpus.py` — `policies.json` flattened to clauses
- `backend/kb/store.py` — Elasticsearch + JSON fallback, same retrieval contract
- `backend/main.py` — FastAPI
- `frontend/` — Next.js customer chat + manager desk
- `docs/` — architecture, 10-slide PPT outline, 15-minute demo script

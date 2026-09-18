# AeroResolve

Policy-governed **airline disruption resolution agent** for the AIONOS.AI Agentic AI Factory Internship — Assignment 3.

This is not a generic LLM chatbot. The model talks. Deterministic code decides.

**Product thesis:** during a disruption, passengers need a trusted resolution layer that translates policy into options, takes authorized action, and knows when a human must take over.

> Simulated prototype. It does not book real flights, pay refunds, or reserve hotels.

## Assignment 3 requirement coverage

| Brief requirement | Where it lives |
| --- | --- |
| Understand the customer's intent | `agent/extract.py`, heuristic extractor with optional LLM |
| Ask only necessary questions | `missing_slots` and `DecisionStatus.ASK`; one slot per turn |
| Use the supplied data and policies | `policies.json` indexed as clauses, retrieved and quoted with a clause id |
| Recommend or execute the correct next action | `ALLOW` → simulated action, logged as `SIMULATED` |
| Handle an angry or confused customer | emotion detected in the extractor, acknowledged in one line; `test_emotion.py` proves tone cannot change an outcome |
| Escalate when authority is missing | `ESCALATE` → supervisor case packet with transcript, decisions, and graph |
| Preserve a clear conversation and action record | events, cases, graph edges, and a per-turn audit event |

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

Optional LLM phrasing: copy `.env.example` to `backend/.env` and set one key. Demos work with
no key at all (heuristic extract + template reply), and policy outcomes are identical either way.

```bash
GEMINI_API_KEY=...   # free tier, preferred
GROQ_API_KEY=...     # free tier
```

Four providers are supported — Gemini, Groq, xAI, and OpenAI — because all of them speak the
OpenAI wire format, so only a base URL and model name change. Leave `LLM_PROVIDER` unset and the
first key present wins, free tiers first. `LLM_PROVIDER=none` forces the deterministic path.

Check what loaded, without printing the key:

```bash
curl localhost:8000/api/llm/health              # provider, model, caps, budget left
curl localhost:8000/api/llm/health?probe=true   # also confirms the key authenticates
curl -X POST localhost:8000/api/llm/reload      # re-read .env without a restart
```

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
- **Optional Gemini / Groq / xAI / OpenAI** — extract JSON and polish replies when a key is present. Policy outcomes are never taken from the model.
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

## Cost control

Every model call passes through `backend/llm/`, which is the only place this codebase talks to
a provider. That single chokepoint carries all the ceilings:

| Ceiling | Default | Env var |
| --- | --- | --- |
| Tokens per extract call | 200 | `LLM_MAX_TOKENS_EXTRACT` |
| Tokens per respond call | 220 | `LLM_MAX_TOKENS_RESPOND` |
| Request timeout | 8s | `LLM_TIMEOUT_SECONDS` |
| Calls per conversation | 12 | `LLM_MAX_CALLS_PER_SESSION` |
| Calls per process per day | 500 | `LLM_MAX_CALLS_PER_PROCESS` |
| Spend per day | $1.00 | `LLM_DAILY_BUDGET_USD` |

Identical utterances are served from an extraction cache, since extraction runs at temperature 0.

Breaching a ceiling is not an error. `LlmClient.complete` returns nothing and the caller falls
back to its deterministic path, so the passenger still gets the policy-approved answer and only
the phrasing degrades. The reason is counted under `degradations` at `/api/llm/health`. Because
the policy engine never calls a model, no setting here can change a decision — a claim
`test_llm.py` and `test_policy.py` enforce together.

## Repository

- `backend/data/` — verbatim pack
- `backend/policy/engine.py` — deterministic rules
- `backend/agent/planner.py` — decides which slices a turn retrieves
- `backend/agent/retrieve.py` — runs the plan against the knowledge store
- `backend/agent/context.py` — context assembler and grounded narration
- `backend/llm/` — provider resolution, token caps, and spend ceilings
- `backend/products/knowledge/corpus.py` — `policies.json` flattened to clauses
- `backend/kb/store.py` — Elasticsearch + JSON fallback, same retrieval contract
- `backend/main.py` — FastAPI
- `frontend/` — Next.js customer chat + manager desk
- `docs/` — architecture, 10-slide PPT outline, 15-minute demo script

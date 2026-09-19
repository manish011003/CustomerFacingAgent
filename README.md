# AeroResolve

Policy-governed **airline disruption resolution agent** for the AIONOS.AI Agentic AI Factory Internship — Assignment 3.

This is not a generic LLM chatbot. The model orchestrates. Deterministic tools decide.

**Product thesis:** during a disruption, passengers need a trusted resolution layer that translates policy into options, takes authorized action, and knows when a human must take over.

> Simulated prototype. It does not book real flights, pay refunds, or reserve hotels.

## Assignment 3 requirement coverage

| Brief requirement | Where it lives |
| --- | --- |
| Understand the customer's intent | `agent/extract.py`, heuristic extractor with optional LLM |
| Ask only necessary questions | `missing_slots` and `DecisionStatus.ASK`; one slot per turn |
| Use the supplied data and policies | `policies.json` indexed as clauses, retrieved and quoted with a clause id |
| Recommend or execute the correct next action | `ALLOW` → simulated action, logged as `SIMULATED` |
| Handle an angry or confused customer | emotion detected in the extractor, acknowledged in one line; `test_emotion.py` proves tone cannot change an outcome. Frustration is a separate audited signal (`classify_frustration` tool + heuristic fallback), written only above `KB_AUTO_STORE_THRESHOLD`, and can never change eligibility |
| Escalate when authority is missing | `ESCALATE` → supervisor case packet, tagged with an `EscalationReason` code. `SEVERE_CUSTOMER_DISTRESS` is the one duty-of-care member, reported apart from authority limits |
| Answer how-to and new-trip asks without inventing money | `IssueFamily` router (`agent/router.py`): disruption stays on the packed engine; `HELP_QUESTION` cites `help.json`; `BOOKING_ASSIST` collects origin / destination / date / passengers. A look-only departure appears only after those slots are filled |
| Close the case only when the passenger says so | Issuing a voucher does not resolve the case. CSAT popup (`feedback_popup`) appears only after `case_status=resolved` |
| Preserve a clear conversation and action record | events, cases, graph edges (`HAS_BOOKING`, `EVALUATED_UNDER`, `DENIED_BY`, `ESCALATED_TO`, `EXHIBITS_FRUSTRATION`), and a per-turn audit event |
| Show it works | containment rate, grounding coverage, p95 latency, and spend at `/api/analytics/containment`; frustration buckets at `/api/analytics/frustration` |

## Surfaces

Exactly two product surfaces, plus one look-only exit:

1. **Customer — Resolution Agent** (`frontend`, http://localhost:3000) — one conversation. Choices, confirmations, and escalations land in the thread. A 1–5 CSAT dialog appears only after the passenger closes the case.
2. **Internal — Operations** (`frontend-manager`, http://localhost:3001) — audit what the agent did. Staff credentials required. Not linked from the passenger chat.
3. **Exit board** (`/exit`) — leaving chat after a completed booking-assist request. Upcoming catalog only; no ticketing.

## Live demo

Passenger chat and Operations run from one origin. Staff is at `/ops`.

```bash
npx vercel --prod
# passenger  https://aeroresolve.vercel.app
# operations https://aeroresolve.vercel.app/ops
```

`vercel.json` is a Vercel Services project: passenger Next.js, operations Next.js at `/ops`, and FastAPI at `/api/*`. In the Vercel project set:

- `GROQ_API_KEY` or `GEMINI_API_KEY` — live phrasing; without a key the heuristic path still answers
- `LLM_PROVIDER=groq` — recommended so a spent Gemini quota does not stall every turn
- `DATABASE_URL` — optional. Unset, the JSON pack loads (demo accounts work; tokens reset on a cold start)

Health check: `GET /api/health`.

Docker / Render remain available for a long-lived process with Postgres:

```bash
docker compose up --build web
# http://localhost:8000          passenger
# http://localhost:8000/ops      operations
```

[Deploy to Render](https://render.com/deploy?repo=https://github.com/manish011003/CustomerFacingAgent) (`render.yaml` + `Dockerfile`).

## Run locally

```bash
# 0) Durable store (keeps signups, cases, and login tokens across restarts)
docker compose up -d postgres

# 1) Backend
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# copy ../.env.example to .env — includes DATABASE_URL for local Postgres
uvicorn main:app --reload --port 8000

# 2) Customer chat
cd frontend
npm install
npm run dev
# http://localhost:3000

# 3) Operations dashboard
cd frontend-manager
npm install
npm run dev
# http://localhost:3001
```

Postgres is the system of record. If `DATABASE_URL` is unset or Postgres is down, the factory falls through to Elasticsearch (when Docker is up), then the in-memory JSON data pack. The JSON path is wiped when uvicorn restarts.

```bash
docker compose up -d postgres
# restart uvicorn so it can connect at localhost:5432
```

Optional Elasticsearch (BM25 retrieval over the same passenger KB):

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

A free tier runs out per model, not per project, so one model going quiet should not cost the
whole LLM path. The Gemini family stands behind the chosen model — `gemini-2.5-flash`, then
`gemini-2.5-flash-lite`, then the `gemini-flash-lite-latest` and `gemini-flash-latest` aliases —
and a model that will not answer hands the call to the next name in that chain. Probing that
family on a free key returned 429 "quota exceeded" or 503 "high demand" on about half of it at
once, which is the case this exists for: exhausting `2.5-flash` now costs `flash-lite`'s plainer
wording instead of costing the model path entirely. The aliases are last because they survive
retirement — `gemini-2.5-pro` is still listed by the endpoint and 404s as "no longer available"
when called, so a chain of pinned versions ages badly.

At most three models are tried per call, so a dead family cannot stack up one timeout per model
in front of the passenger, and a model that refuses stops leading the chain for five minutes
rather than being dropped. `LLM_MODEL` only moves a model to the head of the chain;
`LLM_FALLBACK_MODELS` replaces the chain, and `=none` tries exactly one model.

Model names in a chain are perishable, which is the argument for keeping them in one table.
Groq retired the Llama 3.x pair this file first documented to enterprise-only access — both now
404 as "does not exist or you do not have access to it" on a free key — so the Groq chain is
`openai/gpt-oss-20b`, then `openai/gpt-oss-120b`, then `qwen/qwen3.8-27b`, ordered
cheapest-and-fastest first. `tools/probe_models.py` is what catches this: it calls every model in
the chain and reports which ones answer, because appearing in `models.list()` does not mean a
model will serve a request.

Check what loaded, without printing the key:

```bash
cd backend && .venv/bin/python tools/verify_llm.py
```

That resolves the provider, authenticates the key, makes one real call, then runs a real turn and
asserts the three fixed policy outcomes did not move with a model in the loop. The pytest suite
never touches the network, so this script is the only thing that exercises a provider for real.
`tools/probe_models.py` reports which models in the chain your key actually serves.

Three things live keys taught us, all now handled:

- **Gemini 2.5 thinks by default and bills the thinking to `max_tokens`**, so a 220-token cap left
  13 tokens for the answer and the passenger got `"I understand this delay is frustrating, Me"` —
  truncated mid-word. The agent now sends `reasoning_effort=none`, since rewording an
  already-decided reply requires no deliberation, and refuses any completion that stopped on
  `length` rather than shipping half a sentence.
- **Asked only to "rewrite more naturally", the model answered with a menu of options.** The
  respond prompt now states the required output shape, and a rewrite that adds or drops a money
  amount is discarded in favour of the approved text. A polish may change any word; it may not
  change the money.
- **`gpt-oss` typesets.** It returned `500\u202fINR` and `six\u2011hour`, using a narrow no-break
  space and a non-breaking hyphen. Cosmetic on screen, but a thin space between digits reads as
  two separate numbers, so a rewrite that changed nothing would have failed the money check and
  been thrown away. Spacing is flattened to ASCII before the comparison.

The free tier allows 5 requests per minute per model, which is what the model chain is for: during
verification `gemini-2.5-flash` hit its limit mid-turn and `gemini-2.5-flash-lite` answered
instead, so the turn completed with full policy detail rather than degrading.

A per-minute limit recovers; a per-day quota does not. With the Gemini daily quota spent, all four
models in that chain refused at once and every turn fell back to templates — correct outcomes,
plainer wording, and `model_unavailable` on each turn's `degraded` list saying exactly why.
Switching to `LLM_PROVIDER=groq` restored the polish, and moved p95 latency from 8.2s to 1.8s:
turns were spending seconds collecting refusals from models that had nothing left to give.

The same state is available over HTTP:

```bash
curl localhost:8000/api/llm/health              # provider, model chain, caps, budget left
curl localhost:8000/api/llm/health?probe=true   # also confirms the key authenticates
curl -X POST localhost:8000/api/llm/reload      # re-read .env without a restart
```

```bash
cd backend && pytest -q
```

## What reviewers should try

Sign in at `http://localhost:3000/login`. The chat UI is the same for every passenger. The three assignment travellers are already enrolled; shared prototype password: `Aero2026!`.

1. **Priya Nair** (`priya.nair@example.com`) — cancellation: refund or rebook in the thread; business-class upgrade not in policy → escalate. Return flight remains unaffected. Gold ≠ extra compensation.
2. **Arvind Kulkarni** (`arvind.kulkarni@example.com`) — 4h delay: meal voucher + lounge; hotel denied (not more than 5 hours).
3. **Meher Kaur** (`meher.kaur@example.com`) — 6h delay: delayed-hours hotel allowed, full night denied; ₹2,000 fare waiver escalates (limit ₹1,500).

Then sign in to Operations. The passenger chat does not link to it. Use the quiet **Staff** control at the bottom of `http://localhost:3000/login`, or open `http://localhost:3001` directly.

Prototype staff account: `ops@aeroresolve.local` / `AeroOps2026!`. Passenger passwords do not work there. Read the case: transcript, policy used, actions, and why it escalated.

Join from the login screen to confirm a new passenger can use the same chat. New members start as Standard. Then try:

- **New trip** — “book a flight” asks origin, destination, date, and passengers. No departure card until those four are filled. Delhi → Goa on a catalog date shows look-only `SK-441`; tapping it leaves chat for `/exit`. The agent will not invent a fare.
- **How-to** — “How do I check in?” cites the passenger help guide, not delay vouchers.
- **Beyond policy** — “give me 100000 INR” escalates once. A later “hi” does not repeat the handover card.
- **Resolution** — after in-policy actions, the agent asks if the case is resolved. The 1–5 popup appears only when they say it is (or rate 4–5).

LLMs handle ambiguity and wording. Deterministic systems handle policy, authority, and irreversible actions.

See [docs/system-architecture.md](docs/system-architecture.md) for HLD, engines, and flows. Loop notes: [docs/architecture.md](docs/architecture.md).

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

## Containment: the measured answer

The assessment question is how close an agent gets to replacing a human. That is a number, so
every turn records one. `GET /api/analytics/containment`, also included in `/api/analytics/summary`:

```json
{
  "turns": 5,
  "containment_rate": 0.4,
  "escalations_by_reason": {
    "unknown_entitlement": 1,
    "fare_waiver_above_limit": 1,
    "legal_or_formal": 1
  },
  "grounding_coverage": 1.0,
  "p95_latency_ms": 250,
  "est_cost_per_contained_turn_usd": 0.0
}
```

**Read the rate next to the reasons.** That 40 percent is measured over the three assignment
scenarios plus a legal threat — a set selected to force escalation. Every escalation there is a
boundary the data pack draws on agent authority: ₹2,000 exceeds the ₹1,500 waiver limit, a free
business upgrade appears in no supplied rule, and a legal threat must go to a human immediately.
No agent, human or automated, is permitted to decide those alone, so containment on this set is
capped well below 100 percent by policy rather than by capability. On realistic traffic, where
most contacts are status and entitlement questions, the same code contains the turn.

`EscalationReason` is a closed enum, which is what makes the breakdown meaningful: escalations
aggregate by cause instead of by free text, and a test asserts no `ESCALATE` decision can ship
without one.

`SEVERE_CUSTOMER_DISTRESS` is the one member that is not a data-pack authority limit. It fires
when `classify_frustration` is confident the passenger needs a person. Containment reports it
under `distress_escalations`, separately from `authority_escalations`, so a duty-of-care
handover is never read as a policy boundary. Low-confidence observations are logged for audit
and excluded from the primary buckets at `/api/analytics/frustration`.

**Grounding coverage of 1.0** means every claim the agent made to a passenger traced to a
retrieved policy clause. That is the anti-hallucination property stated as a measurement rather
than a promise.

A captured live run of all three scenarios is in [docs/demo-transcript.txt](docs/demo-transcript.txt),
reproducible with `.venv/bin/python tools/demo_scenarios.py` from `backend/`. On Groq's
`gpt-oss-20b` that run measured 100 percent grounding, p50 298ms and p95 1817ms, and
**$0.0004 for the whole four-turn conversation** — about a hundredth of a cent per turn.

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
| Models tried per call | 3 | `LlmClient.MAX_ATTEMPTS` |
| Cooldown after a model refuses | 300s | `LLM_MODEL_COOLDOWN_SECONDS` |

Identical utterances are served from an extraction cache, since extraction runs at temperature 0.

A ceiling is checked once per turn, not once per model, so walking the fallback chain is a retry
of one logical call and cannot buy itself extra headroom. Only a model that actually answered is
billed and counted, which is why an exhausted model costs latency and nothing else.

Breaching a ceiling is not an error. `LlmClient.complete` returns nothing and the caller falls
back to its deterministic path, so the passenger still gets the policy-approved answer and only
the phrasing degrades. The reason is counted under `degradations` at `/api/llm/health`, where a
refusal is named against the model that refused. Because
the policy engine never calls a model, no setting here can change a decision — a claim
`test_llm.py` and `test_policy.py` enforce together.

## Repository

- `backend/data/` — verbatim pack, plus `help.json` and `scheduled_flights.json`
- `backend/policy/engine.py` — deterministic rules
- `backend/policy/handlers/assist.py` — booking slots and help (never money)
- `backend/agent/router.py` — `IssueFamily`: disruption / assist / help / unclassified
- `backend/products/inventory.py` — look-only departures after a route is known
- `backend/agent/planner.py` — decides which slices a turn retrieves
- `backend/agent/retrieve.py` — runs the plan against the knowledge store
- `backend/agent/context.py` — context assembler and grounded narration
- `backend/agent/closure.py` — sticky escalation; CSAT only after the passenger closes
- `backend/llm/` — provider resolution, token caps, and spend ceilings
- `backend/products/knowledge/corpus.py` — `policies.json` flattened to clauses
- `backend/kb/store.py` — Postgres + Elasticsearch + JSON fallback, same retrieval contract
- `backend/main.py` — FastAPI
- `frontend/` — Next.js customer resolution chat (`/exit` is the look-only board)
- `frontend-manager/` — Next.js operations dashboard
- `docs/` — architecture, 10-slide PPT outline, 15-minute demo script

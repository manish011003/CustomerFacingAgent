# Graph Report - Assesment_project_Custormer-Facing_Resolution_Agent_AIONOS  (2026-09-18)

## Corpus Check
- 113 files · ~28,734 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 878 nodes · 2221 edges · 51 communities (43 shown, 8 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 213 edges (avg confidence: 0.57)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `a47730e6`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- schemas.py
- test_retrieval.py
- index.ts
- devDependencies
- devDependencies
- compilerOptions
- compilerOptions
- main.py
- CustomerAgentContext
- LlmFactory
- 15-Minute Live Demo
- ElasticsearchOrJSON
- Policy Engine
- AeroResolve
- scripts
- Context Engineering
- CustomerAgentContext
- AERO OPS
- PolicyEngine
- frontend/app/layout.tsx
- frontend-manager/app/layout.tsx
- frontend-manager/next.config.js
- frontend/next.config.js
- frontend-manager/next-env.d.ts
- frontend-manager/tailwind.config.js
- frontend/next-env.d.ts
- frontend/tailwind.config.js
- PassengerKnowledgeStore
- AuthSession
- LlmConfig
- test_llm.py
- client_with
- LlmBudget
- LlmClient
- evaluate_policy
- Customer
- PickySdk
- CredentialHasher

## God Nodes (most connected - your core abstractions)
1. `PassengerKnowledgeStore` - 52 edges
2. `PolicyDecision` - 42 edges
3. `evaluate_policy()` - 38 edges
4. `SessionMemory` - 37 edges
5. `client_with()` - 35 edges
6. `handle_chat()` - 34 edges
7. `StubSdk` - 34 edges
8. `LlmClient` - 33 edges
9. `Customer` - 32 edges
10. `LlmBudget` - 31 edges

## Surprising Connections (you probably didn't know these)
- `Model Talks, Deterministic Code Decides` --semantically_similar_to--> `AIONOS-Style Constraint`  [INFERRED] [semantically similar]
  README.md → docs/architecture.md
- `Fail Closed on Unknown Benefits` --semantically_similar_to--> `Unknown ≠ Allowed`  [INFERRED] [semantically similar]
  docs/demo-script.md → README.md
- `FastAPI` --conceptually_related_to--> `AeroResolve`  [INFERRED]
  backend/requirements.txt → README.md
- `Optional OpenAI LLM Phrasing` --conceptually_related_to--> `TemplateOrOptionalLLM`  [INFERRED]
  README.md → docs/architecture.md
- `pytest` --conceptually_related_to--> `Policy Engine`  [INFERRED]
  backend/requirements.txt → README.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Three Mandatory Review Scenarios** — readme_priya_nair_scenario, readme_arvind_kulkarni_scenario, readme_meher_kaur_scenario [EXTRACTED 1.00]
- **Context-First Loop Flow** — docs_architecture_customer_message, docs_architecture_retrieve_this_passenger_only, docs_architecture_extract_intent, docs_architecture_policy_engine, docs_architecture_customer_agent_context, docs_architecture_template_or_optional_llm, docs_architecture_this_turn_context_panel, docs_architecture_elasticsearch_or_json, docs_architecture_escalation_packet, docs_architecture_manager_desk [EXTRACTED 1.00]
- **Resolution Decision Outcomes** — docs_architecture_allow, docs_architecture_ask, docs_architecture_deny, docs_architecture_escalate [EXTRACTED 1.00]

## Communities (51 total, 8 thin omitted)

### Community 0 - "schemas.py"
Cohesion: 0.16
Nodes (29): PolicyHandlerFactory, Maps a request type to a PolicyHandler. Engine never constructs handlers itself., DecisionStatus, EscalationReason, PolicyDecision, PolicyEvaluation, Why authority ran out, as a closed set so escalations aggregate. Every member…, RequestType (+21 more)

### Community 1 - "test_retrieval.py"
Cohesion: 0.05
Nodes (80): assemble(), context_contains_forbidden(), _disruption(), narrate(), packet_for_ui(), Render the decided packet as prose with clause-level citations. Every line is…, render_extract_prompt(), render_respond_prompt() (+72 more)

### Community 2 - "index.ts"
Cohesion: 0.08
Nodes (51): AccountPage(), factory, Me, factory, LoginPage(), Member, factory, Msg (+43 more)

### Community 3 - "devDependencies"
Cohesion: 0.07
Nodes (29): dependencies, next, react, react-dom, devDependencies, autoprefixer, postcss, tailwindcss (+21 more)

### Community 4 - "devDependencies"
Cohesion: 0.07
Nodes (29): dependencies, next, react, react-dom, devDependencies, autoprefixer, postcss, tailwindcss (+21 more)

### Community 5 - "compilerOptions"
Cohesion: 0.07
Nodes (28): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+20 more)

### Community 6 - "compilerOptions"
Cohesion: 0.07
Nodes (28): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+20 more)

### Community 7 - "main.py"
Cohesion: 0.11
Nodes (33): reset_session(), add_my_booking(), analytics(), assess(), case(), cases(), chat(), containment() (+25 more)

### Community 8 - "CustomerAgentContext"
Cohesion: 0.14
Nodes (18): Facade — always goes through ReplyFactory., render_reply(), ReplyFactory, CustomerAgentContext, ABC, ReplyRenderer, LlmPolishedReplyRenderer, Phrasing only. The template reply is already policy-approved, and every path… (+10 more)

### Community 9 - "LlmFactory"
Cohesion: 0.14
Nodes (17): ExtractorFactory, Clients request an IntentExtractor. They never construct concrete extractors., LlmFactory, Clients request an LlmClient. They never read provider environment variables.…, Extraction, IntentExtractor, ABC, Product: turn a customer utterance into structured extraction. Never decides… (+9 more)

### Community 10 - "15-Minute Live Demo"
Cohesion: 0.19
Nodes (14): ManagerDesk, Arvind Chip Demo, Drive Video Plan, 15-Minute Live Demo, Manager Desk Demo, Meher Chip Demo, Priya Chip Demo, Arvind Scenario Slide (+6 more)

### Community 11 - "ElasticsearchOrJSON"
Cohesion: 0.22
Nodes (10): elasticsearch Python Client, Elasticsearch Service, Conversation Graph Edges, CustomerMessage, ElasticsearchOrJSON, Knowledge Base Indices, RetrieveThisPassengerOnly, Optional Elasticsearch Knowledge Base (+2 more)

### Community 12 - "Policy Engine"
Cohesion: 0.22
Nodes (9): pytest, Fail Closed on Unknown Benefits, Journey Compression, Limits and Tools, Passenger Forced to Become Policy Expert, UNDERSTAND GROUND DECIDE ACT ESCALATE AUDIT, Unknown ≠ Allowed, Policy Engine (+1 more)

### Community 13 - "AeroResolve"
Cohesion: 0.29
Nodes (8): FastAPI, Uvicorn, AIONOS-Style Constraint, Context-First Loop, Architecture Slide, AeroResolve, Model Talks, Deterministic Code Decides, Product Thesis

### Community 14 - "scripts"
Cohesion: 0.25
Nodes (7): name, private, scripts, dev:api, dev:ops, dev:web, test

### Community 15 - "Context Engineering"
Cohesion: 0.33
Nodes (7): openai Python SDK, ExtractIntent, Context Engineering Slide, Context Engineering, Extract Prompt, Optional OpenAI LLM Phrasing, Respond Prompt

### Community 16 - "CustomerAgentContext"
Cohesion: 0.33
Nodes (7): CustomerAgentContext, TemplateOrOptionalLLM, ThisTurnContextPanel, This Turn's Context Demo Beat, Context Assembler, CustomerAgentContext, This Turn's Context Panel

### Community 17 - "AERO OPS"
Cohesion: 0.60
Nodes (6): AERO OPS, AERO Resolve, createPlatform Factory Boundary, AERO OPS, AERO Resolve, Platform Factory

### Community 18 - "PolicyEngine"
Cohesion: 0.33
Nodes (6): ALLOW, ASK, DENY, ESCALATE, EscalationPacket, PolicyEngine

### Community 27 - "PassengerKnowledgeStore"
Cohesion: 0.06
Nodes (25): KnowledgeStoreFactory, Clients request a PassengerKnowledgeStore. They never construct JSON or…, KnownFact, One retrieved policy clause. Clause-level, never a whole rule body., RuleHit, StyleHit, TurnHit, PassengerKnowledgeStore (+17 more)

### Community 28 - "AuthSession"
Cohesion: 0.18
Nodes (6): AuthFactory, Session tokens are a singleton product so login survives across requests., InMemoryTokenSession, AuthSession, ABC, Product: issue and resolve passenger session tokens.

### Community 42 - "LlmConfig"
Cohesion: 0.09
Nodes (21): LlmResult, _dedupe(), _detect_provider(), disabled_config(), _fallback_models(), _float(), _int(), LlmConfig (+13 more)

### Community 43 - "test_llm.py"
Cohesion: 0.13
Nodes (24): A client that can never call out, for tests and for LLM_PROVIDER=none., from_env(), Provider resolution, spend ceilings, and graceful degradation. Nothing here…, Anyone who pointed OPENAI_* at Gemini before this layer existed keeps working., One key covers every Gemini model, so quota on one is not quota on all., Family names mean nothing at someone else's endpoint, so none are assumed., Belt and braces: prove the None above is not a swallowed network error., test_a_disabled_provider_has_no_models_to_fall_back_to() (+16 more)

### Community 44 - "client_with"
Cohesion: 0.15
Nodes (22): client_with(), config(), Regression: the original renderer sent no max_tokens at all., Day totals cannot answer "what did this turn cost" once turns overlap., Records every request and answers with canned text., StubSdk, test_a_cached_call_is_counted_but_not_charged(), test_a_ceiling_breach_is_attributed_to_the_turn_that_hit_it() (+14 more)

### Community 45 - "LlmBudget"
Cohesion: 0.13
Nodes (6): LlmBudget, Which model actually answered. The chain means it may not be the first., Every ceiling that stops a runaway bill, plus an extraction cache. A breach is…, Name the breached ceiling, or None to proceed. Records nothing — the caller…, Record a degradation the client hit rather than a ceiling, e.g. a timeout., Start metering one conversational turn, so its cost can be reported. Day totals…

### Community 46 - "LlmClient"
Cohesion: 0.13
Nodes (8): LlmClient, The chain, with cooling models moved to the back rather than dropped. Nothing…, Provider state without leaking the key. `probe` costs one cheap call., The single place this codebase talks to a model. `complete` returns None…, Tokens, cost, and degradations attributable to one turn., Built once, on first use. Disabled providers never construct one., Stop leading with a model that just refused, for a cooldown. Free-tier quota is…, test_key_is_never_exposed_by_health()

### Community 47 - "evaluate_policy"
Cohesion: 0.12
Nodes (38): simulate(), ExtractedRequest, delay_entitlements(), evaluate_policy(), Independent thresholds from the data pack. Does not invent amounts for >3h meal…, _percentile(), Nearest-rank percentile over a pre-sorted list., fresh_store() (+30 more)

### Community 48 - "Customer"
Cohesion: 0.15
Nodes (15): _facts(), OnboardingFactory, Booking, BookingIntake, Customer, SignupRequest, TravelHistory, PassengerOnboarding (+7 more)

### Community 49 - "PickySdk"
Cohesion: 0.14
Nodes (20): chained(), models_tried(), PickySdk, Serves only the models it was given a quota for; the rest raise 429. This is…, A model that returns nothing is as useless as one that errors., Five timeouts in a row would be five times the wait for the passenger., Free-tier quota lasts hours, so re-leading with it would waste the walk., Demoted, never retired: quota comes back and the preferred model resumes. (+12 more)

### Community 50 - "CredentialHasher"
Cohesion: 0.28
Nodes (5): HasherFactory, CredentialHasher, ABC, Product: hash and verify passenger passwords. Clients never pick an algorithm., Pbkdf2Hasher

## Knowledge Gaps
- **123 isolated node(s):** `factory`, `factory`, `Passenger`, `inter`, `metadata` (+118 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **8 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `PassengerKnowledgeStore` connect `PassengerKnowledgeStore` to `Customer`, `test_retrieval.py`, `CredentialHasher`, `AuthSession`?**
  _High betweenness centrality (0.041) - this node is a cross-community bridge._
- **Why does `RequestType` connect `schemas.py` to `test_retrieval.py`, `main.py`, `LlmFactory`, `test_llm.py`, `client_with`, `evaluate_policy`, `PickySdk`, `PassengerKnowledgeStore`?**
  _High betweenness centrality (0.032) - this node is a cross-community bridge._
- **Why does `LlmBudget` connect `LlmBudget` to `LlmFactory`, `LlmConfig`, `test_llm.py`, `client_with`, `LlmClient`, `PickySdk`?**
  _High betweenness centrality (0.029) - this node is a cross-community bridge._
- **Are the 9 inferred relationships involving `PassengerKnowledgeStore` (e.g. with `HasherFactory` and `Booking`) actually correct?**
  _`PassengerKnowledgeStore` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Are the 14 inferred relationships involving `PolicyDecision` (e.g. with `RebookHandler` and `RefundOriginalHandler`) actually correct?**
  _`PolicyDecision` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Are the 8 inferred relationships involving `SessionMemory` (e.g. with `IntentExtractor` and `LlmExtractor`) actually correct?**
  _`SessionMemory` has 8 INFERRED edges - model-reasoned connections that need verification._
- **What connects `factory`, `factory`, `Passenger` to the rest of the system?**
  _123 weakly-connected nodes found - possible documentation gaps or missing edges._
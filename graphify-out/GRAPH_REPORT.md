# Graph Report - Assesment_project_Custormer-Facing_Resolution_Agent_AIONOS  (2026-09-18)

## Corpus Check
- 115 files · ~31,181 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 923 nodes · 2357 edges · 60 communities (51 shown, 9 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 225 edges (avg confidence: 0.57)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `cb513cd8`
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
- client.py
- test_llm.py
- client_with
- LlmBudget
- LlmClient
- evaluate_policy
- PassengerOnboarding
- PickySdk
- CredentialHasher
- ElasticsearchKnowledgeStore
- knowledge/base.py
- Fixed
- test_factories.py
- config.py
- LlmConfig
- PassengerSelfServiceOnboarding
- .disabled
- .rule_ids_for_source

## God Nodes (most connected - your core abstractions)
1. `PassengerKnowledgeStore` - 52 edges
2. `client_with()` - 46 edges
3. `StubSdk` - 44 edges
4. `PolicyDecision` - 42 edges
5. `SessionMemory` - 39 edges
6. `evaluate_policy()` - 38 edges
7. `handle_chat()` - 36 edges
8. `LlmClient` - 34 edges
9. `LlmBudget` - 32 edges
10. `Customer` - 32 edges

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

## Communities (60 total, 9 thin omitted)

### Community 0 - "schemas.py"
Cohesion: 0.16
Nodes (27): PolicyHandlerFactory, Maps a request type to a PolicyHandler. Engine never constructs handlers itself., DecisionStatus, EscalationReason, PolicyDecision, Why authority ran out, as a closed set so escalations aggregate. Every member…, RequestType, PolicyHandler (+19 more)

### Community 1 - "test_retrieval.py"
Cohesion: 0.06
Nodes (73): assemble(), context_contains_forbidden(), _disruption(), _facts(), narrate(), packet_for_ui(), Render the decided packet as prose with clause-level citations. Every line is…, render_respond_prompt() (+65 more)

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
Nodes (33): reset_session(), OnboardingFactory, add_my_booking(), analytics(), assess(), case(), cases(), chat() (+25 more)

### Community 8 - "CustomerAgentContext"
Cohesion: 0.17
Nodes (13): Facade — always goes through ReplyFactory., render_reply(), ReplyFactory, CustomerAgentContext, ABC, ReplyRenderer, _line(), TemplateReplyRenderer (+5 more)

### Community 9 - "LlmFactory"
Cohesion: 0.07
Nodes (37): render_extract_prompt(), _query(), ExtractorFactory, Clients request an IntentExtractor. They never construct concrete extractors., LlmFactory, Clients request an LlmClient. They never read provider environment variables.…, Extraction, IntentExtractor (+29 more)

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
Cohesion: 0.14
Nodes (6): KnownFact, PassengerKnowledgeStore, Any, Product: passenger 360 / events / cases / graph. Clients never construct a…, How much of the work needed no human, and where authority ran out. Only turns…, Optional dual-write. JSON product is in-memory only.

### Community 28 - "AuthSession"
Cohesion: 0.19
Nodes (6): AuthFactory, Session tokens are a singleton product so login survives across requests., InMemoryTokenSession, AuthSession, ABC, Product: issue and resolve passenger session tokens.

### Community 42 - "client.py"
Cohesion: 0.24
Nodes (9): LlmResult, estimate_usd(), rate_for(), An unpriced entry would be billed at the conservative default silently., An alias points at whatever the provider currently serves, so no rate can be…, test_every_pinned_chain_model_has_a_published_rate(), test_moving_aliases_are_knowingly_billed_at_the_default(), test_unknown_model_still_prices_conservatively() (+1 more)

### Community 43 - "test_llm.py"
Cohesion: 0.15
Nodes (22): from_env(), Provider resolution, spend ceilings, and graceful degradation. Nothing here…, Anyone who pointed OPENAI_* at Gemini before this layer existed keeps working., One key covers every Gemini model, so quota on one is not quota on all., Family names mean nothing at someone else's endpoint, so none are assumed., Behind a proxy we cannot know what is listening, so send nothing extra., test_a_disabled_provider_has_no_models_to_fall_back_to(), test_a_redirected_base_url_gets_no_family_chain() (+14 more)

### Community 44 - "client_with"
Cohesion: 0.12
Nodes (27): client_with(), config(), Regression: the original renderer sent no max_tokens at all., Day totals cannot answer "what did this turn cost" once turns overlap., Gemini 2.5 charges thinking to max_tokens, which truncated live replies mid-…, Cut off mid-sentence is worse than not answering: the caller has a correct…, Records every request and answers with canned text., StubSdk (+19 more)

### Community 45 - "LlmBudget"
Cohesion: 0.14
Nodes (6): LlmBudget, Which model actually answered. The chain means it may not be the first., Every ceiling that stops a runaway bill, plus an extraction cache. A breach is…, Name the breached ceiling, or None to proceed. Records nothing — the caller…, Record a degradation the client hit rather than a ceiling, e.g. a timeout., Start metering one conversational turn, so its cost can be reported. Day totals…

### Community 46 - "LlmClient"
Cohesion: 0.14
Nodes (7): LlmClient, The chain, with cooling models moved to the back rather than dropped. Nothing…, Provider state without leaking the key. `probe` costs one cheap call., The single place this codebase talks to a model. `complete` returns None…, Tokens, cost, and degradations attributable to one turn., Built once, on first use. Disabled providers never construct one., Stop leading with a model that just refused, for a cooldown. Free-tier quota is…

### Community 47 - "evaluate_policy"
Cohesion: 0.12
Nodes (38): simulate(), ExtractedRequest, delay_entitlements(), evaluate_policy(), Independent thresholds from the data pack. Does not invent amounts for >3h meal…, _percentile(), Nearest-rank percentile over a pre-sorted list., fresh_store() (+30 more)

### Community 48 - "PassengerOnboarding"
Cohesion: 0.24
Nodes (7): BookingIntake, SignupRequest, PassengerOnboarding, ABC, Any, Product: sign up, sign in, and attach bookings. Pages never write passenger…, test_self_service_signup_and_booking()

### Community 49 - "PickySdk"
Cohesion: 0.14
Nodes (22): chained(), models_tried(), PickySdk, Serves only the models it was given a quota for; the rest raise 429. This is…, A model that returns nothing is as useless as one that errors., One timeout per model would be the whole chain's wait for the passenger., Free-tier quota lasts hours, so re-leading with it would waste the walk., Demoted, never retired: quota comes back and the preferred model resumes. (+14 more)

### Community 50 - "CredentialHasher"
Cohesion: 0.28
Nodes (5): HasherFactory, CredentialHasher, ABC, Product: hash and verify passenger passwords. Clients never pick an algorithm., Pbkdf2Hasher

### Community 51 - "ElasticsearchKnowledgeStore"
Cohesion: 0.13
Nodes (10): One retrieved policy clause. Clause-level, never a whole rule body., RuleHit, StyleHit, TurnHit, ElasticsearchKnowledgeStore, Any, Concrete product: Elasticsearch dual-write plus query-backed retrieval. Every…, Length-normalized term overlap. Dependency-free on purpose: the JSON backend… (+2 more)

### Community 52 - "knowledge/base.py"
Cohesion: 0.20
Nodes (12): load_fixtures(), load_json(), load_policies(), load_style_samples(), ScenarioFixture, ABC, _clauses(), policy_clauses() (+4 more)

### Community 53 - "Fixed"
Cohesion: 0.17
Nodes (14): LlmPolishedReplyRenderer, money_amounts(), Phrasing only. The template reply is already policy-approved, and every path…, ctx_for(), Fixed, Stands in for the policy-approved template reply., Only money is held to the digit. "6 hour" to "six-hour" is good writing., The live failure: a rewrite that silently omits the decision. (+6 more)

### Community 54 - "test_factories.py"
Cohesion: 0.22
Nodes (9): KnowledgeStoreFactory, Clients request a PassengerKnowledgeStore. They never construct JSON or…, JsonKnowledgeStore, Concrete product: in-memory passenger KB seeded from the assignment JSON pack., test_knowledge_factory_auto_never_raises_when_es_is_down(), test_knowledge_factory_json_product_is_interface_not_elasticsearch(), test_onboarding_factory_signs_in_seeded_member(), test_policy_factory_returns_handler_interface_for_each_type() (+1 more)

### Community 55 - "config.py"
Cohesion: 0.18
Nodes (12): _dedupe(), _detect_provider(), disabled_config(), _fallback_models(), _float(), _int(), Honour an explicit choice, else take the first provider holding a key., The chain behind the chosen model, from env if set and the family if not. A… (+4 more)

### Community 56 - "LlmConfig"
Cohesion: 0.18
Nodes (4): LlmConfig, Resolved provider settings plus every ceiling that bounds spend., `model` first, then every sibling worth trying if it will not answer., Enough to confirm which key loaded, never enough to use it.

### Community 57 - "PassengerSelfServiceOnboarding"
Cohesion: 0.29
Nodes (3): TravelHistory, PassengerSelfServiceOnboarding, Any

### Community 58 - ".disabled"
Cohesion: 0.33
Nodes (5): A client that can never call out, for tests and for LLM_PROVIDER=none., Belt and braces: prove the None above is not a swallowed network error., test_disabled_client_never_builds_an_sdk(), test_disabled_client_raises_if_it_ever_tried_to_call_out(), test_falling_back_cannot_be_reached_by_a_disabled_client()

## Knowledge Gaps
- **123 isolated node(s):** `factory`, `factory`, `Passenger`, `inter`, `metadata` (+118 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **9 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `PassengerKnowledgeStore` connect `PassengerKnowledgeStore` to `test_retrieval.py`, `PassengerOnboarding`, `CredentialHasher`, `ElasticsearchKnowledgeStore`, `knowledge/base.py`, `test_factories.py`, `PassengerSelfServiceOnboarding`, `.rule_ids_for_source`?**
  _High betweenness centrality (0.040) - this node is a cross-community bridge._
- **Why does `RequestType` connect `schemas.py` to `test_retrieval.py`, `main.py`, `CustomerAgentContext`, `LlmFactory`, `test_llm.py`, `client_with`, `evaluate_policy`, `PickySdk`, `Fixed`, `test_factories.py`?**
  _High betweenness centrality (0.034) - this node is a cross-community bridge._
- **Why does `SessionMemory` connect `test_retrieval.py` to `schemas.py`, `CustomerAgentContext`, `LlmFactory`, `test_llm.py`, `client_with`, `PickySdk`, `Fixed`?**
  _High betweenness centrality (0.029) - this node is a cross-community bridge._
- **Are the 9 inferred relationships involving `PassengerKnowledgeStore` (e.g. with `HasherFactory` and `Booking`) actually correct?**
  _`PassengerKnowledgeStore` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Are the 12 inferred relationships involving `StubSdk` (e.g. with `ExtractorFactory` and `LlmFactory`) actually correct?**
  _`StubSdk` has 12 INFERRED edges - model-reasoned connections that need verification._
- **Are the 14 inferred relationships involving `PolicyDecision` (e.g. with `RebookHandler` and `RefundOriginalHandler`) actually correct?**
  _`PolicyDecision` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Are the 9 inferred relationships involving `SessionMemory` (e.g. with `IntentExtractor` and `LlmExtractor`) actually correct?**
  _`SessionMemory` has 9 INFERRED edges - model-reasoned connections that need verification._
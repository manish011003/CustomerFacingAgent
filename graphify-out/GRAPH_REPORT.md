# Graph Report - Assesment_project_Custormer-Facing_Resolution_Agent_AIONOS  (2026-09-19)

## Corpus Check
- 149 files · ~57,140 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1389 nodes · 3533 edges · 75 communities (64 shown, 11 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 265 edges (avg confidence: 0.56)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `e2a193dd`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- schemas.py
- test_llm.py
- index.ts
- devDependencies
- dependencies
- compilerOptions
- compilerOptions
- .create
- TemplateReplyRenderer
- Extraction
- AeroResolve
- ElasticsearchOrJSON
- Context-First Loop
- types.ts
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
- frontend-manager/tailwind.config.ts
- frontend/next-env.d.ts
- frontend/tailwind.config.ts
- PassengerKnowledgeStore
- ops.ts
- AeroResolve — System Architecture & HLD
- CustomerAgentContext
- StyleHit
- client_with
- Customer
- ManagerDesk
- JsonKnowledgeStore
- self_service.py
- .payload
- CredentialHasher
- plan_retrieval
- SessionMemory
- Fixed
- .affected_booking
- LlmClient
- sign-in.tsx
- cards.tsx
- .operations
- handle_chat
- AuthSession
- test_retrieval.py
- store.ts
- header.tsx
- chat-shell.tsx
- .rule_ids_for_source
- ToolRuntime
- ElasticsearchKnowledgeStore
- thread.tsx
- loop.py
- test_frustration.py
- main.py
- factories/__init__.py
- _dedupe
- knowledge/base.py

## God Nodes (most connected - your core abstractions)
1. `SessionMemory` - 78 edges
2. `PassengerKnowledgeStore` - 61 edges
3. `client_with()` - 59 edges
4. `StubSdk` - 52 edges
5. `handle_chat()` - 51 edges
6. `evaluate_policy()` - 51 edges
7. `ToolRuntime` - 48 edges
8. `Customer` - 44 edges
9. `ExtractedRequest` - 41 edges
10. `PolicyDecision` - 39 edges

## Surprising Connections (you probably didn't know these)
- `Model Talks, Deterministic Code Decides` --semantically_similar_to--> `AIONOS-Style Constraint`  [INFERRED] [semantically similar]
  README.md → docs/architecture.md
- `Fail Closed on Unknown Benefits` --semantically_similar_to--> `Unknown ≠ Allowed`  [INFERRED] [semantically similar]
  docs/demo-script.md → README.md
- `FastAPI` --conceptually_related_to--> `AeroResolve`  [INFERRED]
  backend/requirements.txt → README.md
- `Meher Kaur Scenario` --conceptually_related_to--> `Meher Scenario and Manager Desk Slide`  [INFERRED]
  README.md → docs/ppt-outline.md
- `Optional OpenAI LLM Phrasing` --conceptually_related_to--> `TemplateOrOptionalLLM`  [INFERRED]
  README.md → docs/architecture.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Three Mandatory Review Scenarios** — readme_priya_nair_scenario, readme_arvind_kulkarni_scenario, readme_meher_kaur_scenario [EXTRACTED 1.00]
- **Context-First Loop Flow** — docs_architecture_customer_message, docs_architecture_retrieve_this_passenger_only, docs_architecture_extract_intent, docs_architecture_policy_engine, docs_architecture_customer_agent_context, docs_architecture_template_or_optional_llm, docs_architecture_this_turn_context_panel, docs_architecture_elasticsearch_or_json, docs_architecture_escalation_packet, docs_architecture_manager_desk [EXTRACTED 1.00]
- **Resolution Decision Outcomes** — docs_architecture_allow, docs_architecture_ask, docs_architecture_deny, docs_architecture_escalate [EXTRACTED 1.00]

## Communities (75 total, 11 thin omitted)

### Community 0 - "schemas.py"
Cohesion: 0.08
Nodes (56): _caps_lock(), _category(), _confidence(), _intents(), _punctuation_escalation(), Frustration detection: a signal, never an authority. This module owns the text…, Shouting, not acronyms. Needs enough letters to mean something., Request types this message asks for, via the existing heuristic extractor.… (+48 more)

### Community 1 - "test_llm.py"
Cohesion: 0.08
Nodes (39): LlmFactory, Clients request an LlmClient. They never read provider environment variables.…, A client that can never call out, for tests and for LLM_PROVIDER=none., _detect_provider(), disabled_config(), _float(), from_env(), _int() (+31 more)

### Community 2 - "index.ts"
Cohesion: 0.15
Nodes (25): AppFrame(), Panel(), PrimaryButton(), Stepper(), TopNav(), createDecisionChrome(), createPlatform(), DECISION_REGISTRY (+17 more)

### Community 3 - "devDependencies"
Cohesion: 0.07
Nodes (29): dependencies, next, react, react-dom, devDependencies, autoprefixer, postcss, tailwindcss (+21 more)

### Community 4 - "dependencies"
Cohesion: 0.05
Nodes (40): clsx, framer-motion, dependencies, clsx, framer-motion, lucide-react, next, react (+32 more)

### Community 5 - "compilerOptions"
Cohesion: 0.07
Nodes (26): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+18 more)

### Community 6 - "compilerOptions"
Cohesion: 0.07
Nodes (26): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+18 more)

### Community 7 - ".create"
Cohesion: 0.38
Nodes (5): test_onboarding_factory_signs_in_seeded_member(), test_the_frustration_endpoint_is_staff_gated_and_correctly_shaped(), test_the_knowledge_graph_endpoint_is_staff_gated_and_correctly_shaped(), test_seeded_passengers_can_sign_in(), test_staff_login_opens_operations_and_rejects_passengers()

### Community 8 - "TemplateReplyRenderer"
Cohesion: 0.12
Nodes (17): Facade — always goes through ReplyFactory., render_reply(), ReplyFactory, ABC, ReplyRenderer, _line(), PolicyDecision, TemplateReplyRenderer (+9 more)

### Community 9 - "Extraction"
Cohesion: 0.10
Nodes (27): detect_emotion(), detect_legal_or_formal(), The existing tone axis: angry / frustrated / confused, or nothing. Kept…, ExtractorFactory, Clients request an IntentExtractor. They never construct concrete extractors., Extraction, IntentExtractor, ABC (+19 more)

### Community 10 - "AeroResolve"
Cohesion: 0.17
Nodes (16): FastAPI, Uvicorn, Arvind Chip Demo, Drive Video Plan, 15-Minute Live Demo, Manager Desk Demo, Meher Chip Demo, Priya Chip Demo (+8 more)

### Community 11 - "ElasticsearchOrJSON"
Cohesion: 0.25
Nodes (9): elasticsearch Python Client, Elasticsearch Service, CustomerMessage, ElasticsearchOrJSON, Knowledge Base Indices, RetrieveThisPassengerOnly, Optional Elasticsearch Knowledge Base, JSON Data Pack Fallback (+1 more)

### Community 12 - "Context-First Loop"
Cohesion: 0.22
Nodes (9): Context-First Loop, Fail Closed on Unknown Benefits, Architecture Slide, Journey Compression, Limits and Tools, Passenger Forced to Become Policy Expert, UNDERSTAND GROUND DECIDE ACT ESCALATE AUDIT, Unknown ≠ Allowed (+1 more)

### Community 13 - "types.ts"
Cohesion: 0.16
Nodes (15): ApiError, OPS_URL, StaffAuthResult, State, AuthResult, Booking, ChatResponse, ContextPacket (+7 more)

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
Cohesion: 0.29
Nodes (8): pytest, AIONOS-Style Constraint, ALLOW, ASK, DENY, PolicyEngine, Model Talks, Deterministic Code Decides, Policy Engine

### Community 19 - "frontend/app/layout.tsx"
Cohesion: 0.40
Nodes (3): jakarta, metadata, viewport

### Community 27 - "PassengerKnowledgeStore"
Cohesion: 0.12
Nodes (10): PassengerKnowledgeStore, Any, Record one frustration observation as an event plus a graph edge. Deliberately…, The live passenger knowledge base, as a graph Operations can draw. Dedupes…, How distressed the traffic was, and whether distress cost containment. Low-…, Did high frustration correlate with needing a human? Keyed on the…, Aggregate the EXHIBITS_FRUSTRATION edges themselves. Read from `graph_edges`…, How much of the work needed no human, and where authority ran out. Only turns… (+2 more)

### Community 28 - "ops.ts"
Cohesion: 0.05
Nodes (64): OperationsPage(), View, CaseBoard(), CaseCard(), COLUMNS, CaseDrawer(), StatusPill(), Donut() (+56 more)

### Community 39 - "AeroResolve — System Architecture & HLD"
Cohesion: 0.05
Nodes (39): 10. HTTP API, 11. Frontends, 12. Closed codes, 13. Auth, 14. Demo contracts this architecture must preserve, 1. Product thesis, 2.1 Design split, 2.2 System context (+31 more)

### Community 42 - "CustomerAgentContext"
Cohesion: 0.27
Nodes (8): render_respond_prompt(), Extract and respond prompt contracts. Rendered from an assembled…, CustomerAgentContext, money_amounts(), normalise(), Plain ASCII spacing, so the same figure compares equal either side., A degraded turn still answers the passenger, with the policy-approved wording., test_reply_renderer_returns_the_approved_text_when_the_provider_fails()

### Community 43 - "StyleHit"
Cohesion: 0.22
Nodes (5): StyleHit, RuleHit, Length-normalized term overlap. Dependency-free on purpose: the JSON backend…, score(), tokenize()

### Community 44 - "client_with"
Cohesion: 0.06
Nodes (58): chained(), client_with(), config(), models_tried(), PickySdk, Serves only the models it was given a quota for; the rest raise 429. This is…, Regression: the original renderer sent no max_tokens at all., A model that returns nothing is as useless as one that errors. (+50 more)

### Community 45 - "Customer"
Cohesion: 0.46
Nodes (6): assemble(), _disruption(), _facts(), Booking, Customer, Booking

### Community 46 - "ManagerDesk"
Cohesion: 0.40
Nodes (5): Conversation Graph Edges, ESCALATE, EscalationPacket, ManagerDesk, Meher Scenario and Manager Desk Slide

### Community 47 - "JsonKnowledgeStore"
Cohesion: 0.23
Nodes (7): KnowledgeStoreFactory, Clients request a PassengerKnowledgeStore. They never construct JSON or…, JsonKnowledgeStore, Concrete product: in-memory passenger KB seeded from the assignment JSON pack., test_knowledge_factory_auto_never_raises_when_es_is_down(), test_knowledge_factory_json_product_is_interface_not_elasticsearch(), test_json_and_elasticsearch_cite_the_same_clauses_for_the_three_scenarios()

### Community 48 - "self_service.py"
Cohesion: 0.15
Nodes (12): BookingIntake, SignupRequest, TravelHistory, PassengerOnboarding, ABC, Any, Booking, Product: sign up, sign in, and attach bookings. Pages never write passenger… (+4 more)

### Community 50 - "CredentialHasher"
Cohesion: 0.23
Nodes (4): CredentialHasher, ABC, Product: hash and verify passenger passwords. Clients never pick an algorithm., Pbkdf2Hasher

### Community 51 - "plan_retrieval"
Cohesion: 0.22
Nodes (12): expand_scope(), plan_retrieval(), Booking, _query(), Classify the turn into the retrievers it needs, before any fetching happens., Widen the citable scope using facts only known after the booking is loaded. A…, Which retrievers this turn needs. Zia-style function classification., RetrievalPlan (+4 more)

### Community 52 - "SessionMemory"
Cohesion: 0.17
Nodes (21): packet_for_ui(), render_extract_prompt(), extract(), Facade — always goes through ExtractorFactory., load_bookings(), load_customers(), Booking, SessionMemory (+13 more)

### Community 53 - "Fixed"
Cohesion: 0.19
Nodes (16): LlmPolishedReplyRenderer, Phrasing only. The template reply is already policy-approved, and every path…, ctx_for(), Fixed, Stands in for the policy-approved template reply., Only money is held to the digit. "6 hour" to "six-hour" is good writing., The live failure: a rewrite that silently omits the decision., gpt-oss typesets "1 500" with U+202F. It is the same 1500. (+8 more)

### Community 55 - "LlmClient"
Cohesion: 0.05
Nodes (30): LlmBudget, Which model actually answered. The chain means it may not be the first., Every ceiling that stops a runaway bill, plus an extraction cache. A breach is…, Name the breached ceiling, or None to proceed. Records nothing — the caller…, Record a degradation the client hit rather than a ceiling, e.g. a timeout., Start metering one conversational turn, so its cost can be reported. Day totals…, LlmClient, LlmResult (+22 more)

### Community 56 - "sign-in.tsx"
Cohesion: 0.16
Nodes (16): BrandMark(), Wordmark(), InlineCard(), Mode, SignIn(), Button, ButtonProps, Size (+8 more)

### Community 57 - "cards.tsx"
Cohesion: 0.18
Nodes (18): AgentCards(), ChoiceCard(), ConfirmationCard(), CHOICE_STATUSES, choiceDecisions(), newActions(), repliesForTurn(), ACTION_ACTIONS (+10 more)

### Community 59 - "handle_chat"
Cohesion: 0.06
Nodes (52): get_session(), handle_chat(), _percentile(), Nearest-rank percentile over a pre-sorted list., fresh_store(), measured_turn(), Containment: the metric that answers how much work needed no human. Two layers…, test_a_store_with_no_measured_turns_reports_zero_not_a_fake_rate() (+44 more)

### Community 60 - "AuthSession"
Cohesion: 0.19
Nodes (4): InMemoryTokenSession, AuthSession, ABC, Product: issue and resolve passenger session tokens.

### Community 61 - "test_retrieval.py"
Cohesion: 0.10
Nodes (22): context_contains_forbidden(), narrate(), Render the decided packet as prose with clause-level citations. Every line is…, Code-side gate: other passengers, raw policy bodies, and history-as-benefit., TurnHit, _FakeEs, _FakeIndices, Build one turn's plan, evaluation, retrieval, and context outside the API. (+14 more)

### Community 62 - "store.ts"
Cohesion: 0.31
Nodes (12): LoginPage(), ResolvePage(), useReady(), greeting(), messageFor(), newSessionId(), openConversation(), Persisted (+4 more)

### Community 63 - "header.tsx"
Cohesion: 0.22
Nodes (10): BookingCard(), ContextPanel(), DecisionRow(), toneFor(), ChatHeader(), Badge(), Tone, TONES (+2 more)

### Community 64 - "chat-shell.tsx"
Cohesion: 0.29
Nodes (7): ChatShell(), Composer(), QuickReplies(), api, starterReplies(), refreshTrip(), QuickReply

### Community 67 - "ToolRuntime"
Cohesion: 0.06
Nodes (36): _assistant_tools(), _history(), _invented_money(), LLM-as-orchestrator loop. The model decides which tools to call. Tools enforce…, run_llm_agent(), _system_for(), _accepted(), _decision_payload() (+28 more)

### Community 68 - "ElasticsearchKnowledgeStore"
Cohesion: 0.12
Nodes (8): KnownFact, One retrieved policy clause. Clause-level, never a whole rule body., RuleHit, ElasticsearchKnowledgeStore, Any, RuleHit, Concrete product: Elasticsearch dual-write plus query-backed retrieval. Every…, Passenger lookup is a filtered query, not a scan of `self.passengers`.

### Community 69 - "thread.tsx"
Cohesion: 0.53
Nodes (4): Thread(), TypingIndicator(), previousExecuted(), formatTime()

### Community 71 - "loop.py"
Cohesion: 0.18
Nodes (24): _case_status(), _deterministic_turn(), _finish(), _frustration_trace(), _identify(), _issue_label(), One trace line, identical on both agent paths, so a reviewer can see the signal…, Same edges on both agent paths, so Operations can draw the live KB. (+16 more)

### Community 73 - "test_frustration.py"
Cohesion: 0.05
Nodes (77): classify(), is_low_confidence(), Assess one turn. Deterministic, offline, and safe to call every turn., Both gates, or neither. A hostile guess is not a reason to fetch a human., Below the store threshold the observation is logged but not aggregated., should_escalate(), ExtractedRequest, delay_entitlements() (+69 more)

### Community 74 - "main.py"
Cohesion: 0.11
Nodes (38): reset_session(), add_my_booking(), analytics(), assess(), case(), cases(), chat(), containment() (+30 more)

### Community 75 - "factories/__init__.py"
Cohesion: 0.18
Nodes (10): AuthFactory, Session tokens are a singleton product so login survives across requests., HasherFactory, OnboardingFactory, Staff sessions stay in process so operations login survives across requests., StaffFactory, _digest(), Any (+2 more)

### Community 79 - "_dedupe"
Cohesion: 0.33
Nodes (5): _dedupe(), _fallback_models(), `model` first, then every sibling worth trying if it will not answer., The chain behind the chosen model, from env if set and the family if not. A…, Order-preserving, so the head stays the model the operator asked for.

### Community 80 - "knowledge/base.py"
Cohesion: 0.16
Nodes (15): load_fixtures(), load_json(), load_policies(), load_style_samples(), ScenarioFixture, _category_counts(), ABC, Counts in severity order, and only for categories actually observed. Fixed key… (+7 more)

## Knowledge Gaps
- **184 isolated node(s):** `inter`, `metadata`, `View`, `COLUMNS`, `Series` (+179 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **11 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `PassengerKnowledgeStore` connect `PassengerKnowledgeStore` to `schemas.py`, `.rule_ids_for_source`, `ElasticsearchKnowledgeStore`, `loop.py`, `factories/__init__.py`, `StyleHit`, `Customer`, `JsonKnowledgeStore`, `knowledge/base.py`, `self_service.py`, `CredentialHasher`, `SessionMemory`, `.affected_booking`, `.operations`, `test_retrieval.py`?**
  _High betweenness centrality (0.066) - this node is a cross-community bridge._
- **Why does `SessionMemory` connect `SessionMemory` to `schemas.py`, `test_llm.py`, `ToolRuntime`, `loop.py`, `test_frustration.py`, `Extraction`, `CustomerAgentContext`, `client_with`, `Customer`, `plan_retrieval`, `Fixed`, `handle_chat`, `test_retrieval.py`?**
  _High betweenness centrality (0.044) - this node is a cross-community bridge._
- **Why does `LlmClient` connect `LlmClient` to `test_llm.py`, `ToolRuntime`, `TemplateReplyRenderer`, `Extraction`, `CustomerAgentContext`, `client_with`, `Fixed`, `handle_chat`?**
  _High betweenness centrality (0.034) - this node is a cross-community bridge._
- **Are the 11 inferred relationships involving `SessionMemory` (e.g. with `ToolRuntime` and `IntentExtractor`) actually correct?**
  _`SessionMemory` has 11 INFERRED edges - model-reasoned connections that need verification._
- **Are the 11 inferred relationships involving `PassengerKnowledgeStore` (e.g. with `HasherFactory` and `Booking`) actually correct?**
  _`PassengerKnowledgeStore` has 11 INFERRED edges - model-reasoned connections that need verification._
- **Are the 14 inferred relationships involving `StubSdk` (e.g. with `ExtractorFactory` and `LlmFactory`) actually correct?**
  _`StubSdk` has 14 INFERRED edges - model-reasoned connections that need verification._
- **What connects `inter`, `metadata`, `View` to the rest of the system?**
  _184 weakly-connected nodes found - possible documentation gaps or missing edges._
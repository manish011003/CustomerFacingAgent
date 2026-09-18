# Graph Report - Assesment_project_Custormer-Facing_Resolution_Agent_AIONOS  (2026-09-19)

## Corpus Check
- 171 files · ~69,047 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1568 nodes · 4077 edges · 74 communities (67 shown, 7 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 278 edges (avg confidence: 0.55)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `e6fb6b8f`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- schemas.py
- client_with
- index.ts
- devDependencies
- dependencies
- compilerOptions
- compilerOptions
- frustration.py
- self_service.py
- HeuristicExtractor
- 15-Minute Live Demo
- ElasticsearchOrJSON
- Policy Engine
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
- CredentialHasher
- evaluate_policy
- AeroResolve
- IntentExtractor
- closure.py
- LlmFactory
- test_frustration.py
- inventory.py
- SessionMemory
- AuthSession
- test_context.py
- CustomerAgentContext
- test_retrieval.py
- LlmClient
- sign-in.tsx
- cards.tsx
- handle_chat
- exit-board.tsx
- store.ts
- StubSdk
- context-panel.tsx
- ToolRuntime
- ElasticsearchKnowledgeStore
- .create
- should_escalate
- .create
- test_llm.py
- main.py
- knowledge/base.py
- factories/__init__.py
- chat-shell.tsx
- web.py

## God Nodes (most connected - your core abstractions)
1. `SessionMemory` - 102 edges
2. `handle_chat()` - 72 edges
3. `PassengerKnowledgeStore` - 70 edges
4. `client_with()` - 59 edges
5. `evaluate_policy()` - 53 edges
6. `StubSdk` - 52 edges
7. `ToolRuntime` - 50 edges
8. `Customer` - 48 edges
9. `ExtractedRequest` - 45 edges
10. `PolicyDecision` - 42 edges

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

## Communities (74 total, 7 thin omitted)

### Community 0 - "schemas.py"
Cohesion: 0.05
Nodes (91): assemble(), _disruption(), _facts(), Booking, _case_status(), _deterministic_turn(), _finish(), _frustration_trace() (+83 more)

### Community 1 - "client_with"
Cohesion: 0.11
Nodes (37): chained(), client_with(), config(), models_tried(), PickySdk, Serves only the models it was given a quota for; the rest raise 429. This is…, A model that returns nothing is as useless as one that errors., One timeout per model would be the whole chain's wait for the passenger. (+29 more)

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

### Community 7 - "frustration.py"
Cohesion: 0.13
Nodes (17): _caps_lock(), _category(), _confidence(), detect_emotion(), detect_legal_or_formal(), _intents(), is_low_confidence(), _punctuation_escalation() (+9 more)

### Community 8 - "self_service.py"
Cohesion: 0.15
Nodes (12): BookingIntake, SignupRequest, TravelHistory, PassengerOnboarding, ABC, Any, Booking, Product: sign up, sign in, and attach bookings. Pages never write passenger… (+4 more)

### Community 9 - "HeuristicExtractor"
Cohesion: 0.16
Nodes (22): reset_session(), classify(), _is_assist_follow_up(), persist_assist(), Classify turns that are not disruption entitlements. Disruption money still…, request_for(), slots_from(), IssueFamily (+14 more)

### Community 10 - "15-Minute Live Demo"
Cohesion: 0.19
Nodes (14): ManagerDesk, Arvind Chip Demo, Drive Video Plan, 15-Minute Live Demo, Manager Desk Demo, Meher Chip Demo, Priya Chip Demo, Arvind Scenario Slide (+6 more)

### Community 11 - "ElasticsearchOrJSON"
Cohesion: 0.22
Nodes (10): elasticsearch Python Client, Elasticsearch Service, Conversation Graph Edges, CustomerMessage, ElasticsearchOrJSON, Knowledge Base Indices, RetrieveThisPassengerOnly, Optional Elasticsearch Knowledge Base (+2 more)

### Community 12 - "Policy Engine"
Cohesion: 0.22
Nodes (9): pytest, Fail Closed on Unknown Benefits, Journey Compression, Limits and Tools, Passenger Forced to Become Policy Expert, UNDERSTAND GROUND DECIDE ACT ESCALATE AUDIT, Unknown ≠ Allowed, Policy Engine (+1 more)

### Community 13 - "types.ts"
Cohesion: 0.15
Nodes (13): api, ApiError, OPS_URL, StaffAuthResult, AuthResult, ChatMessage, ChatResponse, Conversation (+5 more)

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

### Community 19 - "frontend/app/layout.tsx"
Cohesion: 0.40
Nodes (3): jakarta, metadata, viewport

### Community 27 - "PassengerKnowledgeStore"
Cohesion: 0.06
Nodes (25): KnownFact, _category_counts(), PassengerKnowledgeStore, Any, Booking, RuleHit, Optional durable delete. JSON product is in-memory only., Map a PolicyDecision.source label back onto indexed rule ids. (+17 more)

### Community 28 - "ops.ts"
Cohesion: 0.05
Nodes (64): OperationsPage(), View, CaseBoard(), CaseCard(), COLUMNS, CaseDrawer(), StatusPill(), Donut() (+56 more)

### Community 39 - "AeroResolve — System Architecture & HLD"
Cohesion: 0.05
Nodes (40): 10. HTTP API, 11. Frontends, 12. Closed codes, 13. Auth, 14. Demo contracts this architecture must preserve, 1. Product thesis, 2.1 Design split, 2.2 System context (+32 more)

### Community 42 - "CredentialHasher"
Cohesion: 0.25
Nodes (5): HasherFactory, CredentialHasher, ABC, Product: hash and verify passenger passwords. Clients never pick an algorithm., Pbkdf2Hasher

### Community 43 - "evaluate_policy"
Cohesion: 0.12
Nodes (35): ExtractedRequest, delay_entitlements(), evaluate_policy(), PolicyDecision, Independent thresholds from the data pack. Does not invent amounts for >3h meal…, parametrize, Allowed and denied outcomes must not carry an escalation cause., Guards new handlers: an ESCALATE with no code would vanish from the breakdown. (+27 more)

### Community 44 - "AeroResolve"
Cohesion: 0.29
Nodes (8): FastAPI, Uvicorn, AIONOS-Style Constraint, Context-First Loop, Architecture Slide, AeroResolve, Model Talks, Deterministic Code Decides, Product Thesis

### Community 45 - "IntentExtractor"
Cohesion: 0.40
Nodes (3): IntentExtractor, ABC, Product: turn a customer utterance into structured extraction. Never decides…

### Community 46 - "closure.py"
Cohesion: 0.13
Nodes (23): already_asked_feedback(), case_status(), confirms_resolution(), is_greeting(), last_assistant_text(), offered_supervisor(), parse_feedback(), Any (+15 more)

### Community 47 - "LlmFactory"
Cohesion: 0.08
Nodes (28): ExtractorFactory, Clients request an IntentExtractor. They never construct concrete extractors., LlmFactory, Clients request an LlmClient. They never read provider environment variables.…, LlmExtractor, Optional NLU. Both the fallback extractor and the client are injected., isolate_passenger_chats(), no_live_postgres() (+20 more)

### Community 48 - "test_frustration.py"
Cohesion: 0.17
Nodes (22): fresh_store(), observation(), Frustration is a signal, and these tests are what keep it one. Layered the same…, Operations draws the same graph_edges store, not a side table., Absent from handlers(), so the model cannot self-serve a reason code., The same assertion `test_emotion.py` makes about tone, for the classifier., test_a_confident_observation_is_stored_and_aggregated(), test_a_low_confidence_observation_is_logged_but_excluded_from_primary_counts() (+14 more)

### Community 49 - "inventory.py"
Cohesion: 0.20
Nodes (20): load_scheduled_flights(), Look-only departure shown during booking assist. Never a ticket., SuggestedFlight, _as_suggested(), _date_matches(), _href(), _norm(), Any (+12 more)

### Community 50 - "SessionMemory"
Cohesion: 0.11
Nodes (25): classify(), Assess one turn. Deterministic, offline, and safe to call every turn., SessionMemory, No sampling, no clock, no model. CI must not need a retry., A stranded passenger with a child is a care case, not an angry one., Repetition means the previous answer did not land, whatever words were used., One regex, so the escalation rule and the signal cannot disagree., It must not borrow another reason's code to get a supervisor. (+17 more)

### Community 51 - "AuthSession"
Cohesion: 0.09
Nodes (16): AuthFactory, Session tokens are a singleton product so login survives across requests., connect(), database_url(), Any, Thread-local psycopg connection. Schema is applied once per connection., InMemoryTokenSession, PostgresTokenSession (+8 more)

### Community 52 - "test_context.py"
Cohesion: 0.13
Nodes (26): packet_for_ui(), render_respond_prompt(), extract(), Facade — always goes through ExtractorFactory., plan_retrieval(), Classify the turn into the retrievers it needs, before any fetching happens., Extract and respond prompt contracts. Rendered from an assembled…, load_bookings() (+18 more)

### Community 53 - "CustomerAgentContext"
Cohesion: 0.15
Nodes (19): Facade — always goes through ReplyFactory., render_reply(), missing_slots(), parse_notes(), Any, ReplyFactory, CustomerAgentContext, ABC (+11 more)

### Community 54 - "test_retrieval.py"
Cohesion: 0.13
Nodes (25): context_contains_forbidden(), narrate(), Render the decided packet as prose with clause-level citations. Every line is…, Code-side gate: other passengers, raw policy bodies, and history-as-benefit., render_extract_prompt(), TurnHit, test_extract_prompt_is_narrow_and_has_no_policy_schema(), Build one turn's plan, evaluation, retrieval, and context outside the API. (+17 more)

### Community 55 - "LlmClient"
Cohesion: 0.05
Nodes (37): LlmBudget, Which model actually answered. The chain means it may not be the first., Every ceiling that stops a runaway bill, plus an extraction cache. A breach is…, Name the breached ceiling, or None to proceed. Records nothing — the caller…, Record a degradation the client hit rather than a ceiling, e.g. a timeout., Start metering one conversational turn, so its cost can be reported. Day totals…, LlmClient, LlmResult (+29 more)

### Community 56 - "sign-in.tsx"
Cohesion: 0.18
Nodes (14): BrandMark(), Wordmark(), InlineCard(), Thread(), TypingIndicator(), Mode, SignIn(), Field() (+6 more)

### Community 57 - "cards.tsx"
Cohesion: 0.17
Nodes (19): AgentCards(), ChoiceCard(), ConfirmationCard(), CHOICE_STATUSES, choiceDecisions(), newActions(), repliesForTurn(), ACTION_ACTIONS (+11 more)

### Community 58 - "handle_chat"
Cohesion: 0.07
Nodes (51): conversation_for(), get_session(), handle_chat(), Structured 1–5 rating from the chat UI. Same close rules as a spoken rating., _remember(), _stored_session(), submit_feedback(), _percentile() (+43 more)

### Community 61 - "exit-board.tsx"
Cohesion: 0.20
Nodes (9): metadata, BookingCard(), SuggestedFlightCard(), clockLabel(), ExitBoard(), FALLBACK_FLIGHTS, flightStatusCopy(), humanise() (+1 more)

### Community 62 - "store.ts"
Cohesion: 0.24
Nodes (16): LoginPage(), ResolvePage(), useReady(), greeting(), messageFor(), newSessionId(), openConversation(), Persisted (+8 more)

### Community 63 - "StubSdk"
Cohesion: 0.07
Nodes (35): LlmPolishedReplyRenderer, Phrasing only. The template reply is already policy-approved, and every path…, ctx_for(), Fixed, Stands in for the policy-approved template reply., Regression: the original renderer sent no max_tokens at all., Day totals cannot answer "what did this turn cost" once turns overlap., Gemini 2.5 charges thinking to max_tokens, which truncated live replies mid-… (+27 more)

### Community 64 - "context-panel.tsx"
Cohesion: 0.32
Nodes (6): ContextPanel(), DecisionRow(), toneFor(), Badge(), Tone, TONES

### Community 67 - "ToolRuntime"
Cohesion: 0.08
Nodes (26): _assistant_tools(), _history(), _invented_money(), LLM-as-orchestrator loop. The model decides which tools to call. Tools enforce…, run_llm_agent(), _system_for(), _accepted(), _decision_payload() (+18 more)

### Community 68 - "ElasticsearchKnowledgeStore"
Cohesion: 0.06
Nodes (20): KnowledgeStoreFactory, Clients request a PassengerKnowledgeStore. They never construct JSON, Postgres,…, One retrieved policy clause. Clause-level, never a whole rule body., RuleHit, StyleHit, ElasticsearchKnowledgeStore, Any, RuleHit (+12 more)

### Community 69 - ".create"
Cohesion: 0.18
Nodes (16): test_key_is_never_exposed_by_health(), main(), Run the three assignment scenarios and print a transcript with measurements. cd…, show_turn(), summarise(), main(), Ask the configured provider which models your key can actually serve. cd…, heading() (+8 more)

### Community 70 - "should_escalate"
Cohesion: 0.38
Nodes (7): Both gates, or neither. A hostile guess is not a reason to fetch a human., should_escalate(), parametrize, A confident read of mild annoyance is not a reason to fetch a human., test_escalation_does_not_fire_below_the_category_threshold(), test_escalation_does_not_fire_below_the_confidence_threshold(), test_escalation_fires_above_both_thresholds()

### Community 72 - ".create"
Cohesion: 0.32
Nodes (6): signup(), test_onboarding_factory_signs_in_seeded_member(), test_the_frustration_endpoint_is_staff_gated_and_correctly_shaped(), test_the_knowledge_graph_endpoint_is_staff_gated_and_correctly_shaped(), test_seeded_passengers_can_sign_in(), test_staff_login_opens_operations_and_rejects_passengers()

### Community 73 - "test_llm.py"
Cohesion: 0.08
Nodes (39): A client that can never call out, for tests and for LLM_PROVIDER=none., from_env(), estimate_usd(), rate_for(), needs_model(), True only when the regex extractor understood nothing. Measured on a live…, Provider resolution, spend ceilings, and graceful degradation. Nothing here…, Anyone who pointed OPENAI_* at Gemini before this layer existed keeps working. (+31 more)

### Community 74 - "main.py"
Cohesion: 0.11
Nodes (39): add_my_booking(), analytics(), assess(), case(), cases(), chat(), containment(), _eligibility() (+31 more)

### Community 78 - "knowledge/base.py"
Cohesion: 0.17
Nodes (15): load_fixtures(), load_help(), load_json(), load_policies(), load_style_samples(), ScenarioFixture, ABC, _seconds_between() (+7 more)

### Community 79 - "factories/__init__.py"
Cohesion: 0.21
Nodes (7): OnboardingFactory, Staff sessions stay in process so operations login survives across requests., StaffFactory, _digest(), Any, Operations sign-in is a separate product from passenger accounts., StaffAccess

### Community 81 - "chat-shell.tsx"
Cohesion: 0.14
Nodes (17): ChatShell(), Composer(), FeedbackPopup(), ChatHeader(), QuickReplies(), Button, ButtonProps, Size (+9 more)

### Community 84 - "web.py"
Cohesion: 0.67
Nodes (3): mount_ui(), Serve the exported Next.js apps from the same origin as the API. Local `uvicorn…, FastAPI

## Knowledge Gaps
- **189 isolated node(s):** `inter`, `metadata`, `View`, `COLUMNS`, `Series` (+184 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **7 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `PassengerKnowledgeStore` connect `PassengerKnowledgeStore` to `schemas.py`, `ElasticsearchKnowledgeStore`, `self_service.py`, `CredentialHasher`, `knowledge/base.py`, `AuthSession`, `test_context.py`, `test_retrieval.py`?**
  _High betweenness centrality (0.055) - this node is a cross-community bridge._
- **Why does `handle_chat()` connect `handle_chat` to `schemas.py`, `ToolRuntime`, `.create`, `.create`, `HeuristicExtractor`, `main.py`, `LlmFactory`, `test_frustration.py`, `test_context.py`, `CustomerAgentContext`, `test_retrieval.py`?**
  _High betweenness centrality (0.047) - this node is a cross-community bridge._
- **Why does `SessionMemory` connect `SessionMemory` to `schemas.py`, `client_with`, `ToolRuntime`, `ElasticsearchKnowledgeStore`, `frustration.py`, `HeuristicExtractor`, `test_llm.py`, `IntentExtractor`, `closure.py`, `LlmFactory`, `test_frustration.py`, `test_context.py`, `CustomerAgentContext`, `test_retrieval.py`, `handle_chat`, `StubSdk`?**
  _High betweenness centrality (0.044) - this node is a cross-community bridge._
- **Are the 11 inferred relationships involving `SessionMemory` (e.g. with `ToolRuntime` and `IntentExtractor`) actually correct?**
  _`SessionMemory` has 11 INFERRED edges - model-reasoned connections that need verification._
- **Are the 11 inferred relationships involving `PassengerKnowledgeStore` (e.g. with `HasherFactory` and `Booking`) actually correct?**
  _`PassengerKnowledgeStore` has 11 INFERRED edges - model-reasoned connections that need verification._
- **What connects `inter`, `metadata`, `View` to the rest of the system?**
  _189 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `schemas.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05420267085624509 - nodes in this community are weakly interconnected._
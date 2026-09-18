# Graph Report - Assesment_project_Custormer-Facing_Resolution_Agent_AIONOS  (2026-09-19)

## Corpus Check
- 171 files · ~67,046 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1552 nodes · 4005 edges · 78 communities (70 shown, 8 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 279 edges (avg confidence: 0.55)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `23997091`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- PolicyDecision
- client_with
- index.ts
- devDependencies
- dependencies
- compilerOptions
- compilerOptions
- frustration.py
- self_service.py
- Extraction
- AeroResolve
- Optional Elasticsearch Knowledge Base
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
- factories/__init__.py
- evaluate_policy
- PickySdk
- test_factories.py
- loop.py
- LlmExtractor
- test_frustration.py
- inventory.py
- closure.py
- AuthSession
- SessionMemory
- Fixed
- baseline_for_booking
- LlmClient
- sign-in.tsx
- cards.tsx
- handle_chat
- test_containment.py
- connect
- exit-board.tsx
- useConversation
- header.tsx
- chat-shell.tsx
- conftest.py
- tools.py
- ToolRuntime
- schemas.py
- LlmFactory
- _dedupe
- reset_session
- thread.tsx
- test_llm.py
- main.py
- .payload
- store.py
- ElasticsearchOrJSON

## God Nodes (most connected - your core abstractions)
1. `SessionMemory` - 96 edges
2. `PassengerKnowledgeStore` - 70 edges
3. `handle_chat()` - 67 edges
4. `client_with()` - 59 edges
5. `evaluate_policy()` - 53 edges
6. `StubSdk` - 52 edges
7. `ToolRuntime` - 50 edges
8. `Customer` - 48 edges
9. `ExtractedRequest` - 45 edges
10. `PolicyDecision` - 44 edges

## Surprising Connections (you probably didn't know these)
- `Model Talks, Deterministic Code Decides` --semantically_similar_to--> `AIONOS-Style Constraint`  [INFERRED] [semantically similar]
  README.md → docs/architecture.md
- `Fail Closed on Unknown Benefits` --semantically_similar_to--> `Unknown ≠ Allowed`  [INFERRED] [semantically similar]
  docs/demo-script.md → README.md
- `FastAPI` --conceptually_related_to--> `AeroResolve`  [INFERRED]
  backend/requirements.txt → README.md
- `Meher Kaur Scenario` --conceptually_related_to--> `Meher Scenario and Manager Desk Slide`  [INFERRED]
  README.md → docs/ppt-outline.md
- `JSON Data Pack Fallback` --shares_data_with--> `ElasticsearchOrJSON`  [INFERRED]
  README.md → docs/architecture.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Three Mandatory Review Scenarios** — readme_priya_nair_scenario, readme_arvind_kulkarni_scenario, readme_meher_kaur_scenario [EXTRACTED 1.00]
- **Context-First Loop Flow** — docs_architecture_customer_message, docs_architecture_retrieve_this_passenger_only, docs_architecture_extract_intent, docs_architecture_policy_engine, docs_architecture_customer_agent_context, docs_architecture_template_or_optional_llm, docs_architecture_this_turn_context_panel, docs_architecture_elasticsearch_or_json, docs_architecture_escalation_packet, docs_architecture_manager_desk [EXTRACTED 1.00]
- **Resolution Decision Outcomes** — docs_architecture_allow, docs_architecture_ask, docs_architecture_deny, docs_architecture_escalate [EXTRACTED 1.00]

## Communities (78 total, 8 thin omitted)

### Community 0 - "PolicyDecision"
Cohesion: 0.11
Nodes (40): missing_slots(), parse_notes(), Any, PolicyHandlerFactory, Maps a request type to a PolicyHandler. Engine never constructs handlers itself., DecisionStatus, EscalationReason, PolicyDecision (+32 more)

### Community 1 - "client_with"
Cohesion: 0.08
Nodes (39): _args(), LLM agent loop: the model orchestrates, tools enforce policy., Returns a sequence of chat.completions payloads, including tool calls., ScriptedSdk, test_agent_calls_booking_then_policy_then_answers(), test_agent_chat_sends_tools_to_the_model(), test_execute_hotel_is_blocked_when_policy_denies(), test_fare_waiver_above_limit_escalates_and_cannot_be_executed() (+31 more)

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
Cohesion: 0.07
Nodes (40): _caps_lock(), _category(), classify(), _confidence(), detect_legal_or_formal(), _intents(), is_low_confidence(), _punctuation_escalation() (+32 more)

### Community 8 - "self_service.py"
Cohesion: 0.15
Nodes (12): BookingIntake, SignupRequest, TravelHistory, PassengerOnboarding, ABC, Any, Booking, Product: sign up, sign in, and attach bookings. Pages never write passenger… (+4 more)

### Community 9 - "Extraction"
Cohesion: 0.13
Nodes (24): detect_emotion(), The existing tone axis: angry / frustrated / confused, or nothing. Kept…, _query(), classify(), persist_assist(), Classify turns that are not disruption entitlements. Disruption money still…, request_for(), slots_from() (+16 more)

### Community 10 - "AeroResolve"
Cohesion: 0.17
Nodes (16): FastAPI, Uvicorn, Arvind Chip Demo, Drive Video Plan, 15-Minute Live Demo, Manager Desk Demo, Meher Chip Demo, Priya Chip Demo (+8 more)

### Community 11 - "Optional Elasticsearch Knowledge Base"
Cohesion: 0.50
Nodes (5): elasticsearch Python Client, Elasticsearch Service, Optional Elasticsearch Knowledge Base, JSON Data Pack Fallback, Knowledge Base Store

### Community 12 - "Context-First Loop"
Cohesion: 0.22
Nodes (9): Context-First Loop, Fail Closed on Unknown Benefits, Architecture Slide, Journey Compression, Limits and Tools, Passenger Forced to Become Policy Expert, UNDERSTAND GROUND DECIDE ACT ESCALATE AUDIT, Unknown ≠ Allowed (+1 more)

### Community 13 - "types.ts"
Cohesion: 0.14
Nodes (21): api, ApiError, OPS_URL, StaffAuthResult, Persisted, State, AuthResult, Booking (+13 more)

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
Cohesion: 0.05
Nodes (26): _category_counts(), PassengerKnowledgeStore, ABC, Any, Booking, RuleHit, Optional durable delete. JSON product is in-memory only., Map a PolicyDecision.source label back onto indexed rule ids. (+18 more)

### Community 28 - "ops.ts"
Cohesion: 0.05
Nodes (64): OperationsPage(), View, CaseBoard(), CaseCard(), COLUMNS, CaseDrawer(), StatusPill(), Donut() (+56 more)

### Community 39 - "AeroResolve — System Architecture & HLD"
Cohesion: 0.05
Nodes (39): 10. HTTP API, 11. Frontends, 12. Closed codes, 13. Auth, 14. Demo contracts this architecture must preserve, 1. Product thesis, 2.1 Design split, 2.2 System context (+31 more)

### Community 42 - "factories/__init__.py"
Cohesion: 0.20
Nodes (8): AuthFactory, Session tokens are a singleton product so login survives across requests., HasherFactory, OnboardingFactory, CredentialHasher, ABC, Product: hash and verify passenger passwords. Clients never pick an algorithm., Pbkdf2Hasher

### Community 43 - "evaluate_policy"
Cohesion: 0.14
Nodes (30): ExtractedRequest, evaluate_policy(), Booking, parametrize, Allowed and denied outcomes must not carry an escalation cause., Guards new handlers: an ESCALATE with no code would vanish from the breakdown., test_a_reason_code_never_appears_without_an_escalation(), test_each_authority_boundary_maps_to_its_own_reason() (+22 more)

### Community 44 - "PickySdk"
Cohesion: 0.10
Nodes (28): chained(), models_tried(), PickySdk, Serves only the models it was given a quota for; the rest raise 429. This is…, A model that returns nothing is as useless as one that errors., One timeout per model would be the whole chain's wait for the passenger., Free-tier quota lasts hours, so re-leading with it would waste the walk., Demoted, never retired: quota comes back and the preferred model resumes. (+20 more)

### Community 45 - "test_factories.py"
Cohesion: 0.13
Nodes (10): KnowledgeStoreFactory, Clients request a PassengerKnowledgeStore. They never construct JSON, Postgres,…, JsonKnowledgeStore, Concrete product: in-memory passenger KB seeded from the assignment JSON pack., test_knowledge_factory_auto_never_raises_when_es_is_down(), test_knowledge_factory_json_product_is_interface_not_elasticsearch(), test_knowledge_factory_postgres_requires_database_url(), test_register_passenger_persists_the_account_row() (+2 more)

### Community 46 - "loop.py"
Cohesion: 0.18
Nodes (23): _case_status(), _deterministic_turn(), _finish(), _frustration_trace(), _identify(), _issue_label(), One trace line, identical on both agent paths, so a reviewer can see the signal…, Per-turn measurements, recorded on the turn event so analytics can aggregate.… (+15 more)

### Community 47 - "LlmExtractor"
Cohesion: 0.14
Nodes (15): ExtractorFactory, Clients request an IntentExtractor. They never construct concrete extractors., LlmExtractor, Optional NLU. Both the fallback extractor and the client are injected., test_extractor_factory_returns_product_interface(), ExplodingSdk, Measured live: the regex reads this in 4ms, the model takes 2-5 seconds., test_a_readable_utterance_never_reaches_the_model() (+7 more)

### Community 48 - "test_frustration.py"
Cohesion: 0.12
Nodes (28): fresh_store(), observation(), Frustration is a signal, and these tests are what keep it one. Layered the same…, Operations draws the same graph_edges store, not a side table., It must not borrow another reason's code to get a supervisor., Absent from handlers(), so the model cannot self-serve a reason code., The model chooses when to look, never what it sees., Otherwise a chatty model would inflate every frustration bucket. (+20 more)

### Community 49 - "inventory.py"
Cohesion: 0.23
Nodes (18): load_scheduled_flights(), Look-only departure shown during booking assist. Never a ticket., SuggestedFlight, _as_suggested(), _date_matches(), _href(), _norm(), Any (+10 more)

### Community 50 - "closure.py"
Cohesion: 0.16
Nodes (18): already_asked_feedback(), case_status(), confirms_resolution(), last_assistant_text(), offered_supervisor(), parse_feedback(), Any, When a passenger conversation is still open, handed over, or actually closed.… (+10 more)

### Community 51 - "AuthSession"
Cohesion: 0.18
Nodes (4): InMemoryTokenSession, AuthSession, ABC, Product: issue and resolve passenger session tokens.

### Community 52 - "SessionMemory"
Cohesion: 0.07
Nodes (66): assemble(), context_contains_forbidden(), _disruption(), _facts(), narrate(), packet_for_ui(), Booking, Render the decided packet as prose with clause-level citations. Every line is… (+58 more)

### Community 53 - "Fixed"
Cohesion: 0.10
Nodes (31): Facade — always goes through ReplyFactory., render_reply(), ReplyFactory, CustomerAgentContext, ABC, ReplyRenderer, LlmPolishedReplyRenderer, money_amounts() (+23 more)

### Community 54 - "baseline_for_booking"
Cohesion: 0.16
Nodes (13): _baseline(), baseline_for_booking(), delay_entitlements(), Booking, PolicyDecision, Independent thresholds from the data pack. Does not invent amounts for >3h meal…, Entitlements this disruption carries before the passenger asks anything.…, offered_actions() (+5 more)

### Community 55 - "LlmClient"
Cohesion: 0.06
Nodes (31): LlmBudget, Which model actually answered. The chain means it may not be the first., Every ceiling that stops a runaway bill, plus an extraction cache. A breach is…, Name the breached ceiling, or None to proceed. Records nothing — the caller…, Record a degradation the client hit rather than a ceiling, e.g. a timeout., Start metering one conversational turn, so its cost can be reported. Day totals…, LlmClient, LlmResult (+23 more)

### Community 56 - "sign-in.tsx"
Cohesion: 0.16
Nodes (16): BrandMark(), Wordmark(), InlineCard(), Mode, SignIn(), Button, ButtonProps, Size (+8 more)

### Community 57 - "cards.tsx"
Cohesion: 0.17
Nodes (20): AgentCards(), BookingCard(), ChoiceCard(), ConfirmationCard(), CHOICE_STATUSES, choiceDecisions(), newActions(), repliesForTurn() (+12 more)

### Community 58 - "handle_chat"
Cohesion: 0.15
Nodes (22): handle_chat(), Structured 1–5 rating from the chat UI. Same close rules as a spoken rating., submit_feedback(), test_no_key_is_honest_fallback_not_a_live_llm(), _case(), test_card_feedback_endpoint_closes_when_rating_is_good(), test_escalation_survives_later_turns_that_used_to_look_resolved(), test_good_feedback_cannot_un_escalate() (+14 more)

### Community 59 - "test_containment.py"
Cohesion: 0.15
Nodes (21): _percentile(), Nearest-rank percentile over a pre-sorted list., fresh_store(), measured_turn(), Containment: the metric that answers how much work needed no human. Two layers…, test_a_store_with_no_measured_turns_reports_zero_not_a_fake_rate(), test_a_waiver_above_the_limit_reports_itself_as_escalated(), test_an_entitlement_turn_is_contained_and_fully_cited() (+13 more)

### Community 60 - "connect"
Cohesion: 0.12
Nodes (11): connect(), database_url(), Any, Thread-local psycopg connection. Schema is applied once per connection., PostgresTokenSession, Passenger login tokens survive a process restart when Postgres is up., _json(), PostgresKnowledgeStore (+3 more)

### Community 61 - "exit-board.tsx"
Cohesion: 0.21
Nodes (7): metadata, SuggestedFlightCard(), clockLabel(), ExitBoard(), STATUS_TONE, FALLBACK_FLIGHTS, SuggestedFlight

### Community 62 - "useConversation"
Cohesion: 0.31
Nodes (10): LoginPage(), ResolvePage(), useReady(), greeting(), messageFor(), newSessionId(), openConversation(), turnId() (+2 more)

### Community 63 - "header.tsx"
Cohesion: 0.23
Nodes (9): ContextPanel(), DecisionRow(), toneFor(), ChatHeader(), Badge(), Tone, TONES, initialsOf() (+1 more)

### Community 64 - "chat-shell.tsx"
Cohesion: 0.26
Nodes (8): ChatShell(), Composer(), FeedbackPopup(), QuickReplies(), resolvedReplies(), starterReplies(), refreshTrip(), QuickReply

### Community 65 - "conftest.py"
Cohesion: 0.18
Nodes (11): isolate_passenger_chats(), no_live_postgres(), no_real_provider_key(), fixture, Suite-wide isolation from whatever keys a developer has lying around. `pytest`…, Each test starts without another test's transcript on the seeded passengers., clean_env(), fixture (+3 more)

### Community 66 - "tools.py"
Cohesion: 0.26
Nodes (8): _assistant_tools(), _history(), _invented_money(), LLM-as-orchestrator loop. The model decides which tools to call. Tools enforce…, run_llm_agent(), _system_for(), money_in(), Deterministic tools the LLM agent may invoke. The model chooses *when* to call…

### Community 67 - "ToolRuntime"
Cohesion: 0.17
Nodes (8): _accepted(), _decision_payload(), Any, Session-scoped tool implementations. Isolation is enforced here, not by the…, The only channel by which frustration reaches the policy engine., Assess the passenger's state from the real transcript. Takes no arguments on…, Duty-of-care handover. Deliberately not a tool the model can call. Private for…, ToolRuntime

### Community 68 - "schemas.py"
Cohesion: 0.11
Nodes (20): expand_scope(), Booking, Widen the citable scope using facts only known after the booking is loaded. A…, Booking, Customer, KnownFact, One retrieved policy clause. Clause-level, never a whole rule body., Which retrievers this turn needs. Zia-style function classification. (+12 more)

### Community 69 - "LlmFactory"
Cohesion: 0.21
Nodes (14): LlmFactory, Clients request an LlmClient. They never read provider environment variables.…, test_key_is_never_exposed_by_health(), main(), Ask the configured provider which models your key can actually serve. cd…, heading(), key_authenticates(), live_call() (+6 more)

### Community 70 - "_dedupe"
Cohesion: 0.33
Nodes (5): _dedupe(), _fallback_models(), `model` first, then every sibling worth trying if it will not answer., The chain behind the chosen model, from env if set and the family if not. A…, Order-preserving, so the head stays the model the operator asked for.

### Community 71 - "reset_session"
Cohesion: 0.18
Nodes (16): conversation_for(), get_session(), _remember(), reset_session(), _stored_session(), isolate_seeded_chats(), fixture, test_tone_does_not_change_a_single_policy_outcome() (+8 more)

### Community 72 - "thread.tsx"
Cohesion: 0.53
Nodes (4): Thread(), TypingIndicator(), previousExecuted(), formatTime()

### Community 73 - "test_llm.py"
Cohesion: 0.08
Nodes (36): A client that can never call out, for tests and for LLM_PROVIDER=none., _detect_provider(), from_env(), _int(), Honour an explicit choice, else take the first provider holding a key., Whether to ask this provider to skip deliberation. Sending the parameter to a…, _reasoning_effort(), Provider resolution, spend ceilings, and graceful degradation. Nothing here… (+28 more)

### Community 74 - "main.py"
Cohesion: 0.06
Nodes (54): Staff sessions stay in process so operations login survives across requests., StaffFactory, add_my_booking(), analytics(), assess(), case(), cases(), chat() (+46 more)

### Community 76 - "store.py"
Cohesion: 0.47
Nodes (4): main(), Run the three assignment scenarios and print a transcript with measurements. cd…, show_turn(), summarise()

### Community 77 - "ElasticsearchOrJSON"
Cohesion: 0.22
Nodes (9): Conversation Graph Edges, CustomerMessage, ElasticsearchOrJSON, ESCALATE, EscalationPacket, Knowledge Base Indices, ManagerDesk, RetrieveThisPassengerOnly (+1 more)

## Knowledge Gaps
- **189 isolated node(s):** `inter`, `metadata`, `View`, `COLUMNS`, `Series` (+184 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **8 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `SessionMemory` connect `SessionMemory` to `client_with`, `tools.py`, `ToolRuntime`, `schemas.py`, `reset_session`, `frustration.py`, `Extraction`, `test_llm.py`, `PickySdk`, `test_factories.py`, `loop.py`, `LlmExtractor`, `test_frustration.py`, `closure.py`, `Fixed`, `baseline_for_booking`?**
  _High betweenness centrality (0.044) - this node is a cross-community bridge._
- **Why does `PassengerKnowledgeStore` connect `PassengerKnowledgeStore` to `schemas.py`, `frustration.py`, `self_service.py`, `factories/__init__.py`, `test_factories.py`, `loop.py`, `SessionMemory`, `connect`?**
  _High betweenness centrality (0.043) - this node is a cross-community bridge._
- **Why does `handle_chat()` connect `handle_chat` to `client_with`, `tools.py`, `schemas.py`, `LlmFactory`, `reset_session`, `Extraction`, `main.py`, `store.py`, `loop.py`, `LlmExtractor`, `test_frustration.py`, `SessionMemory`, `Fixed`, `test_containment.py`?**
  _High betweenness centrality (0.031) - this node is a cross-community bridge._
- **Are the 11 inferred relationships involving `SessionMemory` (e.g. with `ToolRuntime` and `IntentExtractor`) actually correct?**
  _`SessionMemory` has 11 INFERRED edges - model-reasoned connections that need verification._
- **Are the 11 inferred relationships involving `PassengerKnowledgeStore` (e.g. with `HasherFactory` and `Booking`) actually correct?**
  _`PassengerKnowledgeStore` has 11 INFERRED edges - model-reasoned connections that need verification._
- **What connects `inter`, `metadata`, `View` to the rest of the system?**
  _189 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `PolicyDecision` be split into smaller, more focused modules?**
  _Cohesion score 0.10900045228403438 - nodes in this community are weakly interconnected._
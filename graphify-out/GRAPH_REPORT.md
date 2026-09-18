# Graph Report - Assesment_project_Custormer-Facing_Resolution_Agent_AIONOS  (2026-09-19)

## Corpus Check
- 150 files · ~57,377 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1393 nodes · 3540 edges · 67 communities (59 shown, 8 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 265 edges (avg confidence: 0.56)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `1965e067`
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
- SessionMemory
- Extraction
- LlmFactory
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
- handle_chat
- .create
- client_with
- _FakeEs
- AeroResolve
- JsonKnowledgeStore
- demo_scenarios.py
- context.py
- Fixed
- LlmClient
- sign-in.tsx
- cards.tsx
- test_containment.py
- AuthSession
- test_retrieval.py
- store.ts
- header.tsx
- chat-shell.tsx
- ToolRuntime
- ElasticsearchKnowledgeStore
- thread.tsx
- loop.py
- test_frustration.py
- main.py
- policy_clauses

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

## Communities (67 total, 8 thin omitted)

### Community 0 - "schemas.py"
Cohesion: 0.06
Nodes (66): Deterministic tools the LLM agent may invoke. The model chooses *when* to call…, OnboardingFactory, PolicyHandlerFactory, Maps a request type to a PolicyHandler. Engine never constructs handlers itself., Booking, BookingIntake, Customer, DecisionStatus (+58 more)

### Community 1 - "test_llm.py"
Cohesion: 0.08
Nodes (40): A client that can never call out, for tests and for LLM_PROVIDER=none., _dedupe(), _detect_provider(), disabled_config(), _fallback_models(), _float(), from_env(), _int() (+32 more)

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

### Community 7 - "SessionMemory"
Cohesion: 0.10
Nodes (30): _caps_lock(), _category(), classify(), _confidence(), detect_legal_or_formal(), _intents(), is_low_confidence(), _punctuation_escalation() (+22 more)

### Community 8 - "Extraction"
Cohesion: 0.18
Nodes (11): render_extract_prompt(), detect_emotion(), The existing tone axis: angry / frustrated / confused, or nothing. Kept…, Extraction, IntentExtractor, ABC, Product: turn a customer utterance into structured extraction. Never decides…, needs_model() (+3 more)

### Community 9 - "LlmFactory"
Cohesion: 0.08
Nodes (31): Facade — always goes through ReplyFactory., render_reply(), ExtractorFactory, Clients request an IntentExtractor. They never construct concrete extractors., LlmFactory, Clients request an LlmClient. They never read provider environment variables.…, ReplyFactory, HeuristicExtractor (+23 more)

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
Cohesion: 0.33
Nodes (6): ALLOW, ASK, DENY, ESCALATE, EscalationPacket, PolicyEngine

### Community 19 - "frontend/app/layout.tsx"
Cohesion: 0.40
Nodes (3): jakarta, metadata, viewport

### Community 27 - "PassengerKnowledgeStore"
Cohesion: 0.06
Nodes (22): _category_counts(), PassengerKnowledgeStore, ABC, Any, Booking, RuleHit, Map a PolicyDecision.source label back onto indexed rule ids., Record one frustration observation as an event plus a graph edge. Deliberately… (+14 more)

### Community 28 - "ops.ts"
Cohesion: 0.05
Nodes (64): OperationsPage(), View, CaseBoard(), CaseCard(), COLUMNS, CaseDrawer(), StatusPill(), Donut() (+56 more)

### Community 39 - "AeroResolve — System Architecture & HLD"
Cohesion: 0.05
Nodes (39): 10. HTTP API, 11. Frontends, 12. Closed codes, 13. Auth, 14. Demo contracts this architecture must preserve, 1. Product thesis, 2.1 Design split, 2.2 System context (+31 more)

### Community 42 - "handle_chat"
Cohesion: 0.18
Nodes (13): handle_chat(), test_a_waiver_above_the_limit_reports_itself_as_escalated(), test_an_entitlement_turn_is_contained_and_fully_cited(), test_no_llm_key_means_no_spend(), test_the_escalation_case_carries_both_prose_and_codes(), test_the_turn_trace_reports_the_measurement_to_the_reviewer(), test_turn_event_carries_the_full_telemetry_set(), test_a_calm_turn_is_contained_and_names_no_distress() (+5 more)

### Community 43 - ".create"
Cohesion: 0.32
Nodes (11): test_key_is_never_exposed_by_health(), main(), heading(), key_authenticates(), live_call(), live_turn(), main(), End-to-end check of the LLM layer against a real provider. cd backend &&… (+3 more)

### Community 44 - "client_with"
Cohesion: 0.07
Nodes (56): chained(), client_with(), config(), models_tried(), PickySdk, Serves only the models it was given a quota for; the rest raise 429. This is…, Regression: the original renderer sent no max_tokens at all., A model that returns nothing is as useless as one that errors. (+48 more)

### Community 46 - "AeroResolve"
Cohesion: 0.29
Nodes (8): FastAPI, Uvicorn, AIONOS-Style Constraint, Context-First Loop, Architecture Slide, AeroResolve, Model Talks, Deterministic Code Decides, Product Thesis

### Community 47 - "JsonKnowledgeStore"
Cohesion: 0.23
Nodes (7): KnowledgeStoreFactory, Clients request a PassengerKnowledgeStore. They never construct JSON or…, JsonKnowledgeStore, Concrete product: in-memory passenger KB seeded from the assignment JSON pack., test_knowledge_factory_auto_never_raises_when_es_is_down(), test_knowledge_factory_json_product_is_interface_not_elasticsearch(), test_json_and_elasticsearch_cite_the_same_clauses_for_the_three_scenarios()

### Community 48 - "demo_scenarios.py"
Cohesion: 0.60
Nodes (4): main(), Run the three assignment scenarios and print a transcript with measurements. cd…, show_turn(), summarise()

### Community 52 - "context.py"
Cohesion: 0.13
Nodes (30): assemble(), _disruption(), _facts(), packet_for_ui(), Booking, render_respond_prompt(), extract(), Facade — always goes through ExtractorFactory. (+22 more)

### Community 53 - "Fixed"
Cohesion: 0.11
Nodes (27): CustomerAgentContext, ABC, ReplyRenderer, LlmPolishedReplyRenderer, money_amounts(), normalise(), Plain ASCII spacing, so the same figure compares equal either side., Phrasing only. The template reply is already policy-approved, and every path… (+19 more)

### Community 55 - "LlmClient"
Cohesion: 0.05
Nodes (33): LlmBudget, Which model actually answered. The chain means it may not be the first., Every ceiling that stops a runaway bill, plus an extraction cache. A breach is…, Name the breached ceiling, or None to proceed. Records nothing — the caller…, Record a degradation the client hit rather than a ceiling, e.g. a timeout., Start metering one conversational turn, so its cost can be reported. Day totals…, LlmClient, LlmResult (+25 more)

### Community 56 - "sign-in.tsx"
Cohesion: 0.16
Nodes (16): BrandMark(), Wordmark(), InlineCard(), Mode, SignIn(), Button, ButtonProps, Size (+8 more)

### Community 57 - "cards.tsx"
Cohesion: 0.18
Nodes (18): AgentCards(), ChoiceCard(), ConfirmationCard(), CHOICE_STATUSES, choiceDecisions(), newActions(), repliesForTurn(), ACTION_ACTIONS (+10 more)

### Community 59 - "test_containment.py"
Cohesion: 0.24
Nodes (15): _percentile(), Nearest-rank percentile over a pre-sorted list., fresh_store(), measured_turn(), Containment: the metric that answers how much work needed no human. Two layers…, test_a_store_with_no_measured_turns_reports_zero_not_a_fake_rate(), test_analytics_summary_embeds_containment(), test_containment_rate_is_contained_over_measured() (+7 more)

### Community 60 - "AuthSession"
Cohesion: 0.11
Nodes (11): AuthFactory, Session tokens are a singleton product so login survives across requests., HasherFactory, CredentialHasher, ABC, Product: hash and verify passenger passwords. Clients never pick an algorithm., InMemoryTokenSession, Pbkdf2Hasher (+3 more)

### Community 61 - "test_retrieval.py"
Cohesion: 0.09
Nodes (38): context_contains_forbidden(), narrate(), Render the decided packet as prose with clause-level citations. Every line is…, Code-side gate: other passengers, raw policy bodies, and history-as-benefit., expand_scope(), plan_retrieval(), Booking, _query() (+30 more)

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
Cohesion: 0.09
Nodes (26): _assistant_tools(), _history(), _invented_money(), LLM-as-orchestrator loop. The model decides which tools to call. Tools enforce…, run_llm_agent(), _system_for(), _accepted(), _decision_payload() (+18 more)

### Community 68 - "ElasticsearchKnowledgeStore"
Cohesion: 0.14
Nodes (5): ElasticsearchKnowledgeStore, Any, RuleHit, Concrete product: Elasticsearch dual-write plus query-backed retrieval. Every…, Passenger lookup is a filtered query, not a scan of `self.passengers`.

### Community 69 - "thread.tsx"
Cohesion: 0.53
Nodes (4): Thread(), TypingIndicator(), previousExecuted(), formatTime()

### Community 71 - "loop.py"
Cohesion: 0.15
Nodes (22): _case_status(), _deterministic_turn(), _finish(), _frustration_trace(), _identify(), _issue_label(), One trace line, identical on both agent paths, so a reviewer can see the signal…, Same edges on both agent paths, so Operations can draw the live KB. (+14 more)

### Community 73 - "test_frustration.py"
Cohesion: 0.05
Nodes (75): Both gates, or neither. A hostile guess is not a reason to fetch a human., should_escalate(), ExtractedRequest, delay_entitlements(), evaluate_policy(), PolicyDecision, Independent thresholds from the data pack. Does not invent amounts for >3h meal…, parametrize (+67 more)

### Community 74 - "main.py"
Cohesion: 0.06
Nodes (52): reset_session(), Staff sessions stay in process so operations login survives across requests., StaffFactory, add_my_booking(), analytics(), assess(), case(), cases() (+44 more)

### Community 80 - "policy_clauses"
Cohesion: 0.28
Nodes (6): _clauses(), policy_clauses(), policies.json flattened to clause granularity. Clause-level rather than rule-…, style_docs(), test_every_clause_stays_within_the_retrieval_char_budget(), test_policy_corpus_is_clause_level_not_rule_level()

## Knowledge Gaps
- **184 isolated node(s):** `inter`, `metadata`, `View`, `COLUMNS`, `Series` (+179 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **8 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `PassengerKnowledgeStore` connect `PassengerKnowledgeStore` to `schemas.py`, `ElasticsearchKnowledgeStore`, `loop.py`, `JsonKnowledgeStore`, `policy_clauses`, `context.py`, `AuthSession`, `test_retrieval.py`?**
  _High betweenness centrality (0.066) - this node is a cross-community bridge._
- **Why does `SessionMemory` connect `SessionMemory` to `schemas.py`, `test_llm.py`, `ToolRuntime`, `loop.py`, `Extraction`, `LlmFactory`, `test_frustration.py`, `client_with`, `_FakeEs`, `context.py`, `Fixed`, `test_retrieval.py`?**
  _High betweenness centrality (0.044) - this node is a cross-community bridge._
- **Why does `LlmClient` connect `LlmClient` to `test_llm.py`, `ToolRuntime`, `Extraction`, `LlmFactory`, `.create`, `client_with`, `Fixed`?**
  _High betweenness centrality (0.034) - this node is a cross-community bridge._
- **Are the 11 inferred relationships involving `SessionMemory` (e.g. with `ToolRuntime` and `IntentExtractor`) actually correct?**
  _`SessionMemory` has 11 INFERRED edges - model-reasoned connections that need verification._
- **Are the 11 inferred relationships involving `PassengerKnowledgeStore` (e.g. with `HasherFactory` and `Booking`) actually correct?**
  _`PassengerKnowledgeStore` has 11 INFERRED edges - model-reasoned connections that need verification._
- **Are the 14 inferred relationships involving `StubSdk` (e.g. with `ExtractorFactory` and `LlmFactory`) actually correct?**
  _`StubSdk` has 14 INFERRED edges - model-reasoned connections that need verification._
- **What connects `inter`, `metadata`, `View` to the rest of the system?**
  _184 weakly-connected nodes found - possible documentation gaps or missing edges._
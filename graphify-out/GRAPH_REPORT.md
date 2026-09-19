# Graph Report - Assesment_project_Custormer-Facing_Resolution_Agent_AIONOS  (2026-09-19)

## Corpus Check
- 183 files · ~78,850 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1802 nodes · 4759 edges · 91 communities (79 shown, 12 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 302 edges (avg confidence: 0.55)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `899dd9ee`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- PolicyDecision
- api
- index.ts
- devDependencies
- dependencies
- compilerOptions
- compilerOptions
- SessionMemory
- test_factories.py
- test_history.py
- AeroResolve
- reset_session
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
- corpus.py
- CustomerAgentContext
- closure.py
- LlmFactory
- test_frustration.py
- inventory.py
- orchestrator.py
- AuthSession
- test_context.py
- PickySdk
- handle_chat
- LlmBudget
- sign-in.tsx
- cards.tsx
- Any
- _FakeEs
- Customer
- exit-board.tsx
- useConversation
- client_with
- context-panel.tsx
- PostgresKnowledgeStore
- .operations
- test_distress_escalation_adds_no_policy_decision
- schemas.py
- .create
- vercel-build.sh
- test_containment.py
- demo_scenarios.py
- test_llm.py
- main.py
- should_escalate
- render_extract_prompt
- .frustration
- loop.py
- ToolRuntime
- ._persist
- chat-shell.tsx
- Extraction
- JsonKnowledgeStore
- Optional Elasticsearch Knowledge Base
- test_the_classifier_tool_ignores_text_the_model_supplies
- score
- test_retrieval.py
- ElasticsearchOrJSON
- .append_frustration
- .pending_kb

## God Nodes (most connected - your core abstractions)
1. `SessionMemory` - 125 edges
2. `handle_chat()` - 89 edges
3. `PassengerKnowledgeStore` - 84 edges
4. `client_with()` - 66 edges
5. `StubSdk` - 57 edges
6. `evaluate_policy()` - 56 edges
7. `ToolRuntime` - 54 edges
8. `Customer` - 51 edges
9. `ExtractedRequest` - 49 edges
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

## Communities (91 total, 12 thin omitted)

### Community 0 - "PolicyDecision"
Cohesion: 0.09
Nodes (52): missing_slots(), Deterministic tools the LLM agent may invoke. The model chooses *when* to call…, PolicyHandlerFactory, Maps a request type to a PolicyHandler. Engine never constructs handlers itself., DecisionStatus, EscalationReason, FrustrationCategory, PolicyDecision (+44 more)

### Community 1 - "api"
Cohesion: 0.12
Nodes (15): entrypoint, framework, functions, root, vercel_app.py, framework, root, rewrites (+7 more)

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
Cohesion: 0.09
Nodes (38): _caps_lock(), _category(), classify(), classify_llm(), _classify_llm_user(), _confidence(), _intents(), _latest_user() (+30 more)

### Community 8 - "test_factories.py"
Cohesion: 0.21
Nodes (11): KnowledgeStoreFactory, Clients request a PassengerKnowledgeStore. They never construct JSON, Postgres,…, test_embedding_factory_disabled_is_a_noop(), test_extractor_factory_returns_product_interface(), test_knowledge_factory_auto_never_raises_when_es_is_down(), test_knowledge_factory_auto_skips_local_elasticsearch_on_render(), test_knowledge_factory_json_product_is_interface_not_elasticsearch(), test_knowledge_factory_postgres_requires_database_url() (+3 more)

### Community 9 - "test_history.py"
Cohesion: 0.42
Nodes (8): conversation_for(), get_session(), _remember(), _stored_session(), _forget(), test_new_browser_session_restores_that_passenger_only(), test_restart_clears_only_that_passenger_history(), test_two_passengers_keep_separate_chat_histories()

### Community 10 - "AeroResolve"
Cohesion: 0.17
Nodes (16): FastAPI, Uvicorn, Arvind Chip Demo, Drive Video Plan, 15-Minute Live Demo, Manager Desk Demo, Meher Chip Demo, Priya Chip Demo (+8 more)

### Community 11 - "reset_session"
Cohesion: 0.10
Nodes (32): detect_emotion(), detect_legal_or_formal(), The existing tone axis: angry / frustrated / confused, or nothing. Kept…, reset_session(), classify(), _is_assist_follow_up(), persist_assist(), Classify turns that are not disruption entitlements. Disruption money still… (+24 more)

### Community 12 - "Context-First Loop"
Cohesion: 0.22
Nodes (9): Context-First Loop, Fail Closed on Unknown Benefits, Architecture Slide, Journey Compression, Limits and Tools, Passenger Forced to Become Policy Expert, UNDERSTAND GROUND DECIDE ACT ESCALATE AUDIT, Unknown ≠ Allowed (+1 more)

### Community 13 - "types.ts"
Cohesion: 0.14
Nodes (21): api, ApiError, OPS_URL, StaffAuthResult, Persisted, State, AuthResult, Booking (+13 more)

### Community 14 - "scripts"
Cohesion: 0.22
Nodes (8): name, private, scripts, build, dev:api, dev:ops, dev:web, test

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
Nodes (8): PassengerKnowledgeStore, ABC, Booking, Optional durable delete. JSON product is in-memory only., Keep a passenger on this process without a password (Vercel isolate hop)., Map a PolicyDecision.source label back onto indexed rule ids., Nearest approved prior resolutions by embedding similarity. Reads `kb_entries`…, Product: passenger 360 / events / cases / graph. Clients never construct a…

### Community 28 - "ops.ts"
Cohesion: 0.05
Nodes (68): OperationsPage(), View, CaseBoard(), CaseCard(), COLUMNS, CaseDrawer(), StatusPill(), Donut() (+60 more)

### Community 39 - "AeroResolve — System Architecture & HLD"
Cohesion: 0.05
Nodes (40): 10. HTTP API, 11. Frontends, 12. Closed codes, 13. Auth, 14. Demo contracts this architecture must preserve, 1. Product thesis, 2.1 Design split, 2.2 System context (+32 more)

### Community 42 - "factories/__init__.py"
Cohesion: 0.12
Nodes (16): AuthFactory, Session tokens are a singleton product so login survives across requests., HasherFactory, OnboardingFactory, Staff sessions stay in process so operations login survives across requests., StaffFactory, CredentialHasher, ABC (+8 more)

### Community 43 - "evaluate_policy"
Cohesion: 0.11
Nodes (39): ExtractedRequest, delay_entitlements(), evaluate_policy(), PolicyDecision, Independent thresholds from the data pack. Does not invent amounts for >3h meal…, parametrize, Allowed and denied outcomes must not carry an escalation cause., Guards new handlers: an ESCALATE with no code would vanish from the breakdown. (+31 more)

### Community 44 - "corpus.py"
Cohesion: 0.25
Nodes (8): load_help(), _clauses(), help_docs(), policy_clauses(), policies.json flattened to clause granularity. Clause-level rather than rule-…, style_docs(), test_every_clause_stays_within_the_retrieval_char_budget(), test_policy_corpus_is_clause_level_not_rule_level()

### Community 45 - "CustomerAgentContext"
Cohesion: 0.12
Nodes (28): Facade — always goes through ReplyFactory., render_reply(), ReplyFactory, CustomerAgentContext, ABC, ReplyRenderer, LlmPolishedReplyRenderer, money_amounts() (+20 more)

### Community 46 - "closure.py"
Cohesion: 0.08
Nodes (47): already_asked_feedback(), asked_if_resolved(), asks_to_close_case(), confirms_resolution(), is_greeting(), is_thanks(), last_assistant_text(), offered_supervisor() (+39 more)

### Community 47 - "LlmFactory"
Cohesion: 0.13
Nodes (15): LlmFactory, Clients request an LlmClient. They never read provider environment variables.…, isolate_passenger_chats(), no_live_postgres(), no_real_provider_key(), fixture, Suite-wide isolation from whatever keys a developer has lying around. `pytest`…, Each test starts without another test's transcript on the seeded passengers. (+7 more)

### Community 48 - "test_frustration.py"
Cohesion: 0.14
Nodes (27): fresh_store(), observation(), Frustration is a signal, and these tests are what keep it one. Layered the same…, Same import-time getenv as KB_AUTO_STORE_THRESHOLD, so tests can pin it., Operations draws the same graph_edges store, not a side table., test_a_calm_turn_is_contained_and_names_no_distress(), test_a_confident_observation_is_stored_and_aggregated(), test_a_distressed_turn_escalates_and_records_with_zero_llm_key() (+19 more)

### Community 49 - "inventory.py"
Cohesion: 0.24
Nodes (17): _as_suggested(), _date_matches(), _href(), _norm(), Any, _random_flight(), Look-only departures for booking assist. Scheduled rows come from the upcoming…, Look-only match after the passenger named a route. No guesswork before that. (+9 more)

### Community 50 - "orchestrator.py"
Cohesion: 0.20
Nodes (14): _assistant_tools(), _history(), _invented_money(), LLM-as-orchestrator loop. The model decides which tools to call. Tools enforce…, run_llm_agent(), _system_for(), _collect_money(), money_in() (+6 more)

### Community 51 - "AuthSession"
Cohesion: 0.07
Nodes (25): connect(), database_url(), Any, Thread-local psycopg connection. Schema is applied once per connection., InMemoryTokenSession, Signed tokens — no process-local map, so Vercel isolates can share a login., PostgresTokenSession, Passenger login tokens survive a process restart when Postgres is up. (+17 more)

### Community 52 - "test_context.py"
Cohesion: 0.15
Nodes (27): assemble(), _disruption(), _facts(), packet_for_ui(), Booking, render_respond_prompt(), extract(), Facade — always goes through ExtractorFactory. (+19 more)

### Community 53 - "PickySdk"
Cohesion: 0.10
Nodes (28): chained(), models_tried(), PickySdk, Serves only the models it was given a quota for; the rest raise 429. This is…, A model that returns nothing is as useless as one that errors., One timeout per model would be the whole chain's wait for the passenger., Free-tier quota lasts hours, so re-leading with it would waste the walk., Demoted, never retired: quota comes back and the preferred model resumes. (+20 more)

### Community 54 - "handle_chat"
Cohesion: 0.13
Nodes (30): handle_chat(), Structured 1–5 rating from the chat UI. Same close rules as a spoken rating., submit_feedback(), test_no_key_is_honest_fallback_not_a_live_llm(), _case(), Priya's unknown_entitlement stays escalated after 'that's fine' + 5★., test_booking_assist_does_not_append_a_resolved_survey(), test_card_feedback_endpoint_closes_when_rating_is_good() (+22 more)

### Community 55 - "LlmBudget"
Cohesion: 0.05
Nodes (28): LlmBudget, Which model actually answered. The chain means it may not be the first., Every ceiling that stops a runaway bill, plus an extraction cache. A breach is…, Name the breached ceiling, or None to proceed. Records nothing — the caller…, Record a degradation the client hit rather than a ceiling, e.g. a timeout., Start metering one conversational turn, so its cost can be reported. Day totals…, LlmClient, LlmResult (+20 more)

### Community 56 - "sign-in.tsx"
Cohesion: 0.17
Nodes (15): BrandMark(), Wordmark(), InlineCard(), Thread(), TypingIndicator(), DEMO_ACCOUNTS, Mode, SignIn() (+7 more)

### Community 57 - "cards.tsx"
Cohesion: 0.16
Nodes (21): AgentCards(), BookingCard(), ChoiceCard(), ConfirmationCard(), SuggestedFlightCard(), CHOICE_STATUSES, choiceDecisions(), newActions() (+13 more)

### Community 58 - "Any"
Cohesion: 0.18
Nodes (3): Any, What the customer UI should show: this passenger's transcript, nobody else's., The live passenger knowledge base, as a graph Operations can draw. Dedupes…

### Community 60 - "Customer"
Cohesion: 0.13
Nodes (18): BookingIntake, Customer, SignupRequest, TravelHistory, Passenger lookup is a filtered query, not a scan of `self.passengers`., PassengerOnboarding, ABC, Any (+10 more)

### Community 61 - "exit-board.tsx"
Cohesion: 0.26
Nodes (5): metadata, clockLabel(), ExitBoard(), FALLBACK_FLIGHTS, SuggestedFlight

### Community 62 - "useConversation"
Cohesion: 0.31
Nodes (10): LoginPage(), ResolvePage(), useReady(), greeting(), messageFor(), newSessionId(), openConversation(), turnId() (+2 more)

### Community 63 - "client_with"
Cohesion: 0.08
Nodes (43): _args(), LLM agent loop: the model orchestrates, tools enforce policy., Returns a sequence of chat.completions payloads, including tool calls., ScriptedSdk, test_agent_calls_booking_then_policy_then_answers(), test_agent_chat_sends_tools_to_the_model(), test_live_agent_path_records_tool_calls(), The same live-client test as agent_mode, not a third branch. (+35 more)

### Community 64 - "context-panel.tsx"
Cohesion: 0.32
Nodes (6): ContextPanel(), DecisionRow(), toneFor(), Badge(), Tone, TONES

### Community 65 - "PostgresKnowledgeStore"
Cohesion: 0.27
Nodes (6): _as_vector(), _json(), PostgresKnowledgeStore, Any, Concrete product: Postgres is the system of record, RAM is a cache. Seed…, test_postgres_keeps_self_service_passenger_across_store_instances()

### Community 66 - ".operations"
Cohesion: 0.33
Nodes (3): Lightweight dashboard numbers. Policy is not computed here., How much of the work needed no human, and where authority ran out. Only turns…, _seconds_between()

### Community 67 - "test_distress_escalation_adds_no_policy_decision"
Cohesion: 0.20
Nodes (6): It must not borrow another reason's code to get a supervisor., Absent from handlers(), so the model cannot self-serve a reason code., Both fire on the same turn, and neither hides behind the other., test_distress_escalation_adds_no_policy_decision(), test_policy_and_distress_escalations_are_logged_as_distinct_reasons(), test_the_distress_escalation_is_not_a_tool_the_model_can_call()

### Community 68 - "schemas.py"
Cohesion: 0.09
Nodes (23): Booking, ChatResponse, KbHit, KbMatch, KnownFact, One retrieved policy clause. Clause-level, never a whole rule body., One approved prior resolution, ranked by embedding cosine., Whether this turn reused a prior resolution or queued one for ops. (+15 more)

### Community 69 - ".create"
Cohesion: 0.36
Nodes (10): test_key_is_never_exposed_by_health(), heading(), key_authenticates(), live_call(), live_turn(), main(), End-to-end check of the LLM layer against a real provider. cd backend &&…, The real test: does a model in the loop still yield the policy outcome. (+2 more)

### Community 71 - "test_containment.py"
Cohesion: 0.14
Nodes (23): _percentile(), Nearest-rank percentile over a pre-sorted list., fresh_store(), measured_turn(), Containment: the metric that answers how much work needed no human. Two layers…, The two counters are independent slices, not a partition of turns., test_a_store_with_no_measured_turns_reports_zero_not_a_fake_rate(), test_a_waiver_above_the_limit_reports_itself_as_escalated() (+15 more)

### Community 72 - "demo_scenarios.py"
Cohesion: 0.60
Nodes (4): main(), Run the three assignment scenarios and print a transcript with measurements. cd…, show_turn(), summarise()

### Community 73 - "test_llm.py"
Cohesion: 0.07
Nodes (44): A client that can never call out, for tests and for LLM_PROVIDER=none., _dedupe(), _detect_provider(), disabled_config(), _fallback_models(), _float(), from_env(), _int() (+36 more)

### Community 74 - "main.py"
Cohesion: 0.08
Nodes (52): add_my_booking(), analytics(), approve_kb(), approve_pending_kb(), assess(), case(), cases(), chat() (+44 more)

### Community 75 - "should_escalate"
Cohesion: 0.22
Nodes (11): _assessment_from_llm(), is_low_confidence(), Both gates, or neither. A hostile guess is not a reason to fetch a human., Below the store threshold the observation is logged but not aggregated., should_escalate(), parametrize, A confident read of mild annoyance is not a reason to fetch a human., test_confidence_at_or_above_the_threshold_is_counted() (+3 more)

### Community 76 - "render_extract_prompt"
Cohesion: 0.25
Nodes (7): context_contains_forbidden(), Code-side gate: other passengers, raw policy bodies, and history-as-benefit., render_extract_prompt(), Extract and respond prompt contracts. Rendered from an assembled…, test_extract_prompt_is_narrow_and_has_no_policy_schema(), test_extract_prompt_does_not_replay_the_whole_transcript(), test_narrated_prompt_still_hides_other_passengers_and_raw_policy()

### Community 77 - ".frustration"
Cohesion: 0.25
Nodes (6): _category_counts(), Counts in severity order, and only for categories actually observed. Fixed key…, How distressed the traffic was, and whether distress cost containment. Low-…, Did high frustration correlate with needing a human? Keyed on the…, Aggregate the EXHIBITS_FRUSTRATION edges themselves. Read from `graph_edges`…, _tally()

### Community 78 - "loop.py"
Cohesion: 0.09
Nodes (35): case_status(), Sticky case state for this conversation. Executed actions never close it., ground_prior_resolution(), Reuse a prior resolution's phrasing, or queue the turn for ops approval. Runs…, Embed this turn, reuse a close prior phrasing, or queue a pending row., _case_status(), _deterministic_turn(), _frustration_trace() (+27 more)

### Community 79 - "ToolRuntime"
Cohesion: 0.15
Nodes (10): _accepted(), _decision_payload(), Any, Session-scoped tool implementations. Isolation is enforced here, not by the…, The only channel by which frustration reaches the policy engine., Assess the passenger's state from the real transcript. Takes no arguments on…, Duty-of-care handover. Deliberately not a tool the model can call. Private for…, ToolRuntime (+2 more)

### Community 80 - "._persist"
Cohesion: 0.13
Nodes (6): Optional dual-write. JSON product is in-memory only., Park an unseen phrasing for ops. Does not embed or index., Write one approved resolution into the corpus semantic_search reads., Embed and index. The only write path into the searchable KB., Supervisor decision on one pending observation. Same event row, no new index., Write the passenger's live conversation so the next login can restore it.

### Community 81 - "chat-shell.tsx"
Cohesion: 0.14
Nodes (17): ChatShell(), Composer(), FeedbackPopup(), ChatHeader(), QuickReplies(), Button, ButtonProps, Size (+9 more)

### Community 82 - "Extraction"
Cohesion: 0.12
Nodes (21): ExtractorFactory, Clients request an IntentExtractor. They never construct concrete extractors., Extraction, IntentExtractor, ABC, Product: turn a customer utterance into structured extraction. Never decides…, LlmExtractor, needs_model() (+13 more)

### Community 83 - "JsonKnowledgeStore"
Cohesion: 0.06
Nodes (30): EmbeddingClient, Built once, on first use. Disabled clients never construct one., The single place this codebase talks to an embedding model. OpenAI `text-…, A client that can never call out, for tests and for EMBEDDING_PROVIDER=none., One 1536-d vector, or None when this client must not call out., EmbeddingFactory, Clients request an EmbeddingClient. They never read provider environment…, A client that can never call out, for tests and for EMBEDDING_PROVIDER=none. (+22 more)

### Community 84 - "Optional Elasticsearch Knowledge Base"
Cohesion: 0.50
Nodes (5): elasticsearch Python Client, Elasticsearch Service, Optional Elasticsearch Knowledge Base, JSON Data Pack Fallback, Knowledge Base Store

### Community 86 - "score"
Cohesion: 0.22
Nodes (6): RuleHit, cosine(), Length-normalized term overlap. Dependency-free on purpose: the JSON backend…, Cosine similarity of two embedding vectors. 0.0 when either side is empty., score(), tokenize()

### Community 87 - "test_retrieval.py"
Cohesion: 0.10
Nodes (32): narrate(), Render the decided packet as prose with clause-level citations. Every line is…, expand_scope(), plan_retrieval(), Booking, _query(), Classify the turn into the retrievers it needs, before any fetching happens., Widen the citable scope using facts only known after the booking is loaded. A… (+24 more)

### Community 89 - "ElasticsearchOrJSON"
Cohesion: 0.22
Nodes (9): Conversation Graph Edges, CustomerMessage, ElasticsearchOrJSON, ESCALATE, EscalationPacket, Knowledge Base Indices, ManagerDesk, RetrieveThisPassengerOnly (+1 more)

## Knowledge Gaps
- **203 isolated node(s):** `inter`, `metadata`, `View`, `COLUMNS`, `Series` (+198 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **12 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `SessionMemory` connect `SessionMemory` to `PolicyDecision`, `test_history.py`, `reset_session`, `CustomerAgentContext`, `closure.py`, `test_frustration.py`, `orchestrator.py`, `test_context.py`, `PickySdk`, `handle_chat`, `_FakeEs`, `client_with`, `test_distress_escalation_adds_no_policy_decision`, `schemas.py`, `test_llm.py`, `render_extract_prompt`, `loop.py`, `ToolRuntime`, `Extraction`, `test_the_classifier_tool_ignores_text_the_model_supplies`, `test_retrieval.py`?**
  _High betweenness centrality (0.050) - this node is a cross-community bridge._
- **Why does `PassengerKnowledgeStore` connect `PassengerKnowledgeStore` to `PolicyDecision`, `PostgresKnowledgeStore`, `.operations`, `.pending_kb`, `schemas.py`, `test_factories.py`, `factories/__init__.py`, `corpus.py`, `.frustration`, `loop.py`, `.append_frustration`, `._persist`, `JsonKnowledgeStore`, `test_context.py`, `score`, `Any`, `Customer`?**
  _High betweenness centrality (0.043) - this node is a cross-community bridge._
- **Why does `JsonKnowledgeStore` connect `JsonKnowledgeStore` to `PostgresKnowledgeStore`, `schemas.py`, `test_containment.py`, `test_factories.py`, `_FakeEs`, `loop.py`, `test_frustration.py`, `handle_chat`, `test_retrieval.py`, `PassengerKnowledgeStore`?**
  _High betweenness centrality (0.038) - this node is a cross-community bridge._
- **Are the 11 inferred relationships involving `SessionMemory` (e.g. with `ToolRuntime` and `IntentExtractor`) actually correct?**
  _`SessionMemory` has 11 INFERRED edges - model-reasoned connections that need verification._
- **Are the 12 inferred relationships involving `PassengerKnowledgeStore` (e.g. with `EmbeddingFactory` and `HasherFactory`) actually correct?**
  _`PassengerKnowledgeStore` has 12 INFERRED edges - model-reasoned connections that need verification._
- **Are the 13 inferred relationships involving `StubSdk` (e.g. with `ExtractorFactory` and `LlmFactory`) actually correct?**
  _`StubSdk` has 13 INFERRED edges - model-reasoned connections that need verification._
- **What connects `inter`, `metadata`, `View` to the rest of the system?**
  _203 weakly-connected nodes found - possible documentation gaps or missing edges._
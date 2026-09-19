# Graph Report - Assesment_project_Custormer-Facing_Resolution_Agent_AIONOS  (2026-09-19)

## Corpus Check
- 183 files · ~78,671 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1801 nodes · 4758 edges · 95 communities (84 shown, 11 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 302 edges (avg confidence: 0.55)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `b6393181`
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
- frustration.py
- test_factories.py
- test_history.py
- 15-Minute Live Demo
- reset_session
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
- factories/__init__.py
- evaluate_policy
- knowledge/base.py
- LlmFactory
- closure.py
- llm_factory.py
- test_frustration.py
- inventory.py
- loop.py
- InMemoryTokenSession
- test_context.py
- PickySdk
- handle_chat
- LlmBudget
- sign-in.tsx
- cards.tsx
- Any
- test_agent.py
- schemas.py
- exit-board.tsx
- store.ts
- client_with
- context-panel.tsx
- PostgresKnowledgeStore
- AuthSession
- tools.py
- ElasticsearchKnowledgeStore
- .create
- vercel-build.sh
- test_containment.py
- .disabled
- test_llm.py
- main.py
- should_escalate
- SessionMemory
- .frustration
- test_kb_match.py
- ToolRuntime
- ._persist
- chat-shell.tsx
- LlmExtractor
- JsonKnowledgeStore
- AeroResolve
- .approve_pending_kb_entry
- score
- test_retrieval.py
- test_scenarios.py
- ElasticsearchOrJSON
- test_loop_calls_classify_llm_when_the_client_is_live
- detect_emotion
- .append_frustration
- classify
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

## Communities (95 total, 11 thin omitted)

### Community 0 - "PolicyDecision"
Cohesion: 0.12
Nodes (35): PolicyHandlerFactory, Maps a request type to a PolicyHandler. Engine never constructs handlers itself., DecisionStatus, EscalationReason, PolicyDecision, Why authority ran out, as a closed set so escalations aggregate. Every member…, RequestType, BookingAssistHandler (+27 more)

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

### Community 7 - "frustration.py"
Cohesion: 0.14
Nodes (20): _assessment_from_llm(), _caps_lock(), classify_llm(), _classify_llm_user(), detect_legal_or_formal(), _intents(), is_low_confidence(), _latest_user() (+12 more)

### Community 8 - "test_factories.py"
Cohesion: 0.29
Nodes (7): KnowledgeStoreFactory, Clients request a PassengerKnowledgeStore. They never construct JSON, Postgres,…, test_knowledge_factory_auto_never_raises_when_es_is_down(), test_knowledge_factory_auto_skips_local_elasticsearch_on_render(), test_knowledge_factory_json_product_is_interface_not_elasticsearch(), test_knowledge_factory_postgres_requires_database_url(), test_register_passenger_persists_the_account_row()

### Community 9 - "test_history.py"
Cohesion: 0.67
Nodes (5): conversation_for(), _forget(), test_new_browser_session_restores_that_passenger_only(), test_restart_clears_only_that_passenger_history(), test_two_passengers_keep_separate_chat_histories()

### Community 10 - "15-Minute Live Demo"
Cohesion: 0.19
Nodes (14): ManagerDesk, Arvind Chip Demo, Drive Video Plan, 15-Minute Live Demo, Manager Desk Demo, Meher Chip Demo, Priya Chip Demo, Arvind Scenario Slide (+6 more)

### Community 11 - "reset_session"
Cohesion: 0.12
Nodes (27): reset_session(), classify(), _is_assist_follow_up(), Classify turns that are not disruption entitlements. Disruption money still…, request_for(), slots_from(), IssueFamily, What kind of conversation this turn is, before a RequestType is chosen.… (+19 more)

### Community 12 - "Policy Engine"
Cohesion: 0.22
Nodes (9): pytest, Fail Closed on Unknown Benefits, Journey Compression, Limits and Tools, Passenger Forced to Become Policy Expert, UNDERSTAND GROUND DECIDE ACT ESCALATE AUDIT, Unknown ≠ Allowed, Policy Engine (+1 more)

### Community 13 - "types.ts"
Cohesion: 0.15
Nodes (13): api, ApiError, OPS_URL, StaffAuthResult, AuthResult, ChatMessage, ChatResponse, Conversation (+5 more)

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
Cohesion: 0.33
Nodes (6): ALLOW, ASK, DENY, ESCALATE, EscalationPacket, PolicyEngine

### Community 19 - "frontend/app/layout.tsx"
Cohesion: 0.40
Nodes (3): jakarta, metadata, viewport

### Community 27 - "PassengerKnowledgeStore"
Cohesion: 0.11
Nodes (8): PassengerKnowledgeStore, ABC, Booking, Optional durable delete. JSON product is in-memory only., Keep a passenger on this process without a password (Vercel isolate hop)., Map a PolicyDecision.source label back onto indexed rule ids., Nearest approved prior resolutions by embedding similarity. Reads `kb_entries`…, Product: passenger 360 / events / cases / graph. Clients never construct a…

### Community 28 - "ops.ts"
Cohesion: 0.05
Nodes (68): OperationsPage(), View, CaseBoard(), CaseCard(), COLUMNS, CaseDrawer(), StatusPill(), Donut() (+60 more)

### Community 39 - "AeroResolve — System Architecture & HLD"
Cohesion: 0.05
Nodes (40): 10. HTTP API, 11. Frontends, 12. Closed codes, 13. Auth, 14. Demo contracts this architecture must preserve, 1. Product thesis, 2.1 Design split, 2.2 System context (+32 more)

### Community 42 - "factories/__init__.py"
Cohesion: 0.12
Nodes (17): AuthFactory, Session tokens are a singleton product so login survives across requests., HasherFactory, OnboardingFactory, Staff sessions stay in process so operations login survives across requests., StaffFactory, CredentialHasher, ABC (+9 more)

### Community 43 - "evaluate_policy"
Cohesion: 0.11
Nodes (39): ExtractedRequest, delay_entitlements(), evaluate_policy(), PolicyDecision, Independent thresholds from the data pack. Does not invent amounts for >3h meal…, parametrize, Allowed and denied outcomes must not carry an escalation cause., Guards new handlers: an ESCALATE with no code would vanish from the breakdown. (+31 more)

### Community 44 - "knowledge/base.py"
Cohesion: 0.22
Nodes (14): load_fixtures(), load_help(), load_json(), load_policies(), load_scheduled_flights(), load_style_samples(), ScenarioFixture, _clauses() (+6 more)

### Community 45 - "LlmFactory"
Cohesion: 0.12
Nodes (23): is_thanks(), Facade — always goes through ReplyFactory., render_reply(), missing_slots(), parse_notes(), Any, LlmFactory, Clients request an LlmClient. They never read provider environment variables.… (+15 more)

### Community 46 - "closure.py"
Cohesion: 0.10
Nodes (34): already_asked_feedback(), asked_if_resolved(), asks_to_close_case(), confirms_resolution(), is_greeting(), last_assistant_text(), offered_supervisor(), parse_feedback() (+26 more)

### Community 47 - "llm_factory.py"
Cohesion: 0.10
Nodes (19): _dedupe(), _detect_provider(), disabled_config(), _fallback_models(), _float(), _int(), `model` first, then every sibling worth trying if it will not answer., Honour an explicit choice, else take the first provider holding a key. (+11 more)

### Community 48 - "test_frustration.py"
Cohesion: 0.18
Nodes (23): fresh_store(), observation(), Frustration is a signal, and these tests are what keep it one. Layered the same…, Operations draws the same graph_edges store, not a side table., test_a_calm_turn_is_contained_and_names_no_distress(), test_a_confident_observation_is_stored_and_aggregated(), test_a_low_confidence_observation_is_logged_but_excluded_from_primary_counts(), test_a_neutral_turn_records_the_event_but_claims_no_frustration() (+15 more)

### Community 49 - "inventory.py"
Cohesion: 0.24
Nodes (17): _as_suggested(), _date_matches(), _href(), _norm(), Any, _random_flight(), Look-only departures for booking assist. Scheduled rows come from the upcoming…, Look-only match after the passenger named a route. No guesswork before that. (+9 more)

### Community 50 - "loop.py"
Cohesion: 0.14
Nodes (23): CSAT is a post-close popup, not a card that closes the case., should_show_feedback_popup(), _deterministic_turn(), _finish(), _frustration_trace(), get_session(), _identify(), _issue_label() (+15 more)

### Community 51 - "InMemoryTokenSession"
Cohesion: 0.15
Nodes (16): InMemoryTokenSession, Signed tokens — no process-local map, so Vercel isolates can share a login., HMAC tokens that any process can verify. In-memory maps die on a Vercel…, Passenger claims, or `{id}` for the first signed tokens that carried only an id., read_claims(), _secret(), sign(), sign_claims() (+8 more)

### Community 52 - "test_context.py"
Cohesion: 0.17
Nodes (25): assemble(), context_contains_forbidden(), _disruption(), _facts(), packet_for_ui(), Booking, Code-side gate: other passengers, raw policy bodies, and history-as-benefit., render_respond_prompt() (+17 more)

### Community 53 - "PickySdk"
Cohesion: 0.10
Nodes (28): chained(), models_tried(), PickySdk, Serves only the models it was given a quota for; the rest raise 429. This is…, A model that returns nothing is as useless as one that errors., One timeout per model would be the whole chain's wait for the passenger., Free-tier quota lasts hours, so re-leading with it would waste the walk., Demoted, never retired: quota comes back and the preferred model resumes. (+20 more)

### Community 54 - "handle_chat"
Cohesion: 0.11
Nodes (32): handle_chat(), Structured 1–5 rating from the chat UI. Same close rules as a spoken rating., submit_feedback(), test_no_key_is_honest_fallback_not_a_live_llm(), _case(), Priya's unknown_entitlement stays escalated after 'that's fine' + 5★., test_booking_assist_does_not_append_a_resolved_survey(), test_card_feedback_endpoint_closes_when_rating_is_good() (+24 more)

### Community 55 - "LlmBudget"
Cohesion: 0.06
Nodes (27): LlmBudget, Which model actually answered. The chain means it may not be the first., Every ceiling that stops a runaway bill, plus an extraction cache. A breach is…, Name the breached ceiling, or None to proceed. Records nothing — the caller…, Record a degradation the client hit rather than a ceiling, e.g. a timeout., Start metering one conversational turn, so its cost can be reported. Day totals…, LlmClient, LlmResult (+19 more)

### Community 56 - "sign-in.tsx"
Cohesion: 0.25
Nodes (10): BrandMark(), Wordmark(), InlineCard(), Mode, SignIn(), Field(), Input, resolveOpsUrl() (+2 more)

### Community 57 - "cards.tsx"
Cohesion: 0.14
Nodes (24): AgentCards(), ChoiceCard(), ConfirmationCard(), Thread(), TypingIndicator(), CHOICE_STATUSES, choiceDecisions(), newActions() (+16 more)

### Community 58 - "Any"
Cohesion: 0.14
Nodes (6): Any, What the customer UI should show: this passenger's transcript, nobody else's., The live passenger knowledge base, as a graph Operations can draw. Dedupes…, Lightweight dashboard numbers. Policy is not computed here., How much of the work needed no human, and where authority ran out. Only turns…, _seconds_between()

### Community 59 - "test_agent.py"
Cohesion: 0.29
Nodes (6): _args(), LLM agent loop: the model orchestrates, tools enforce policy., Returns a sequence of chat.completions payloads, including tool calls., ScriptedSdk, test_agent_calls_booking_then_policy_then_answers(), test_live_agent_path_records_tool_calls()

### Community 60 - "schemas.py"
Cohesion: 0.11
Nodes (25): Booking, BookingIntake, ChatResponse, Customer, KbHit, One approved prior resolution, ranked by embedding cosine., Look-only departure shown during booking assist. Never a ticket., SignupRequest (+17 more)

### Community 61 - "exit-board.tsx"
Cohesion: 0.22
Nodes (8): metadata, BookingCard(), SuggestedFlightCard(), clockLabel(), ExitBoard(), FALLBACK_FLIGHTS, flightStatusCopy(), SuggestedFlight

### Community 62 - "store.ts"
Cohesion: 0.24
Nodes (16): LoginPage(), ResolvePage(), useReady(), greeting(), messageFor(), newSessionId(), openConversation(), Persisted (+8 more)

### Community 63 - "client_with"
Cohesion: 0.08
Nodes (51): LlmPolishedReplyRenderer, Phrasing only. The template reply is already policy-approved, and every path…, test_agent_chat_sends_tools_to_the_model(), test_a_heuristic_pin_does_not_call_the_model(), test_classify_llm_asks_for_json_at_temperature_zero(), test_classify_llm_orders_signals_canonically_and_drops_unknowns(), test_classify_llm_returns_the_same_fields_as_classify(), client_with() (+43 more)

### Community 64 - "context-panel.tsx"
Cohesion: 0.32
Nodes (6): ContextPanel(), DecisionRow(), toneFor(), Badge(), Tone, TONES

### Community 65 - "PostgresKnowledgeStore"
Cohesion: 0.33
Nodes (5): _as_vector(), _json(), PostgresKnowledgeStore, Any, Concrete product: Postgres is the system of record, RAM is a cache. Seed…

### Community 66 - "AuthSession"
Cohesion: 0.12
Nodes (9): connect(), database_url(), Any, Thread-local psycopg connection. Schema is applied once per connection., PostgresTokenSession, Passenger login tokens survive a process restart when Postgres is up., AuthSession, ABC (+1 more)

### Community 67 - "tools.py"
Cohesion: 0.13
Nodes (22): case_status(), Sticky case state for this conversation. Executed actions never close it., remaining_offered(), should_prompt_feedback(), _case_status(), persist_assist(), Deterministic tools the LLM agent may invoke. The model chooses *when* to call…, FrustrationCategory (+14 more)

### Community 68 - "ElasticsearchKnowledgeStore"
Cohesion: 0.08
Nodes (15): KnownFact, One retrieved policy clause. Clause-level, never a whole rule body., RuleHit, StyleHit, TurnHit, ElasticsearchKnowledgeStore, Any, RuleHit (+7 more)

### Community 69 - ".create"
Cohesion: 0.26
Nodes (12): test_key_is_never_exposed_by_health(), main(), Ask the configured provider which models your key can actually serve. cd…, heading(), key_authenticates(), live_call(), live_turn(), main() (+4 more)

### Community 71 - "test_containment.py"
Cohesion: 0.14
Nodes (23): _percentile(), Nearest-rank percentile over a pre-sorted list., fresh_store(), measured_turn(), Containment: the metric that answers how much work needed no human. Two layers…, The two counters are independent slices, not a partition of turns., test_a_store_with_no_measured_turns_reports_zero_not_a_fake_rate(), test_a_waiver_above_the_limit_reports_itself_as_escalated() (+15 more)

### Community 72 - ".disabled"
Cohesion: 0.29
Nodes (6): A client that can never call out, for tests and for LLM_PROVIDER=none., test_classify_llm_falls_back_to_classify_when_the_model_is_silent(), Belt and braces: prove the None above is not a swallowed network error., test_disabled_client_never_builds_an_sdk(), test_disabled_client_raises_if_it_ever_tried_to_call_out(), test_falling_back_cannot_be_reached_by_a_disabled_client()

### Community 73 - "test_llm.py"
Cohesion: 0.12
Nodes (26): from_env(), Provider resolution, spend ceilings, and graceful degradation. Nothing here…, Anyone who pointed OPENAI_* at Gemini before this layer existed keeps working., One key covers every Gemini model, so quota on one is not quota on all., Family names mean nothing at someone else's endpoint, so none are assumed., An unpriced entry would be billed at the conservative default silently., An alias points at whatever the provider currently serves, so no rate can be…, Behind a proxy we cannot know what is listening, so send nothing extra. (+18 more)

### Community 74 - "main.py"
Cohesion: 0.08
Nodes (52): add_my_booking(), analytics(), approve_kb(), approve_pending_kb(), assess(), case(), cases(), chat() (+44 more)

### Community 75 - "should_escalate"
Cohesion: 0.24
Nodes (10): Both gates, or neither. A hostile guess is not a reason to fetch a human., should_escalate(), parametrize, No sampling, no clock, no model. CI must not need a retry., A confident read of mild annoyance is not a reason to fetch a human., test_escalation_does_not_fire_below_the_category_threshold(), test_escalation_does_not_fire_below_the_confidence_threshold(), test_escalation_fires_above_both_thresholds() (+2 more)

### Community 76 - "SessionMemory"
Cohesion: 0.14
Nodes (24): render_extract_prompt(), expand_scope(), plan_retrieval(), Booking, _query(), Classify the turn into the retrievers it needs, before any fetching happens., Widen the citable scope using facts only known after the booking is loaded. A…, Execute a retrieval plan. Facade — always goes through the knowledge store. (+16 more)

### Community 77 - ".frustration"
Cohesion: 0.25
Nodes (6): _category_counts(), Counts in severity order, and only for categories actually observed. Fixed key…, How distressed the traffic was, and whether distress cost containment. Low-…, Did high frustration correlate with needing a human? Keyed on the…, Aggregate the EXHIBITS_FRUSTRATION edges themselves. Read from `graph_edges`…, _tally()

### Community 78 - "test_kb_match.py"
Cohesion: 0.16
Nodes (18): ground_prior_resolution(), Reuse a prior resolution's phrasing, or queue the turn for ops approval. Runs…, Embed this turn, reuse a close prior phrasing, or queue a pending row., Remove amounts, PNRs, and flight numbers from a tone sample., strip_style_identifiers(), FrustrationAssessment, KbMatch, Any (+10 more)

### Community 79 - "ToolRuntime"
Cohesion: 0.07
Nodes (36): _assistant_tools(), _history(), _invented_money(), LLM-as-orchestrator loop. The model decides which tools to call. Tools enforce…, run_llm_agent(), _system_for(), _accepted(), _collect_money() (+28 more)

### Community 80 - "._persist"
Cohesion: 0.15
Nodes (4): Optional dual-write. JSON product is in-memory only., Park an unseen phrasing for ops. Does not embed or index., Supervisor decision on one pending observation. Same event row, no new index., Write the passenger's live conversation so the next login can restore it.

### Community 81 - "chat-shell.tsx"
Cohesion: 0.14
Nodes (17): ChatShell(), Composer(), FeedbackPopup(), ChatHeader(), QuickReplies(), Button, ButtonProps, Size (+9 more)

### Community 82 - "LlmExtractor"
Cohesion: 0.10
Nodes (19): ExtractorFactory, Clients request an IntentExtractor. They never construct concrete extractors., LlmExtractor, Optional NLU. Both the fallback extractor and the client are injected., test_extractor_factory_returns_product_interface(), clean_env(), ExplodingSdk, fixture (+11 more)

### Community 83 - "JsonKnowledgeStore"
Cohesion: 0.06
Nodes (31): EmbeddingClient, Built once, on first use. Disabled clients never construct one., The single place this codebase talks to an embedding model. OpenAI `text-…, A client that can never call out, for tests and for EMBEDDING_PROVIDER=none., One 1536-d vector, or None when this client must not call out., EmbeddingFactory, Clients request an EmbeddingClient. They never read provider environment…, A client that can never call out, for tests and for EMBEDDING_PROVIDER=none. (+23 more)

### Community 84 - "AeroResolve"
Cohesion: 0.29
Nodes (8): FastAPI, Uvicorn, AIONOS-Style Constraint, Context-First Loop, Architecture Slide, AeroResolve, Model Talks, Deterministic Code Decides, Product Thesis

### Community 86 - "score"
Cohesion: 0.22
Nodes (6): RuleHit, cosine(), Length-normalized term overlap. Dependency-free on purpose: the JSON backend…, Cosine similarity of two embedding vectors. 0.0 when either side is empty., score(), tokenize()

### Community 87 - "test_retrieval.py"
Cohesion: 0.17
Nodes (19): narrate(), Render the decided packet as prose with clause-level citations. Every line is…, Build one turn's plan, evaluation, retrieval, and context outside the API., The demo's citations cannot depend on which store is wired., _StubEsStore, test_citations_stay_inside_the_plan_scope(), test_cited_rules_are_exactly_the_ones_retrieval_returned(), test_elasticsearch_backend_parses_query_hits() (+11 more)

### Community 88 - "test_scenarios.py"
Cohesion: 0.28
Nodes (8): Duty-of-care and the upgrade authority limit are independent codes., Legal detection must not gate distress; the engine still adds the upgrade., _reset_priya(), test_arvind_scenario_chat(), test_meher_scenario_chat(), test_priya_distress_and_unknown_entitlement_are_both_on_the_case(), test_priya_legal_distress_and_upgrade_stack_three_distinct_reasons(), test_priya_scenario_chat()

### Community 89 - "ElasticsearchOrJSON"
Cohesion: 0.22
Nodes (10): elasticsearch Python Client, Elasticsearch Service, Conversation Graph Edges, CustomerMessage, ElasticsearchOrJSON, Knowledge Base Indices, RetrieveThisPassengerOnly, Optional Elasticsearch Knowledge Base (+2 more)

### Community 90 - "test_loop_calls_classify_llm_when_the_client_is_live"
Cohesion: 0.33
Nodes (4): Same import-time getenv as KB_AUTO_STORE_THRESHOLD, so tests can pin it., The same live-client test as agent_mode, not a third branch., test_frustration_classifier_is_read_from_the_environment_like_the_store_threshold(), test_loop_calls_classify_llm_when_the_client_is_live()

### Community 91 - "detect_emotion"
Cohesion: 0.67
Nodes (3): detect_emotion(), The existing tone axis: angry / frustrated / confused, or nothing. Kept…, test_fuck_is_profanity_and_not_neutral()

### Community 94 - "classify"
Cohesion: 0.14
Nodes (14): _category(), classify(), _confidence(), Assess one turn. Deterministic, offline, and safe to call every turn., `low_confidence` and `source` are for the store, not the prompt., A stranded passenger with a child is a care case, not an angry one., Repetition means the previous answer did not land, whatever words were used., test_a_calm_question_is_neutral_with_no_signals() (+6 more)

## Knowledge Gaps
- **202 isolated node(s):** `inter`, `metadata`, `View`, `COLUMNS`, `Series` (+197 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **11 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `SessionMemory` connect `SessionMemory` to `frustration.py`, `reset_session`, `LlmFactory`, `closure.py`, `test_frustration.py`, `loop.py`, `test_context.py`, `PickySdk`, `handle_chat`, `test_agent.py`, `schemas.py`, `client_with`, `tools.py`, `ElasticsearchKnowledgeStore`, `.disabled`, `test_llm.py`, `should_escalate`, `test_kb_match.py`, `ToolRuntime`, `LlmExtractor`, `test_retrieval.py`, `detect_emotion`, `classify`?**
  _High betweenness centrality (0.050) - this node is a cross-community bridge._
- **Why does `PassengerKnowledgeStore` connect `PassengerKnowledgeStore` to `PostgresKnowledgeStore`, `tools.py`, `ElasticsearchKnowledgeStore`, `.pending_kb`, `test_factories.py`, `factories/__init__.py`, `knowledge/base.py`, `.frustration`, `test_kb_match.py`, `.append_frustration`, `._persist`, `JsonKnowledgeStore`, `.approve_pending_kb_entry`, `score`, `Any`, `schemas.py`?**
  _High betweenness centrality (0.043) - this node is a cross-community bridge._
- **Why does `JsonKnowledgeStore` connect `JsonKnowledgeStore` to `PostgresKnowledgeStore`, `ElasticsearchKnowledgeStore`, `test_containment.py`, `test_factories.py`, `test_kb_match.py`, `test_frustration.py`, `test_retrieval.py`, `test_scenarios.py`, `PassengerKnowledgeStore`?**
  _High betweenness centrality (0.038) - this node is a cross-community bridge._
- **Are the 11 inferred relationships involving `SessionMemory` (e.g. with `ToolRuntime` and `IntentExtractor`) actually correct?**
  _`SessionMemory` has 11 INFERRED edges - model-reasoned connections that need verification._
- **Are the 12 inferred relationships involving `PassengerKnowledgeStore` (e.g. with `EmbeddingFactory` and `HasherFactory`) actually correct?**
  _`PassengerKnowledgeStore` has 12 INFERRED edges - model-reasoned connections that need verification._
- **Are the 13 inferred relationships involving `StubSdk` (e.g. with `ExtractorFactory` and `LlmFactory`) actually correct?**
  _`StubSdk` has 13 INFERRED edges - model-reasoned connections that need verification._
- **What connects `inter`, `metadata`, `View` to the rest of the system?**
  _202 weakly-connected nodes found - possible documentation gaps or missing edges._
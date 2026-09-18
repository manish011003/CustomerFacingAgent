# Graph Report - Assesment_project_Custormer-Facing_Resolution_Agent_AIONOS  (2026-09-18)

## Corpus Check
- 111 files · ~24,503 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 782 nodes · 1982 edges · 48 communities (40 shown, 8 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 193 edges (avg confidence: 0.58)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `3cf40d58`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- PolicyDecision
- test_retrieval.py
- index.ts
- devDependencies
- devDependencies
- compilerOptions
- compilerOptions
- main.py
- test_factories.py
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
- schemas.py
- factories/__init__.py
- LlmConfig
- test_llm.py
- StubSdk
- LlmBudget
- LlmClient
- .disabled

## God Nodes (most connected - your core abstractions)
1. `PassengerKnowledgeStore` - 51 edges
2. `PolicyDecision` - 42 edges
3. `SessionMemory` - 36 edges
4. `evaluate_policy()` - 33 edges
5. `Customer` - 32 edges
6. `PolicyHandler` - 30 edges
7. `Booking` - 29 edges
8. `LlmClient` - 28 edges
9. `DecisionStatus` - 27 edges
10. `StubSdk` - 27 edges

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

## Communities (48 total, 8 thin omitted)

### Community 0 - "PolicyDecision"
Cohesion: 0.11
Nodes (45): PolicyHandlerFactory, Maps a request type to a PolicyHandler. Engine never constructs handlers itself., simulate(), DecisionStatus, ExtractedRequest, PolicyDecision, PolicyEvaluation, RequestType (+37 more)

### Community 1 - "test_retrieval.py"
Cohesion: 0.06
Nodes (70): assemble(), context_contains_forbidden(), _disruption(), narrate(), packet_for_ui(), Render the decided packet as prose with clause-level citations. Every line is…, render_extract_prompt(), render_respond_prompt() (+62 more)

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
Cohesion: 0.13
Nodes (29): reset_session(), add_my_booking(), analytics(), assess(), case(), cases(), chat(), _eligibility() (+21 more)

### Community 8 - "test_factories.py"
Cohesion: 0.12
Nodes (20): Facade — always goes through ReplyFactory., render_reply(), KnowledgeStoreFactory, Clients request a PassengerKnowledgeStore. They never construct JSON or…, ReplyFactory, CustomerAgentContext, JsonKnowledgeStore, Concrete product: in-memory passenger KB seeded from the assignment JSON pack. (+12 more)

### Community 9 - "LlmFactory"
Cohesion: 0.15
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

### Community 27 - "schemas.py"
Cohesion: 0.05
Nodes (35): _facts(), Booking, BookingIntake, ChatRequest, ChatResponse, Customer, KnownFact, LoginRequest (+27 more)

### Community 28 - "factories/__init__.py"
Cohesion: 0.11
Nodes (12): AuthFactory, Session tokens are a singleton product so login survives across requests., HasherFactory, OnboardingFactory, CredentialHasher, ABC, Product: hash and verify passenger passwords. Clients never pick an algorithm., InMemoryTokenSession (+4 more)

### Community 42 - "LlmConfig"
Cohesion: 0.16
Nodes (12): LlmResult, disabled_config(), _float(), _int(), LlmConfig, Resolved provider settings plus every ceiling that bounds spend., Enough to confirm which key loaded, never enough to use it., No provider, no model, no ceilings that could ever be consulted. (+4 more)

### Community 43 - "test_llm.py"
Cohesion: 0.15
Nodes (18): _detect_provider(), from_env(), Honour an explicit choice, else take the first provider holding a key., clean_env(), Provider resolution, spend ceilings, and graceful degradation. Nothing here…, Anyone who pointed OPENAI_* at Gemini before this layer existed keeps working., No developer's real key leaks into a test run., test_auto_prefers_the_free_tier_when_several_keys_exist() (+10 more)

### Community 44 - "StubSdk"
Cohesion: 0.21
Nodes (14): client_with(), config(), Regression: the original renderer sent no max_tokens at all., Records every request and answers with canned text., StubSdk, test_cache_does_not_confuse_different_utterances(), test_daily_usd_ceiling_stops_further_calls(), test_empty_response_is_treated_as_a_degradation() (+6 more)

### Community 45 - "LlmBudget"
Cohesion: 0.22
Nodes (4): LlmBudget, Every ceiling that stops a runaway bill, plus an extraction cache. A breach is…, Return the name of the breached ceiling, or None to proceed., Record a degradation the client hit rather than a ceiling, e.g. a timeout.

### Community 46 - "LlmClient"
Cohesion: 0.20
Nodes (5): LlmClient, Provider state without leaking the key. `probe` costs one cheap call., The single place this codebase talks to a model. `complete` returns None…, Built once, on first use. Disabled providers never construct one., test_key_is_never_exposed_by_health()

### Community 47 - ".disabled"
Cohesion: 0.40
Nodes (4): A client that can never call out, for tests and for LLM_PROVIDER=none., Belt and braces: prove the None above is not a swallowed network error., test_disabled_client_never_builds_an_sdk(), test_disabled_client_raises_if_it_ever_tried_to_call_out()

## Knowledge Gaps
- **123 isolated node(s):** `factory`, `factory`, `Passenger`, `inter`, `metadata` (+118 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **8 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `PassengerKnowledgeStore` connect `schemas.py` to `test_factories.py`, `factories/__init__.py`?**
  _High betweenness centrality (0.042) - this node is a cross-community bridge._
- **Why does `SessionMemory` connect `test_retrieval.py` to `test_factories.py`, `LlmFactory`, `test_llm.py`, `StubSdk`, `schemas.py`?**
  _High betweenness centrality (0.026) - this node is a cross-community bridge._
- **Why does `RequestType` connect `PolicyDecision` to `test_retrieval.py`, `main.py`, `test_factories.py`, `LlmFactory`, `test_llm.py`, `StubSdk`, `schemas.py`?**
  _High betweenness centrality (0.023) - this node is a cross-community bridge._
- **Are the 9 inferred relationships involving `PassengerKnowledgeStore` (e.g. with `HasherFactory` and `Booking`) actually correct?**
  _`PassengerKnowledgeStore` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Are the 14 inferred relationships involving `PolicyDecision` (e.g. with `RebookHandler` and `RefundOriginalHandler`) actually correct?**
  _`PolicyDecision` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `SessionMemory` (e.g. with `IntentExtractor` and `LlmExtractor`) actually correct?**
  _`SessionMemory` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `Customer` (e.g. with `PolicyHandler` and `StatusHandler`) actually correct?**
  _`Customer` has 5 INFERRED edges - model-reasoned connections that need verification._
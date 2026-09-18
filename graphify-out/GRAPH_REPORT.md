# Graph Report - Assesment_project_Custormer-Facing_Resolution_Agent_AIONOS  (2026-09-18)

## Corpus Check
- 103 files · ~20,808 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 665 nodes · 1634 edges · 42 communities (34 shown, 8 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 156 edges (avg confidence: 0.59)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- PolicyDecision
- schemas.py
- index.ts
- devDependencies
- devDependencies
- compilerOptions
- compilerOptions
- main.py
- CustomerAgentContext
- evaluate_policy
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
- test_factories.py

## God Nodes (most connected - your core abstractions)
1. `PassengerKnowledgeStore` - 51 edges
2. `PolicyDecision` - 42 edges
3. `Customer` - 32 edges
4. `evaluate_policy()` - 31 edges
5. `SessionMemory` - 30 edges
6. `PolicyHandler` - 30 edges
7. `Booking` - 29 edges
8. `DecisionStatus` - 27 edges
9. `assemble()` - 23 edges
10. `ExtractedRequest` - 22 edges

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

## Communities (42 total, 8 thin omitted)

### Community 0 - "PolicyDecision"
Cohesion: 0.17
Nodes (24): PolicyHandlerFactory, Maps a request type to a PolicyHandler. Engine never constructs handlers itself., DecisionStatus, PolicyDecision, PolicyEvaluation, baseline_for_booking(), PolicyHandler, ABC (+16 more)

### Community 1 - "schemas.py"
Cohesion: 0.05
Nodes (77): assemble(), context_contains_forbidden(), _disruption(), narrate(), packet_for_ui(), Render the decided packet as prose with clause-level citations. Every line is…, render_extract_prompt(), render_respond_prompt() (+69 more)

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
Cohesion: 0.08
Nodes (40): _facts(), reset_session(), add_my_booking(), analytics(), assess(), case(), cases(), chat() (+32 more)

### Community 8 - "CustomerAgentContext"
Cohesion: 0.24
Nodes (10): Facade — always goes through ReplyFactory., render_reply(), ReplyFactory, CustomerAgentContext, ABC, ReplyRenderer, LlmPolishedReplyRenderer, _line() (+2 more)

### Community 9 - "evaluate_policy"
Cohesion: 0.28
Nodes (18): simulate(), ExtractedRequest, delay_entitlements(), evaluate_policy(), Independent thresholds from the data pack. Does not invent amounts for >3h meal…, _people(), test_airline_cancellation_refund_or_rebook(), test_arvind_hotel_denied() (+10 more)

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
Cohesion: 0.07
Nodes (18): KnownFact, One retrieved policy clause. Clause-level, never a whole rule body., RuleHit, StyleHit, TurnHit, PassengerKnowledgeStore, ABC, Any (+10 more)

### Community 28 - "test_factories.py"
Cohesion: 0.08
Nodes (21): AuthFactory, Session tokens are a singleton product so login survives across requests., HasherFactory, KnowledgeStoreFactory, Clients request a PassengerKnowledgeStore. They never construct JSON or…, OnboardingFactory, CredentialHasher, ABC (+13 more)

## Knowledge Gaps
- **123 isolated node(s):** `factory`, `factory`, `Passenger`, `inter`, `metadata` (+118 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **8 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `PassengerKnowledgeStore` connect `PassengerKnowledgeStore` to `schemas.py`, `test_factories.py`, `main.py`?**
  _High betweenness centrality (0.047) - this node is a cross-community bridge._
- **Why does `Customer` connect `main.py` to `PolicyDecision`, `schemas.py`, `PassengerKnowledgeStore`, `evaluate_policy`?**
  _High betweenness centrality (0.022) - this node is a cross-community bridge._
- **Why does `evaluate_policy()` connect `evaluate_policy` to `PolicyDecision`, `schemas.py`, `main.py`?**
  _High betweenness centrality (0.019) - this node is a cross-community bridge._
- **Are the 9 inferred relationships involving `PassengerKnowledgeStore` (e.g. with `HasherFactory` and `Booking`) actually correct?**
  _`PassengerKnowledgeStore` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Are the 14 inferred relationships involving `PolicyDecision` (e.g. with `RebookHandler` and `RefundOriginalHandler`) actually correct?**
  _`PolicyDecision` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `Customer` (e.g. with `PolicyHandler` and `StatusHandler`) actually correct?**
  _`Customer` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `SessionMemory` (e.g. with `IntentExtractor` and `LlmExtractor`) actually correct?**
  _`SessionMemory` has 5 INFERRED edges - model-reasoned connections that need verification._
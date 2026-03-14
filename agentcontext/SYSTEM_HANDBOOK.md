# System Handbook: Databricks Ontology Copilot

This document serves as the primary technical reference for the Databricks Ontology Copilot, explaining what it is, how it works, and its current implementation status.

---

## 1. System Overview

The Databricks Ontology Copilot is an AI-powered tool designed to automate "schema archaeology." It reads Databricks metadata, constructs a semantic knowledge graph (ontology), and provides a natural language interface for discovering relevant data assets for ML tasks.

### Core Value Proposition
- **Automated Discovery**: Replaces manual tracing of joins and schema reading.
- **Natural Language Querying**: Asks questions like "What data should I use to predict customer churn?"
- **Grounded Recommendations**: Provides target/feature suggestions with join keys and auto-generated SQL scaffolds.

---

## 2. Technical Architecture

The system uses an **LLM-based graph traversal** pipeline. Unlike traditional programmatic traversal, the entire ontology is passed to the LLM (GPT-4o or Llama 3.1) as context, leveraging its native reasoning capabilities.

### The Agent Pipeline
1. **User Query**: Collected via Streamlit interface.
2. **Context Assembly**: The full `ontology_graph.json` is serialized and injected into the LLM system prompt.
3. **LLM Traversal**: The LLM analyzes the graph nodes (tables) and edges (joins) to identify paths relevant to the user's intent.
4. **Structured Output**: The LLM returns a JSON object containing:
   - `target`: The recommended label table and column.
   - `features`: A list of feature tables with join keys and confidence scores.
   - `gaps`: Any limitations or missing data.
5. **UI Rendering**: Streamlit renders the recommendation and generates a SQL scaffold.

### Implementation Details
- **Frontend**: Streamlit with custom Databricks-themed CSS.
- **Graph Visualization**: `streamlit-agraph` for interactive, color-coded node/edge displays.
- **Graph Model**: NetworkX is used for backend graph storage and utility operations.
- **LLM Engine**: OpenAI GPT-4o (primary) or NVIDIA NIM Llama 3.1 405B (alternative).

---

## 3. Implementation Status

The system is fully implemented as of v2.0.0, matching the original PRD specifications and adding significant enhancements.

### Recent Milestones (v2.0.0)
- **Advanced Testing**: Expanded to 52 tests with 100% success rate on core functionality.
- **Multi-Provider Support**: Seamlessly switch between OpenAI and NVIDIA NIM (Llama 3.1 405B).
- **Professional UX**: Implemented custom Databricks branding and interactive UI elements.
- **Production Infrastructure**: Added automated setup, test runners, and data swap utilities.

### Feature Matrix
| Feature | Status | Notes |
| :--- | :--- | :--- |
| **Graph Visualization** | ✅ Complete | Interactive, color-coded, physics-enabled. |
| **Agent Query UI** | ✅ Complete | Natural language input + button trigger. |
| **LLM Reasoning** | ✅ Complete | Deterministic (temp=0.0) graph traversal. |
| **SQL Scaffolding** | ✅ Bonus | Auto-generates JOIN queries from results. |
| **Demo Mode** | ✅ Bonus | Cached responses for no-internet/key scenarios. |
| **Multi-Provider API**| ✅ Bonus | Supports OpenAI and NVIDIA NIM. |
| **Security/Validation**| ✅ Complete | Hallucination tests ensure only real assets are cited. |
| **Test Automation** | ✅ Complete | Sequentially runs 50+ tests via `run_all_tests.sh`. |

---

## 4. Key Components

- `app/app.py`: The heart of the application, containing UI and agent logic.
- `app/ontology_graph.json`: The semantic graph consumed by the agent.
- `app/swap_graph_data.py`: Utility for integrating new production data from P1.
- `agentcontext/PRD.md`: Original requirement specification.
- `agentcontext/OPERATIONS_PLAYBOOK.md`: Instructions for setup, integration, and testing.

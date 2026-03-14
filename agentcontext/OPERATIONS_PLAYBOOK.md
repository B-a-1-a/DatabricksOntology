# Operations Playbook: Databricks Ontology Copilot

This document provides actionable procedures for setting up, integrating, and testing the system, with a focus on the P1 data workflow.

---

## 🚀 30-Second Quick Start

```bash
# 1. Navigate and Activate
cd ~/DatabricksOntology/app
source ../venv/bin/activate

# 2. Set API Key (Optional- demo mode works without)
export OPENAI_API_KEY='sk-...' # OR NVIDIA_API_KEY='nvapi-...'

# 3. Test and Run
python test_integration.py
streamlit run app.py
```
*App opens at: http://localhost:8501*

---

## 1. P1 Workflow: Data Preparation

The "Person 1" (P1) workflow is responsible for pulling real Databricks metadata and transforming it into the ontology consumed by the agent.

### Process Steps
1. **Metadata Ingestion**:
   - Uses the Databricks SDK to connect to the workspace.
   - Lists all tables in the target catalog/schema.
   - Saves table/column details to `ontology_metadata.json`.
2. **Ontology Construction**:
   - Pass `ontology_metadata.json` to an LLM with specific semantic classification rules.
   - Classify nodes (feature, label, entity, lookup).
   - Infer edges (joins) based on shared keys.
   - Save the result to `ontology_graph.json`.

### Technical Specs
- **Script**: `ingest_metadata.py` (Ingestion) and `construct_ontology.py` (Construction).
- **Authentication**: Uses `databricks-sdk` with configured profiles (e.g., 'Akshat Vasisht').
- **LLM Prompting**: Uses `gpt-4o` with `json_object` mode and `temperature=0.0`.

---

## 2. P1 Integration & Data Swap

When new ontology data is delivered, use the following steps to update the application safely.

### Quick Integration Steps
1. **Validate JSON Syntax**:
   ```bash
   python -m json.tool <p1_graph.json> > /dev/null && echo "✅ Valid JSON"
   ```
2. **Run Data Swap**:
   ```bash
   cd app
   python swap_graph_data.py <p1_graph.json>
   # Review the summary and confirm. This script validates schema and creates backups.
   ```
3. **Restart App**:
   ```bash
   pkill -f streamlit
   streamlit run app.py
   ```

---

## 3. End-to-End Testing Guide

Run these tests after every data swap to ensure system integrity.

### Critical Tests
- **Visual Verification**: Ensure the graph renders with correct node colors and edge labels.
- **Agent Hallucination Test**:
  ```bash
  python test_integration.py
  ```
  **CRITICAL**: The `no_hallucinations` test must pass. It verifies the agent only recommends tables and columns that exist in the provided graph.
- **SQL Validation**: Copy the SQL scaffold from the UI and verify it uses real table names and valid JOIN syntax.

### Manual Querying
Test the system with actual target outcomes from the production data:
- *"What data should I use to predict [target_column]?"*
- *"Which tables contain features for [entity_key]?"*

---

## 4. Troubleshooting

| Issue | Likely Cause | Fix |
| :--- | :--- | :--- |
| **Streamlit: command not found** | venv not active. | Run `source ../venv/bin/activate`. |
| **Graph won't render** | Malformed JSON. | Validate with `python -m json.tool`. |
| **Agent Hallucinations** | Temperature > 0 or weak prompt. | Verify `temperature=0.0` and system prompt constraints in `app.py`. |
| **API Key Missing** | Environment variable not set. | Run `export OPENAI_API_KEY='sk-...'`. |
| **Hallucination Test Fails** | Inconsistent node/edge IDs. | Check for unique `id` fields in `ontology_graph.json`. |

# PRD — Hackathon Build
## Databricks Ontology Copilot
### 2:00 PM – 5:00 PM, March 14 2026

**Team:** 3 developers, all using Claude Code (Antigravity)  
**Dev window:** 3 hours (2:00–5:00 PM)  
**Pitch:** 5:00 PM, 1 minute  
**Buffer assumption:** 15 min misc absorbed — clean start at 2:00 PM

---

## Stack

| Layer | Tool | Notes |
|-------|------|-------|
| UI | Streamlit | One command, no frontend code |
| Graph visualization | streamlit-agraph | Native Streamlit, clickable nodes, no HTML hacks |
| Graph visualization fallback | yfiles-graphs-for-streamlit | Drop-in if agraph looks rough |
| Graph model | NetworkX | Backend computation, feeds directly into agraph |
| LLM | OpenAI gpt-4o | $200 account, keys ready, json_object mode = no parse errors |
| Databricks connectivity | databricks-sdk | Already installed and authenticated |

```bash
pip install streamlit streamlit-agraph networkx openai databricks-sdk
export OPENAI_API_KEY="sk-..."
```

---

## The One Thing That Must Work

> User asks: *"What data should I use to predict [target outcome]?"*
> System returns: target column, feature table, join key, explanation.
> Graph is visible behind it.

Everything in this document exists to make that moment happen by 4:15 PM.

**Note:** The specific dataset/catalog/schema will be provided by P1. All examples below are illustrative only.

---

## Scope (What Gets Built)

| Component | Spec | Owner | Done by |
|-----------|------|-------|---------|
| Metadata ingestion | SDK pulls catalog/schema/table/column from **TBD benchmark dataset** → flat JSON | P1 | 2:30 PM |
| Ontology construction | Single OpenAI API call over metadata JSON → node/edge graph JSON | P1 | 3:00 PM |
| Graph visualization | `streamlit-agraph` native component. Color by node type. Clickable nodes. | P2 | 3:15 PM |
| Agent query UI | Text input + OpenAI API call with graph as context → structured recommendation panel | P3 | 3:15 PM |
| Integration | P2 + P3 swap stubs for real graph JSON | All | 3:30 PM |
| Polish + demo prep | Labels, colors, backup screenshots, pitch rehearsal | All | 4:15 PM |
| Buffer | Bug fixes, rehearsal, hard stop | All | 5:00 PM |

---

## What Is Cut

No auth UI. No search/filter sidebar. No confidence sliders. No SQL scaffold output. No multi-catalog support. No scheduled refresh. No database backend. No React. No lineage. No multi-page Streamlit.

One page. One query. One graph. One recommendation.

---

## Stub Contract — Agree Before 2:00 PM

P2 and P3 build against this JSON from minute one. P1 replaces it with the real graph by 3:00 PM. **The schema does not change after 2:00 PM.**

```json
{
  "nodes": [
    {
      "id": "example_features_daily",
      "type": "feature_table",
      "entity_key": "entity_id",
      "candidate_features": ["metric_a","metric_b","metric_c","aggregate_value"]
    },
    {
      "id": "example_labels",
      "type": "label_table",
      "entity_key": "entity_id",
      "candidate_targets": ["target_outcome"]
    },
    {
      "id": "example_entity_master",
      "type": "entity_master",
      "entity_key": "entity_id",
      "attributes": ["category","region","created_date"]
    },
    {
      "id": "example_derived_features",
      "type": "feature_table",
      "entity_key": "entity_id",
      "candidate_features": ["computed_metric_x","computed_metric_y"]
    }
  ],
  "edges": [
    {"source": "example_features_daily", "target": "example_labels",
     "relationship": "joinable_on", "key": "entity_id", "confidence": "high"},
    {"source": "example_entity_master", "target": "example_features_daily",
     "relationship": "entity_of", "key": "entity_id", "confidence": "high"},
    {"source": "example_entity_master", "target": "example_labels",
     "relationship": "entity_of", "key": "entity_id", "confidence": "high"},
    {"source": "example_derived_features", "target": "example_labels",
     "relationship": "joinable_on", "key": "entity_id", "confidence": "medium"}
  ]
}
```

---

## Person 1 — Ingestion + Ontology

**Claude Code prompt to paste at 2:00 PM:**

```
Using the Databricks SDK with profile 'Akshat Vasisht', do the following:

1. Connect to the workspace at https://dbc-bc2a5dd3-798c.cloud.databricks.com
2. List all tables in the **benchmark dataset** (catalog/schema TBD - coordinate with team)
3. For each table, pull: table name, table comment, all column names,
   column data types, column comments
4. Output as a flat JSON list saved to ontology_metadata.json

Then make a single OpenAI API call with all that metadata as context.
Use model gpt-4o with response_format={"type": "json_object"} to guarantee
valid JSON output. Instruct the model to output ONLY valid JSON matching this exact schema:
{
  "nodes": [{"id": str, "type": str, "entity_key": str,
              "candidate_features": list, "candidate_targets": list}],
  "edges": [{"source": str, "target": str, "relationship": str,
              "key": str, "confidence": str}]
}

Node type must be one of: feature_table, label_table, entity_master, lookup.
Confidence must be one of: high, medium, low.
Only include edges where a shared key column (ending in _id or _key) exists.
Save output to ontology_graph.json.
```

**Fallback:** If SDK ingestion fails, hardcode the stub JSON above as `ontology_graph.json` and proceed. Do not spend more than 20 minutes debugging ingestion.

---

## Person 2 — Graph Visualization

**Claude Code prompt to paste at 2:00 PM:**

```
Build a Streamlit app (app.py) that does the following:

1. Load ontology_graph.json from the current directory
2. Build a streamlit-agraph graph from the nodes and edges using the
   Node, Edge, and Config classes from streamlit_agraph
3. Color nodes by type:
   - feature_table: #4A90D9 (blue)
   - label_table: #E24B4A (red)
   - entity_master: #1D9E75 (green)
   - lookup: #888780 (gray)
4. Label each node with its id
5. Label each edge with its key value
6. Use dashed edges for confidence=medium, solid for confidence=high
7. Render with agraph(nodes=nodes, edges=edges, config=Config(width=700,
   height=500, directed=True, physics=True))
8. Add a small color legend above the graph as markdown

The app should load the graph on startup. No buttons needed for graph render.
Use st.cache_data on the file load so it doesn't re-render on every interaction.
Nodes should be clickable — store selected node in st.session_state.

Start with the stub JSON below if ontology_graph.json doesn't exist yet:
[paste stub JSON here]
```

**Deliverable by 3:15 PM:** Graph renders cleanly in browser with color-coded nodes and labeled edges.

---

## Person 3 — Agent Query + Recommendation Panel

**Claude Code prompt to paste at 2:00 PM:**

```
Add the following to app.py (coordinate with Person 2 on file):

Below the graph, add a section titled "Ask the Ontology":

1. st.text_input: "What do you want to predict?"
2. st.button: "Find relevant data"
3. On button click:
   - Load ontology_graph.json
   - Call OpenAI API with model gpt-4o and response_format={"type": "json_object"}
     with this system prompt:
     "You are an ontology traversal agent. You have a knowledge graph of
      Databricks data assets as JSON. Answer the user's question by traversing
      the graph. Return ONLY valid JSON with this schema:
      {
        'target': {'table': str, 'column': str, 'reason': str},
        'features': [{'table': str, 'columns': [str], 'join_key': str,
                      'confidence': str, 'reason': str}],
        'gaps': str
      }
      Only recommend tables and columns that exist in the graph JSON.
      Never invent assets. If confidence is low, say so in gaps."
   - Pass the full graph JSON + user question as user message
   - Parse the JSON response
   - Display as:
     st.success for target column (table.column + reason)
     st.dataframe for feature table recommendations
     st.warning for gaps if non-empty

Use gpt-4o with response_format={"type": "json_object"} — this guarantees
valid JSON output, no try/except needed around the parse.
```

**Deliverable by 3:15 PM:** Query box returns a rendered recommendation for a sample prediction query relevant to the dataset.

---

## Integration at 3:30 PM

Checklist — all three do this together:

- [ ] P1 delivers `ontology_graph.json` (real or confirmed stub)
- [ ] P2 confirms graph renders with real JSON
- [ ] P3 confirms agent returns grounded recommendations with real JSON
- [ ] Run the full demo flow once end to end
- [ ] Take a screenshot of the working graph — save as `backup_graph.png`
- [ ] Take a screenshot of a working recommendation — save as `backup_rec.png`

If anything breaks after 3:30 PM, revert to stub and use screenshots. Do not debug past 4:00 PM.

---

## Demo Script (60 seconds)

**Say this:**
> "Every ML team spends their first week on a new project doing the same thing — reading schemas, tracing joins, figuring out which column is the target. We built a tool that does it in seconds.
>
> [show graph] This is the semantic ontology our system built by reading the Databricks metadata. No manual documentation. Red nodes are label tables, blue are feature tables, green are entity masters.
>
> [type query] I'll ask it: what data should I use to predict [relevant prediction task for the dataset]?
>
> [show result] It identified the target column, the feature table, the join key, and explained why — grounded entirely in the schema, no hallucination.
>
> We turned schema archaeology into a conversation. That's the first week of every ML project, automated."

**If demo breaks:** Open `backup_graph.png` and `backup_rec.png`. Narrate over screenshots. Do not apologize.

---

## Risk Register

| Risk | Mitigation |
|------|-----------|
| SDK ingestion fails or is slow | Fallback to stub JSON — decision at 2:20 PM |
| OpenAI API key not set | Run `export OPENAI_API_KEY="sk-..."` before 2:00 PM, confirm with a test call |
| agraph graph is cluttered | Hide column-level nodes, show tables only, enable physics for auto-layout |
| P2 and P3 have merge conflicts on app.py | P2 owns graph section, P3 owns query section — clear line break in file |
| Agent cites non-existent tables | System prompt strictly restricts to graph JSON, json_object mode prevents malformed output |
| No internet / API access at venue | Pre-run and cache all LLM outputs before 4:00 PM |

---

## Success Criteria

Done means all five are true at 4:15 PM:

- [ ] Streamlit app opens in browser
- [ ] Graph renders with at least 4 color-coded nodes
- [ ] Agent returns a recommendation for a sample prediction query
- [ ] Recommendation cites only tables in the graph
- [ ] Backup screenshots exist
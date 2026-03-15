"""
Databricks Ontology Copilot

A natural language interface for querying Databricks data ontologies
using AI-powered graph traversal and visualization.

Supports OpenAI and NVIDIA NIM API endpoints.
"""

import streamlit as st
import json
import os
import base64
from pathlib import Path
from openai import OpenAI
from streamlit_agraph import agraph, Node, Edge, Config
from databricks_crawler import create_workspace_client, crawl_catalog_metadata, test_connection
from ontology_builder import build_ontology_graph
from rag_store import create_metadata_store, populate_store, get_rag_context

DEFAULT_OPENAI_MODEL = "gpt-4o"
DEFAULT_NVIDIA_MODEL = "meta/llama-3.1-405b-instruct"
OPENAI_MODEL = os.getenv("OPENAI_MODEL", DEFAULT_OPENAI_MODEL).strip() or DEFAULT_OPENAI_MODEL
NVIDIA_MODEL = os.getenv("NVIDIA_MODEL", DEFAULT_NVIDIA_MODEL).strip() or DEFAULT_NVIDIA_MODEL

# ============================================
# PAGE CONFIGURATION
# ============================================

st.set_page_config(
    page_title="Databricks Ontology Copilot",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

APP_DIR = Path(__file__).resolve().parent

if "selected_node" not in st.session_state:
    st.session_state["selected_node"] = None
if "focused_node" not in st.session_state:
    st.session_state["focused_node"] = None
if "last_result" not in st.session_state:
    st.session_state["last_result"] = None
if "last_question" not in st.session_state:
    st.session_state["last_question"] = ""
if "demo_mode" not in st.session_state:
    st.session_state["demo_mode"] = False

# ============================================
# CUSTOM CSS STYLING
# ============================================

st.markdown("""
<style>
    :root {
        --brand-primary: #FF3621;
        --brand-accent: #FF8A1F;
        --brand-ink: #1B3139;
        --brand-muted: #6C757D;
    }

    .block-container {
        max-width: 1180px;
        margin-left: auto;
        margin-right: auto;
        padding-top: 1rem;
    }

    .main h1 {
        color: var(--brand-primary);
        font-weight: 700;
        padding-bottom: 0.5rem;
    }

    .main h2 {
        color: var(--brand-ink);
        font-weight: 600;
        padding-top: 1rem;
        border-bottom: 2px solid var(--brand-primary);
        padding-bottom: 0.5rem;
    }

    [data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 600;
        color: var(--brand-ink);
    }

    .stAlert {
        border-radius: 8px;
        border-left: 4px solid var(--brand-primary);
    }

    .stButton>button {
        border-radius: 6px;
        font-weight: 600;
        transition: all 0.3s ease;
        background-color: var(--brand-primary);
        border: 1px solid var(--brand-primary);
        color: #FFFFFF;
    }

    .stButton>button:hover {
        transform: translateY(-2px);
        background-color: #E22E1C;
        border: 1px solid #E22E1C;
        box-shadow: 0 4px 12px rgba(255, 54, 33, 0.35);
    }

    .stCodeBlock {
        border-radius: 8px;
        border: 1px solid #E0E0E0;
    }

    .stTextInput>div>div>input {
        border-radius: 6px;
        border: 2px solid #E0E0E0;
        font-size: 1rem;
    }

    .stTextInput>div>div>input:focus {
        border-color: var(--brand-primary);
        box-shadow: 0 0 0 1px var(--brand-primary);
    }

    .streamlit-expanderHeader {
        background-color: #F8F9FA;
        border-radius: 6px;
        font-weight: 600;
    }

    .stSuccess {
        background-color: #D4EDDA;
        border-color: #C3E6CB;
        color: #155724;
    }

    .stWarning {
        background-color: #FFF3CD;
        border-color: #FFEAA7;
        color: #856404;
    }

    .stError {
        background-color: #F8D7DA;
        border-color: #F5C6CB;
        color: #721C24;
    }

    .footer {
        text-align: center;
        padding: 1rem;
        color: var(--brand-muted);
        font-size: 0.875rem;
    }

    .app-title {
        color: var(--brand-ink);
        font-weight: 750;
        text-align: center;
        margin: 0.1rem 0 0.2rem 0;
    }

    .app-subtitle {
        color: var(--brand-muted);
        text-align: center;
        font-style: italic;
        margin-top: 0;
        margin-bottom: 1.25rem;
    }

    .app-logo-wrap {
        display: flex;
        justify-content: center;
        align-items: center;
        width: 100%;
        margin-bottom: 0.5rem;
    }

    .app-logo {
        width: min(560px, 72vw);
        max-width: 100%;
        height: auto;
        display: block;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# SIDEBAR: DATABRICKS CONFIGURATION
# ============================================

with st.sidebar:
    st.header("Configuration")

    # --- Databricks Connection ---
    st.subheader("Databricks Connection")
    db_host = st.text_input(
        "Workspace URL",
        placeholder="https://xxx.cloud.databricks.com",
        value=st.session_state.get("db_host", ""),
        key="db_host_input",
    )
    db_token = st.text_input(
        "Personal Access Token",
        type="password",
        value=st.session_state.get("db_token", ""),
        key="db_token_input",
    )
    db_warehouse_id = st.text_input(
        "SQL Warehouse ID",
        placeholder="abc123def456",
        value=st.session_state.get("db_warehouse_id", ""),
        key="db_warehouse_input",
    )

    # --- Catalog ---
    st.subheader("Catalog")
    catalog_name = st.text_input(
        "Catalog Name",
        placeholder="uw_team_h",
        value=st.session_state.get("catalog_name", ""),
        key="catalog_name_input",
    )

    # --- Test Connection ---
    if st.button("Test Connection"):
        if not db_host or not db_token or not db_warehouse_id:
            st.error("Please fill in all connection fields.")
        else:
            try:
                with st.spinner("Testing connection..."):
                    client = create_workspace_client(db_host, db_token)
                    test_connection(client, db_warehouse_id)
                    st.session_state["db_host"] = db_host
                    st.session_state["db_token"] = db_token
                    st.session_state["db_warehouse_id"] = db_warehouse_id
                    st.session_state["db_client"] = client
                    st.session_state["db_connected"] = True
                st.success("Connected to Databricks!")
            except Exception as e:
                st.session_state["db_connected"] = False
                st.error(f"Connection failed: {e}")

    # --- Crawl Catalog ---
    db_connected = st.session_state.get("db_connected", False)
    if st.button("Crawl Catalog", type="primary", disabled=not db_connected or not catalog_name):
        try:
            with st.spinner("Crawling catalog metadata..."):
                client = st.session_state["db_client"]
                wh_id = st.session_state["db_warehouse_id"]
                st.session_state["catalog_name"] = catalog_name

                # 1. Crawl metadata
                metadata = crawl_catalog_metadata(client, wh_id, catalog_name)
                st.session_state["catalog_metadata"] = metadata

                # 2. Build ontology graph
                graph = build_ontology_graph(metadata)
                st.session_state["live_graph_data"] = graph

                # 3. Populate ChromaDB RAG store
                collection = create_metadata_store()
                doc_count = populate_store(collection, metadata)
                st.session_state["rag_collection"] = collection

                table_count = sum(len(s["tables"]) for s in metadata["schemas"])
                st.success(
                    f"Crawled {table_count} tables across "
                    f"{len(metadata['schemas'])} schemas. "
                    f"Indexed {doc_count} documents in RAG store."
                )
        except Exception as e:
            st.error(f"Crawl failed: {e}")

    # --- Status Indicators ---
    st.divider()
    st.subheader("Status")
    if st.session_state.get("db_connected"):
        st.success("Databricks: Connected")
    else:
        st.info("Databricks: Not connected")

    if "catalog_metadata" in st.session_state:
        meta = st.session_state["catalog_metadata"]
        table_count = sum(len(s["tables"]) for s in meta["schemas"])
        st.success(f"Metadata: {table_count} tables crawled")
    else:
        st.info("Metadata: No catalog crawled")

    if "rag_collection" in st.session_state:
        count = st.session_state["rag_collection"].count()
        st.success(f"RAG Index: {count} documents")
    else:
        st.info("RAG Index: Not initialized")

# ============================================
# SHARED: DATA LOADING
# ============================================

@st.cache_data
def load_graph_data():
    """Load the ontology graph from JSON file (fallback/demo)."""
    graph_path = APP_DIR / "ontology_graph.json"
    try:
        with open(graph_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        st.error(f"Error: ontology_graph.json not found at `{graph_path}`.")
        return None
    except json.JSONDecodeError as exc:
        st.error(f"Error: Invalid JSON in ontology_graph.json: {exc}")
        return None


def get_active_graph_data():
    """Get graph data - prefer live crawled data, fall back to file."""
    if "live_graph_data" in st.session_state:
        return st.session_state["live_graph_data"]
    return load_graph_data()


def get_logo_path():
    """Return the first available logo path, else None."""
    candidates = [
        APP_DIR.parent / "logo.png",
        APP_DIR.parent / "linqr-logo-dark",
        APP_DIR.parent / "linqr-logo-dark.png",
        APP_DIR.parent / "linqr-logo-dark.jpg",
        APP_DIR.parent / "linqr-logo-dark.jpeg",
        APP_DIR.parent / "linqr-logo-dark.webp",
        APP_DIR.parent / "linqr-logo",
        APP_DIR.parent / "linqr-logo.png",
        APP_DIR.parent / "linqr-logo.jpg",
        APP_DIR.parent / "linqr-logo.jpeg",
        APP_DIR.parent / "linqr-logo.webp",
        APP_DIR / "assets" / "linqr-logo-light.png",
        APP_DIR / "assets" / "linqr-logo-dark.png",
        APP_DIR / "assets" / "logo-light.png",
        APP_DIR / "assets" / "logo-dark.png",
        APP_DIR / "assets" / "logo.png",
        APP_DIR / "linqr-logo-light.png",
        APP_DIR / "linqr-logo-dark.png",
        APP_DIR / "logo.png",
    ]
    for path in candidates:
        if path.exists():
            return path
    return None


def render_centered_logo(logo_path: Path):
    """Render a centered responsive logo image."""
    suffix = logo_path.suffix.lower()
    mime_type = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
    }.get(suffix, "image/png")
    encoded = base64.b64encode(logo_path.read_bytes()).decode("ascii")
    st.markdown(
        f'''
        <div class="app-logo-wrap">
            <img src="data:{mime_type};base64,{encoded}" alt="LINQR logo" class="app-logo" />
        </div>
        ''',
        unsafe_allow_html=True,
    )

# ============================================
# APP HEADER
# ============================================

logo_path = get_logo_path()
if logo_path:
    render_centered_logo(logo_path)
    st.markdown('<h1 class="app-title">Databricks Ontology Copilot</h1>', unsafe_allow_html=True)
    st.markdown('<p class="app-subtitle">AI-powered data discovery for ML projects</p>', unsafe_allow_html=True)
else:
    st.markdown('<h1 class="app-title">Databricks Ontology Copilot</h1>', unsafe_allow_html=True)
    st.markdown('<p class="app-subtitle">AI-powered data discovery for ML projects</p>', unsafe_allow_html=True)

# ============================================
# GRAPH VISUALIZATION
# ============================================

# Load graph data
graph_data = get_active_graph_data()

if graph_data:
    st.header("Data Ontology Graph")

    with st.expander("Graph Display Controls", expanded=False):
        anti_overlap_mode = st.checkbox(
            "Use anti-overlap hierarchical layout",
            value=True,
            help="Recommended for larger graphs or noisy test data",
        )
        hierarchy_direction = st.selectbox(
            "Hierarchy direction",
            options=["LR", "UD"],
            index=0,
            help="LR = left-to-right, UD = top-to-bottom",
        )
        show_edge_labels = st.checkbox(
            "Show edge key labels",
            value=False,
            help="Turn off labels to reduce visual knotting",
        )
        show_nav_controls = st.checkbox(
            "Show on-canvas navigation controls",
            value=False,
            help="Disable to avoid control clipping and reduce visual noise",
        )

    st.markdown("""
    **Node Types:**
    - **Orange:** Feature Table
    - **Red:** Label Table
    - **Amber:** Entity Master
    - **Gray:** Lookup / Other
    """)

    color_map = {
        "feature_table": "#FF8A1F",
        "label_table": "#E24B4A",
        "entity_master": "#F2A93B",
        "lookup": "#888780",
    }

    # Determine which nodes/edges to display based on focused node
    focused_node = st.session_state.get("focused_node")

    if focused_node:
        # Find neighbor node IDs (connected via any edge)
        neighbor_ids = set()
        focused_edges = []
        for edge_data in graph_data.get("edges", []):
            if edge_data["source"] == focused_node:
                neighbor_ids.add(edge_data["target"])
                focused_edges.append(edge_data)
            elif edge_data["target"] == focused_node:
                neighbor_ids.add(edge_data["source"])
                focused_edges.append(edge_data)
        visible_node_ids = {focused_node} | neighbor_ids
        visible_nodes = [n for n in graph_data.get("nodes", []) if n["id"] in visible_node_ids]
        visible_edge_data = focused_edges
    else:
        visible_nodes = graph_data.get("nodes", [])
        visible_edge_data = graph_data.get("edges", [])

    nodes = []
    edges = []

    for node_data in visible_nodes:
        node_type = node_data.get("type", "lookup")
        is_focused = focused_node and node_data["id"] == focused_node
        nodes.append(Node(
            id=node_data["id"],
            label=node_data["id"],
            size=40 if is_focused else 28,
            color=color_map.get(node_type, "#888780"),
            font={"size": 18 if is_focused else 14, "color": "#FFFFFF"},
            shape="box",
            borderWidth=4 if is_focused else 1,
            borderWidthSelected=4,
        ))

    for edge_data in visible_edge_data:
        confidence = edge_data.get("confidence", "high")
        edge_color = "#9A9A9A"
        if confidence == "high":
            edge_color = "#FF8A1F"
        elif confidence == "medium":
            edge_color = "#C58B4D"
        edges.append(Edge(
            source=edge_data["source"],
            target=edge_data["target"],
            label=edge_data.get("key", "") if show_edge_labels else "",
            color=edge_color,
            dashes=confidence in ("medium", "low"),
            font={"size": 10, "align": "middle"},
            width=3 if focused_node else 1,
        ))

    config_kwargs = dict(
        width=940,
        height=540,
        directed=True,
        physics=not anti_overlap_mode,
        hierarchical=anti_overlap_mode,
        nodeHighlightBehavior=True,
        highlightColor="#FFD2A6",
        collapsible=False,
        layout={"improvedLayout": True, "randomSeed": 42},
        node={"labelProperty": "label"},
        link={"labelProperty": "label", "renderLabel": show_edge_labels},
    )
    if anti_overlap_mode:
        config_kwargs["layout"] = {
            "improvedLayout": True,
            "randomSeed": 42,
            "hierarchical": {
                "enabled": True,
                "direction": hierarchy_direction,
                "sortMethod": "directed",
                "nodeSpacing": 220,
                "levelSeparation": 220,
                "treeSpacing": 260,
            },
        }
        config_kwargs["physics"] = False
        config_kwargs["hierarchical"] = True
    config_kwargs["interaction"] = {
        "zoomSpeed": 0.35,
        "navigationButtons": show_nav_controls,
        "zoomView": True,
        "dragView": True,
    }
    try:
        config = Config(**config_kwargs)
    except TypeError:
        config_kwargs.pop("interaction", None)
        config = Config(**config_kwargs)

    selected_node = agraph(nodes=nodes, edges=edges, config=config)

    # Handle node click: focus on the clicked node
    if selected_node and selected_node != focused_node:
        st.session_state["focused_node"] = selected_node
        st.session_state["selected_node"] = selected_node
        st.rerun()

    if focused_node:
        # Show focused-node info panel with reset button
        focus_col1, focus_col2 = st.columns([3, 1])
        with focus_col1:
            # Gather connection details
            connections = []
            for edge_data in graph_data.get("edges", []):
                if edge_data["source"] == focused_node:
                    connections.append(f"**{focused_node}** → **{edge_data['target']}** ({edge_data.get('relationship', '')} on `{edge_data.get('key', '')}`)")
                elif edge_data["target"] == focused_node:
                    connections.append(f"**{edge_data['source']}** → **{focused_node}** ({edge_data.get('relationship', '')} on `{edge_data.get('key', '')}`)")
            st.info(f"Focused on: **{focused_node}**\n\n" + "\n\n".join(connections))
        with focus_col2:
            if st.button("Reset View", type="primary", use_container_width=True):
                st.session_state["focused_node"] = None
                st.rerun()
    elif st.session_state.get("selected_node"):
        st.info(f"Selected node: **{st.session_state['selected_node']}**")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Nodes", len(graph_data.get("nodes", [])))
    with col2:
        st.metric("Total Edges", len(graph_data.get("edges", [])))
    with col3:
        node_types = set(n.get("type", "unknown") for n in graph_data.get("nodes", []))
        st.metric("Node Types", len(node_types))

    if "catalog_metadata" in st.session_state:
        with st.expander("Catalog Metadata Summary"):
            meta = st.session_state["catalog_metadata"]
            st.markdown(f"**Catalog:** `{meta['catalog']}`")
            for schema in meta["schemas"]:
                st.markdown(
                    f"- **{schema['name']}** — {len(schema['tables'])} tables"
                )
                if schema.get("comment"):
                    st.caption(f"  {schema['comment']}")

else:
    st.error("Warning: Cannot render graph - data loading failed")

st.markdown("---")

# ============================================
# AGENT QUERY & RECOMMENDATION PANEL
# ============================================

st.header("Ask the Ontology")

# ============================================
# API CONFIGURATION
# ============================================

def get_api_client():
    """
    Get API client (OpenAI or NVIDIA NIM)

    Supports:
    - OpenAI API: OPENAI_API_KEY
    - NVIDIA NIM: NVIDIA_API_KEY (OpenAI-compatible format)

    Returns:
        tuple: (client, model_name, api_type)
    """
    # Check for NVIDIA NIM API key first
    nvidia_key = os.getenv('NVIDIA_API_KEY')
    if nvidia_key:
        client = OpenAI(
            api_key=nvidia_key,
            base_url="https://integrate.api.nvidia.com/v1"
        )
        return client, NVIDIA_MODEL, "nvidia"

    # Fall back to OpenAI
    openai_key = os.getenv('OPENAI_API_KEY')
    if openai_key:
        client = OpenAI(api_key=openai_key)
        return client, OPENAI_MODEL, "openai"

    return None, None, None


# Helper function for the agent
def query_ontology_agent(graph_json, user_question, rag_context=None):
    """
    Query the ontology using LLM (OpenAI or NVIDIA NIM)

    Args:
        graph_json: The ontology graph as a dict
        user_question: User's natural language question
        rag_context: Optional RAG-retrieved metadata context string

    Returns:
        dict: Structured recommendation with target, features, gaps
    """
    client, model_name, api_type = get_api_client()

    if not client:
        raise ValueError("No API key configured. Set OPENAI_API_KEY or NVIDIA_API_KEY")

    system_prompt = '''You are an ontology traversal agent. You have a knowledge graph of Databricks data assets as JSON. Answer the user's question by traversing the graph. Return ONLY valid JSON with this schema:
{
  "target": {"table": str, "column": str, "reason": str},
  "features": [{"table": str, "columns": [str], "join_key": str, "confidence": str, "reason": str}],
  "gaps": str
}
Only recommend tables and columns that exist in the graph JSON or the provided metadata. Never invent assets. If confidence is low, say so in gaps. Be concise but informative.'''

    # Build user message with optional RAG context
    user_content = f'Graph:\n{json.dumps(graph_json)}'
    if rag_context:
        user_content += f'\n\nRelevant Metadata (from catalog):\n{rag_context}'
    user_content += f'\n\nQuestion: {user_question}'

    # o-series models (o1, o3, gpt-5-mini, etc.) don't support temperature,
    # max_tokens, response_format, or the 'system' role.
    is_reasoning_model = any(
        model_name.startswith(p)
        for p in ("o1", "o3", "o4", "gpt-5-mini")
    )

    # Reasoning models require 'developer' role instead of 'system'
    system_role = "developer" if is_reasoning_model else "system"

    # Build API call parameters
    call_params = {
        'model': model_name,
        'messages': [
            {'role': system_role, 'content': system_prompt},
            {'role': 'user', 'content': user_content}
        ],
    }

    if is_reasoning_model:
        call_params['max_completion_tokens'] = 2000
    else:
        call_params['temperature'] = 0.0
        call_params['max_tokens'] = 1000
        if api_type == "openai":
            call_params['response_format'] = {'type': 'json_object'}

    response = client.chat.completions.create(**call_params)

    raw = response.choices[0].message.content or ""
    # Strip markdown code fences if present
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
        if raw.endswith("```"):
            raw = raw[:-3]
        raw = raw.strip()

    if not raw:
        raise ValueError(f"Model returned empty response. Raw: {response.choices[0].message}")

    return json.loads(raw)


# Check if API key is set
api_key_set = bool(os.getenv('OPENAI_API_KEY') or os.getenv('NVIDIA_API_KEY'))
api_provider = "NVIDIA NIM" if os.getenv('NVIDIA_API_KEY') else "OpenAI" if os.getenv('OPENAI_API_KEY') else None
if not api_key_set:
    st.warning("""
    Warning: **API key not set**

    To use the agent, set one of the following:

    **OpenAI:**
    ```bash
    export OPENAI_API_KEY='sk-...'
    export OPENAI_MODEL='gpt-5-mini'  # Optional override
    ```

    **NVIDIA NIM (OpenAI-compatible):**
    ```bash
    export NVIDIA_API_KEY='nvapi-...'
    ```

    Then restart the Streamlit app.
    """)
else:
    st.info(f"Using **{api_provider}** API")

# Demo mode (fallback for live demo if API fails)
with st.expander("Demo Controls"):
    demo_mode = st.checkbox(
        "Use cached demo response (fallback if API fails)",
        key="demo_mode",
        help="Enable this if the API is down or you want to show a pre-cached result",
    )
    if demo_mode:
        st.info("Demo mode enabled - using cached response")

# User input section with improved layout
col1, col2 = st.columns([4, 1])

with col1:
    user_question = st.text_input(
        "What do you want to predict?",
        placeholder="e.g., What data should I use to predict customer churn?",
        disabled=(not api_key_set and not demo_mode) or graph_data is None,
        key="query_input",
    )

with col2:
    st.write("")  # Spacer for alignment
    query_button = st.button(
        "Find relevant data",
        type="primary",
        disabled=(not api_key_set and not demo_mode) or graph_data is None,
        use_container_width=True
    )

# Example questions
with st.expander("💡 Example questions"):
    st.markdown("""
    **Try asking:**
    - What data should I use to predict target_outcome?
    - Which tables contain features for entity_id?
    - What are the available label columns?
    - How can I join feature tables with label tables?

    **Note:** These examples work with the stub data. Adjust questions based on the actual dataset.
    """)

# Handle query submission
if query_button:
    if not user_question or not user_question.strip():
        st.error("Error: Please enter a question to get started.")
    else:
        # Show loading state
        with st.spinner("Querying the ontology..."):
            try:
                if demo_mode:
                    # Use cached demo response
                    result = {
                        "target": {
                            "table": "example_labels",
                            "column": "target_outcome",
                            "reason": "This table contains the target variable for prediction. The target_outcome column indicates the result we want to predict based on entity characteristics and features."
                        },
                        "features": [
                            {
                                "table": "example_features_daily",
                                "columns": ["metric_a", "metric_b", "metric_c", "aggregate_value"],
                                "join_key": "entity_id",
                                "confidence": "high",
                                "reason": "Daily aggregated metrics provide strong predictive signals. These features capture entity behavior patterns over time."
                            },
                            {
                                "table": "example_derived_features",
                                "columns": ["computed_metric_x", "computed_metric_y"],
                                "join_key": "entity_id",
                                "confidence": "medium",
                                "reason": "Derived features offer additional computed insights, though with medium confidence as they may have some data quality issues."
                            }
                        ],
                        "gaps": "Consider adding temporal features or interaction terms for improved model performance."
                    }
                    st.info("Showing cached demo response")
                else:
                    # Retrieve RAG context if available
                    rag_context = None
                    if "rag_collection" in st.session_state:
                        rag_context = get_rag_context(
                            st.session_state["rag_collection"], user_question
                        )
                    # Call the agent with live API + RAG context
                    result = query_ontology_agent(graph_data, user_question, rag_context)

                # Store result in session state for persistence
                st.session_state['last_result'] = result
                st.session_state['last_question'] = user_question

            except Exception as e:
                st.error(f"Error: Error querying the agent: {str(e)}")
                with st.expander("Debug Info"):
                    st.code(str(e), language="text")
                result = None

# Display results if available
if st.session_state.get("last_result"):
    result = st.session_state["last_result"]

    st.markdown("---")
    st.subheader("Recommendation")

    # Display target
    if "target" in result and result["target"]:
        target = result["target"]
        st.success(f"**Target: Target Column:** `{target.get('table', 'N/A')}.{target.get('column', 'N/A')}`")
        st.write(target.get('reason', 'No reason provided'))

    if "features" in result and result["features"]:
        st.markdown("### Recommended Feature Tables")

        confidence_icons = {
            "high": "🟢",
            "medium": "🟡",
            "low": "🔴",
        }

        for idx, feat in enumerate(result["features"], 1):
            confidence_icon = confidence_icons.get(feat.get("confidence", "medium"), "")

            with st.expander(
                f"{confidence_icon} **{feat.get('table', 'Unknown')}** (confidence: {feat.get('confidence', 'medium')})",
                expanded=(idx == 1),
            ):
                col_a, col_b = st.columns(2)

                with col_a:
                    st.write(f"**Join Key:** `{feat.get('join_key', 'N/A')}`")

                with col_b:
                    columns = feat.get('columns', [])
                    if columns:
                        st.write(f"**Columns ({len(columns)}):** {', '.join([f'`{c}`' for c in columns[:5]])}")
                        if len(columns) > 5:
                            st.write(f"_...and {len(columns) - 5} more_")
                    else:
                        st.write("**Columns:** None specified")

                st.write(f"**Reasoning:** {feat.get('reason', 'No reasoning provided')}")

        if len(result["features"]) > 0 and "target" in result:
            with st.expander("SQL Scaffold (Copy & Paste)"):
                first_feat = result["features"][0]
                target = result["target"]

                # Build column list
                feature_cols = first_feat.get("columns", ["col1", "col2"])[:5]
                feature_select = ',\n  '.join([f'features.{c}' for c in feature_cols])

                sql_template = f"""-- Suggested query scaffold
SELECT
  labels.{target.get('column', 'target')} as target,
  {feature_select}
FROM {target.get('table', 'label_table')} as labels
JOIN {first_feat.get('table', 'feature_table')} as features
  ON labels.{first_feat.get('join_key', 'id')} = features.{first_feat.get('join_key', 'id')}
WHERE labels.{target.get('column', 'target')} IS NOT NULL
LIMIT 1000;"""

                st.code(sql_template, language='sql')
                st.caption("Warning: This is a starting point. Adjust based on your specific needs and add more feature tables as needed.")

    if "gaps" in result and result["gaps"]:
        st.warning(f"**Warning: Data Gaps & Limitations:**\n\n{result['gaps']}")

    if st.session_state.get("last_question"):
        st.caption(f"_Query: \"{st.session_state['last_question']}\"_")

# Empty state when no results
elif graph_data and (api_key_set or demo_mode):
    st.info("Enter a prediction question above to get data recommendations from the ontology.")

# Footer / Status
st.markdown("---")

# Status indicators
col_status1, col_status2, col_status3 = st.columns(3)
with col_status1:
    if graph_data:
        st.success("Success: Graph loaded")
    else:
        st.error("Error: Graph not loaded")

with col_status2:
    if api_key_set:
        st.success("Success: API key set")
    else:
        st.warning("Warning: API key missing")

with col_status3:
    if demo_mode:
        st.info("Demo mode active")
    elif st.session_state.get("last_result"):
        st.success("Success: Results cached")
    else:
        st.info("Ready for query")

st.markdown(
    '<div class="footer">Built for Databricks Hackathon 2026 | Powered by LLMs + Streamlit + streamlit-agraph</div>',
    unsafe_allow_html=True
)

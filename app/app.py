"""
Databricks Ontology Copilot

A natural language interface for querying Databricks data ontologies
using AI-powered graph traversal and visualization.

Supports OpenAI GPT-4o and NVIDIA NIM API endpoints.
"""

import streamlit as st
import json
import os
from pathlib import Path
from openai import OpenAI
from streamlit_agraph import agraph, Node, Edge, Config

# ============================================
# PAGE CONFIGURATION
# ============================================

st.set_page_config(
    page_title="Databricks Ontology Copilot",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# App constants
APP_DIR = Path(__file__).resolve().parent

# Stable session-state defaults for predictable reruns
if "selected_node" not in st.session_state:
    st.session_state["selected_node"] = None
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

    /* Keep content centered and readable on large screens */
    .block-container {
        max-width: 1180px;
        margin-left: auto;
        margin-right: auto;
        padding-top: 1rem;
    }

    /* Main title styling */
    .main h1 {
        color: var(--brand-primary);
        font-weight: 700;
        padding-bottom: 0.5rem;
    }

    /* Section headers */
    .main h2 {
        color: var(--brand-ink);
        font-weight: 600;
        padding-top: 1rem;
        border-bottom: 2px solid var(--brand-primary);
        padding-bottom: 0.5rem;
    }

    /* Metrics styling */
    [data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 600;
        color: var(--brand-ink);
    }

    /* Info boxes */
    .stAlert {
        border-radius: 8px;
        border-left: 4px solid var(--brand-primary);
    }

    /* Buttons */
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

    /* Code blocks */
    .stCodeBlock {
        border-radius: 8px;
        border: 1px solid #E0E0E0;
    }

    /* Input fields */
    .stTextInput>div>div>input {
        border-radius: 6px;
        border: 2px solid #E0E0E0;
        font-size: 1rem;
    }

    .stTextInput>div>div>input:focus {
        border-color: var(--brand-primary);
        box-shadow: 0 0 0 1px var(--brand-primary);
    }

    /* Expanders */
    .streamlit-expanderHeader {
        background-color: #F8F9FA;
        border-radius: 6px;
        font-weight: 600;
    }

    /* Success/Warning/Error boxes */
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

    /* Footer styling */
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
        margin-bottom: 0.35rem;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# SHARED: DATA LOADING
# ============================================

@st.cache_data
def load_graph_data():
    """Load the ontology graph from JSON file"""
    graph_path = APP_DIR / "ontology_graph.json"
    try:
        with open(graph_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error(f"Error: ontology_graph.json not found at `{graph_path}`.")
        return None
    except json.JSONDecodeError as e:
        st.error(f"Error: Invalid JSON in ontology_graph.json: {e}")
        return None

# Optional logo support (safe if files are absent)
def get_logo_path():
    """Return first available logo path, else None."""
    # Support both app directory and project root naming conventions.
    candidates = [
        APP_DIR.parent / "linqr-logo-dark",
        APP_DIR.parent / "linqr-logo-dark.png",
        APP_DIR.parent / "linqr-logo-dark.jpg",
        APP_DIR.parent / "linqr-logo-dark.jpeg",
        APP_DIR.parent / "linqr-logo-dark.webp",
        APP_DIR.parent / "linqr-logo",
        APP_DIR.parent / "linqr-logo-dark",
        APP_DIR.parent / "linqr-logo.png",
        APP_DIR.parent / "linqr-logo-dark.png",
        APP_DIR.parent / "linqr-logo.jpg",
        APP_DIR.parent / "linqr-logo-dark.jpg",
        APP_DIR.parent / "linqr-logo.jpeg",
        APP_DIR.parent / "linqr-logo-dark.jpeg",
        APP_DIR.parent / "linqr-logo.webp",
        APP_DIR.parent / "linqr-logo-dark.webp",
        APP_DIR / "assets" / "linqr-logo-light.png",
        APP_DIR / "assets" / "linqr-logo-dark.png",
        APP_DIR / "assets" / "logo-light.png",
        APP_DIR / "assets" / "logo-dark.png",
        APP_DIR / "assets" / "logo.png",
        APP_DIR / "linqr-logo-light.png",
        APP_DIR / "linqr-logo-dark.png",
        APP_DIR / "logo.png",
        APP_DIR.parent.parent / "linqr-logo-dark",
        APP_DIR.parent.parent / "linqr-logo-dark.png",
        APP_DIR.parent.parent / "linqr-logo",
        APP_DIR.parent.parent / "linqr-logo.png",
    ]
    for path in candidates:
        if path.exists():
            return path
    return None

# ============================================
# GRAPH VISUALIZATION
# ============================================

logo_path = get_logo_path()
if logo_path:
    center_col = st.columns([1, 6, 1])[1]
    with center_col:
        st.markdown('<div class="app-logo-wrap">', unsafe_allow_html=True)
        st.image(str(logo_path), width=240)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<h1 class="app-title">Databricks Ontology Copilot</h1>', unsafe_allow_html=True)
        st.markdown('<p class="app-subtitle">AI-powered data discovery for ML projects</p>', unsafe_allow_html=True)
else:
    st.markdown('<h1 class="app-title">Databricks Ontology Copilot</h1>', unsafe_allow_html=True)
    st.markdown('<p class="app-subtitle">AI-powered data discovery for ML projects</p>', unsafe_allow_html=True)

# Load graph data
graph_data = load_graph_data()

if graph_data:
    st.header("Data Ontology Graph")

    # Lightweight clutter controls to keep large/messy graphs readable in demos.
    with st.expander("Graph Display Controls", expanded=False):
        anti_overlap_mode = st.checkbox(
            "Use anti-overlap hierarchical layout",
            value=True,
            help="Recommended for larger graphs or noisy test data"
        )
        hierarchy_direction = st.selectbox(
            "Hierarchy direction",
            options=["LR", "UD"],
            index=0,
            help="LR = left-to-right, UD = top-to-bottom"
        )
        show_edge_labels = st.checkbox(
            "Show edge key labels",
            value=False,
            help="Turn off labels to reduce visual knotting"
        )
        show_nav_controls = st.checkbox(
            "Show on-canvas navigation controls",
            value=False,
            help="Disable to avoid control clipping and reduce visual noise"
        )

    # Color legend
    st.markdown("""
    **Node Types:**
    - **Orange:** Feature Table
    - **Red:** Label Table
    - **Amber:** Entity Master
    - **Gray:** Lookup / Other
    """)

    # Build agraph nodes and edges
    nodes = []
    edges = []

    # Color mapping for node types
    color_map = {
        'feature_table': '#FF8A1F',  # Orange
        'label_table': '#E24B4A',     # Red
        'entity_master': '#F2A93B',   # Amber
        'lookup': '#888780'           # Gray
    }

    # Create nodes
    for node_data in graph_data.get('nodes', []):
        node_type = node_data.get('type', 'lookup')
        nodes.append(Node(
            id=node_data['id'],
            label=node_data['id'],
            size=28,
            color=color_map.get(node_type, '#888780'),
            font={'size': 14, 'color': '#FFFFFF'},
            shape='box'
        ))

    # Create edges
    for edge_data in graph_data.get('edges', []):
        confidence = edge_data.get('confidence', 'high')
        dashed = confidence in ('medium', 'low')
        edge_color = '#9A9A9A'
        if confidence == 'high':
            edge_color = '#FF8A1F'
        elif confidence == 'medium':
            edge_color = '#C58B4D'

        edges.append(Edge(
            source=edge_data['source'],
            target=edge_data['target'],
            label=edge_data.get('key', '') if show_edge_labels else '',
            color=edge_color,
            dashes=dashed,
            font={'size': 10, 'align': 'middle'}
        ))

    # Configure graph visualization
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
        node={'labelProperty': 'label'},
        link={'labelProperty': 'label', 'renderLabel': show_edge_labels}
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
                "treeSpacing": 260
            }
        }
        config_kwargs["physics"] = False
        config_kwargs["hierarchical"] = True

    # Best-effort interaction tuning for less aggressive zooming.
    config_kwargs["interaction"] = {
        "zoomSpeed": 0.35,
        "navigationButtons": show_nav_controls,
        "zoomView": True,
        "dragView": True
    }
    try:
        config = Config(**config_kwargs)
    except TypeError:
        # Some streamlit-agraph versions may reject interaction.
        config_kwargs.pop("interaction", None)
        config = Config(**config_kwargs)

    # Render graph
    selected_node = agraph(nodes=nodes, edges=edges, config=config)

    # Store selected node in session state
    if selected_node:
        st.session_state['selected_node'] = selected_node

    if st.session_state.get('selected_node'):
        st.info(f"Selected node: **{st.session_state['selected_node']}**")

    # Graph statistics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Nodes", len(graph_data.get('nodes', [])))
    with col2:
        st.metric("Total Edges", len(graph_data.get('edges', [])))
    with col3:
        node_types = set(n.get('type', 'unknown') for n in graph_data.get('nodes', []))
        st.metric("Node Types", len(node_types))

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
        return client, "meta/llama-3.1-405b-instruct", "nvidia"

    # Fall back to OpenAI
    openai_key = os.getenv('OPENAI_API_KEY')
    if openai_key:
        client = OpenAI(api_key=openai_key)
        return client, "gpt-4o", "openai"

    return None, None, None


# Helper function for the agent
def query_ontology_agent(graph_json, user_question):
    """
    Query the ontology using LLM (OpenAI GPT-4o or NVIDIA NIM)

    Args:
        graph_json: The ontology graph as a dict
        user_question: User's natural language question

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
Only recommend tables and columns that exist in the graph JSON. Never invent assets. If confidence is low, say so in gaps. Be concise but informative.'''

    # Build API call parameters
    call_params = {
        'model': model_name,
        'messages': [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': f'Graph: {json.dumps(graph_json)}\n\nQuestion: {user_question}'}
        ],
        'temperature': 0.0,
        'max_tokens': 1000
    }

    # Only OpenAI supports response_format parameter
    if api_type == "openai":
        call_params['response_format'] = {'type': 'json_object'}

    response = client.chat.completions.create(**call_params)
    message_content = ""
    if response.choices and response.choices[0].message:
        message_content = response.choices[0].message.content or ""

    try:
        parsed = json.loads(message_content)
    except json.JSONDecodeError as exc:
        raise ValueError(
            "Model response was not valid JSON. Try again or enable demo mode."
        ) from exc

    if not isinstance(parsed, dict):
        raise ValueError("Unexpected model response shape. Expected a JSON object.")
    return parsed


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
    ```

    **NVIDIA NIM (OpenAI-compatible):**
    ```bash
    export NVIDIA_API_KEY='nvapi-...'
    ```

    Or enable **Demo Controls** below to use a cached response without API keys.
    """)
else:
    st.info(f"Using **{api_provider}** API")

# Demo mode (fallback for live demo if API fails)
with st.expander("Demo Controls"):
    demo_mode = st.checkbox(
        "Use cached demo response (fallback if API fails)",
        key="demo_mode",
        help="Enable this if the API is down or you want to show a pre-cached result"
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
        key="query_input"
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
                    # Call the agent with live API
                    result = query_ontology_agent(graph_data, user_question)

                # Store result in session state for persistence
                st.session_state['last_result'] = result
                st.session_state['last_question'] = user_question

            except Exception as e:
                st.error(f"Error: Error querying the agent: {str(e)}")
                with st.expander("Debug Info"):
                    st.code(str(e), language="text")
                result = None

# Display results if available
if st.session_state.get('last_result'):
    result = st.session_state['last_result']

    st.markdown("---")
    st.subheader("Recommendation")

    # Display target
    if 'target' in result and result['target']:
        target = result['target']
        st.success(f"**Target: Target Column:** `{target.get('table', 'N/A')}.{target.get('column', 'N/A')}`")
        st.write(target.get('reason', 'No reason provided'))

    # Display features
    if 'features' in result and result['features']:
        st.markdown("### Recommended Feature Tables")

        # Confidence color mapping
        confidence_icons = {
            'high': '🟢',
            'medium': '🟡',
            'low': '🔴'
        }

        for idx, feat in enumerate(result['features'], 1):
            confidence_icon = confidence_icons.get(feat.get('confidence', 'medium'), '')

            with st.expander(
                f"{confidence_icon} **{feat.get('table', 'Unknown')}** (confidence: {feat.get('confidence', 'medium')})",
                expanded=(idx == 1)  # Expand first one by default
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

        # SQL scaffold (nice-to-have)
        if len(result['features']) > 0 and 'target' in result:
            with st.expander("SQL Scaffold (Copy & Paste)"):
                first_feat = result['features'][0]
                target = result['target']

                # Build column list
                feature_cols = first_feat.get('columns', ['col1', 'col2'])[:5]  # Limit to 5 for readability
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

    # Display gaps/warnings
    if 'gaps' in result and result['gaps']:
        st.warning(f"**Warning: Data Gaps & Limitations:**\n\n{result['gaps']}")

    # Display query for reference
    if st.session_state.get('last_question'):
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
    elif st.session_state.get('last_result'):
        st.success("Success: Results cached")
    else:
        st.info("Ready for query")

st.markdown(
    '<div class="footer">Built for Databricks Hackathon 2026 | Powered by LLMs + Streamlit + streamlit-agraph</div>',
    unsafe_allow_html=True
)

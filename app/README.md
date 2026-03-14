# Databricks Ontology Copilot - Agent Query Interface

A natural language interface for querying Databricks data ontologies using AI-powered graph traversal.

## Setup

### Prerequisites

- Python 3.8+
- OpenAI API key
- Virtual environment (recommended)

### Installation

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install streamlit streamlit-agraph networkx openai databricks-sdk

# Set OpenAI API key
export OPENAI_API_KEY='sk-...'  # Replace with your actual key
```

### Running the Application

```bash
# Navigate to app directory
cd app

# Start Streamlit
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`.

## Features

### Agent Query Interface
- Natural language question input for data discovery
- AI-powered ontology traversal using GPT-4o
- Structured recommendations with target columns, feature tables, and join keys
- Confidence scoring for recommendations
- SQL scaffold generation

### Data Visualization
- Interactive knowledge graph display
- Color-coded nodes by type (feature tables, label tables, entity masters)
- Relationship edges with confidence indicators

## Usage

1. **Load your ontology graph** - Place your `ontology_graph.json` in the app directory
2. **Ask questions** - Use natural language to query the ontology (e.g., "What data should I use to predict customer churn?")
3. **Review recommendations** - Get structured data recommendations with reasoning
4. **Generate SQL** - Use the provided SQL scaffold as a starting point

## Graph Data Format

The application expects `ontology_graph.json` in the following format:

```json
{
  "nodes": [
    {
      "id": "table_name",
      "type": "feature_table|label_table|entity_master|lookup",
      "entity_key": "key_column",
      "candidate_features": ["col1", "col2"],
      "candidate_targets": ["target_col"]
    }
  ],
  "edges": [
    {
      "source": "table1",
      "target": "table2",
      "relationship": "joinable_on|entity_of",
      "key": "join_key",
      "confidence": "high|medium|low"
    }
  ]
}
```

## Testing

```bash
# Test OpenAI API connection and agent logic
python test_agent.py
```

This will verify:
- OpenAI API connectivity
- Graph data loading
- Agent query processing
- Response structure validation

## Troubleshooting

**API Key Issues:**
```bash
# Verify API key is set
echo $OPENAI_API_KEY

# Set permanently (add to ~/.bashrc or ~/.zshrc)
export OPENAI_API_KEY='sk-...'
```

**Missing Dependencies:**
```bash
pip install -r requirements.txt
# Or install individually
pip install streamlit openai
```

**Graph Data Not Found:**
- Ensure `ontology_graph.json` exists in the app directory
- Validate JSON syntax using `python -m json.tool ontology_graph.json`

## Architecture

- **Frontend:** Streamlit for interactive UI
- **AI Agent:** OpenAI GPT-4o with structured JSON output
- **Graph Model:** NetworkX for backend computation
- **Visualization:** streamlit-agraph for interactive graphs

## Configuration

Key parameters in `app.py`:

```python
model='gpt-4o'              # OpenAI model
temperature=0.0             # Deterministic outputs
response_format={'type': 'json_object'}  # Guaranteed valid JSON
```

## License

See LICENSE file for details.

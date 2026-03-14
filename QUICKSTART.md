# Quick Start Guide - Databricks Ontology Copilot

## 30-Second Setup

```bash
# 1. Navigate to project
cd ~/DatabricksOntology/app

# 2. Activate environment
source ../venv/bin/activate

# 3. Set API key (optional - demo mode works without it)
export OPENAI_API_KEY='sk-...'  # Replace with your key

# 4. Test setup
python test_integration.py

# 5. Run app
streamlit run app.py
```

App opens at: http://localhost:8501

## What You'll See

1. **Graph Visualization** - Interactive knowledge graph with color-coded nodes
2. **Agent Query Interface** - Natural language query system
   - Text input for prediction questions
   - AI-powered recommendations
   - SQL scaffold generation

## Try This Query

```
What data should I use to predict target_outcome?
```

**Expected Result:**
- Target column recommendation
- Feature tables with join keys
- Confidence scores
- SQL scaffold

## File Overview

```
app/
├── app.py                  # Main Streamlit application
├── ontology_graph.json     # Graph data (stub provided)
├── test_agent.py           # API connectivity test
├── test_integration.py     # Integration test suite
├── swap_graph_data.py      # Data swap utility
├── requirements.txt        # Python dependencies
├── setup.sh                # Automated setup
└── README.md               # Full documentation
```

## Troubleshooting

**"Module not found"**
```bash
source ../venv/bin/activate
pip install -r requirements.txt
```

**"API key not set"**
```bash
export OPENAI_API_KEY='sk-...'
# Verify: echo $OPENAI_API_KEY

# Alternative: Use demo mode in the app (cached responses)
```

**"Graph not loading"**
```bash
# Check file exists
ls -la ontology_graph.json

# Validate JSON
python -m json.tool ontology_graph.json
```

## Demo Mode

Enable the "Demo Controls" section in the app to use cached responses without requiring an API key. This is useful for testing and demonstrations.

## Documentation

- **Full Setup Guide:** [app/README.md](app/README.md)
- **Implementation Details:** [agentcontext/IMPLEMENTATION_COMPLETE.md](agentcontext/IMPLEMENTATION_COMPLETE.md)
- **Executive Summary:** [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)

## Testing

```bash
# Run integration tests
python test_integration.py

# Test API connectivity (requires API key)
python test_agent.py
```

## Architecture

- **Frontend:** Streamlit
- **Graph Visualization:** streamlit-agraph
- **AI Agent:** OpenAI GPT-4o
- **Graph Model:** NetworkX

---

For detailed configuration and usage instructions, see [app/README.md](app/README.md).

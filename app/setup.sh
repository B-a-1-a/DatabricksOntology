#!/bin/bash
# Setup script for Databricks Ontology Copilot

set -e

echo "🚀 Setting up Databricks Ontology Copilot..."

# Check if uv is installed
if ! command -v uv >/dev/null 2>&1; then
    echo "❌ uv is not installed"
    echo "   Install it from: https://docs.astral.sh/uv/getting-started/installation/"
    exit 1
fi

# Check if venv exists
if [ ! -d "../venv" ]; then
    echo "📦 Creating virtual environment..."
    uv venv ../venv
fi

# Activate venv
echo "🔧 Activating virtual environment..."
source ../venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
uv pip install -r requirements.txt --quiet

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Set your OpenAI API key:"
echo "     export OPENAI_API_KEY='sk-...'"
echo ""
echo "  2. Test the setup:"
echo "     uv run test_agent.py"
echo ""
echo "  3. Run the app:"
echo "     uv run streamlit run app.py"
echo ""

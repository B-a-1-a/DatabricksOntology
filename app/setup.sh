#!/bin/bash
# Setup script for Databricks Ontology Copilot

set -e

echo "🚀 Setting up Databricks Ontology Copilot..."

# Check if venv exists
if [ ! -d "../venv" ]; then
    echo "📦 Creating virtual environment..."
    cd .. && python3 -m venv venv && cd app
fi

# Activate venv
echo "🔧 Activating virtual environment..."
source ../venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip --quiet

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt --quiet

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Set your OpenAI API key:"
echo "     export OPENAI_API_KEY='sk-...'"
echo ""
echo "  2. Test the setup:"
echo "     python test_agent.py"
echo ""
echo "  3. Run the app:"
echo "     streamlit run app.py"
echo ""

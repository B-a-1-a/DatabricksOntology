"""
Test script for OpenAI API integration with ontology graph
Run this before building the full Streamlit app to verify API access
"""

import json
import os
from openai import OpenAI

def test_api_connection():
    """Test basic OpenAI API connectivity"""
    print("Testing OpenAI API connection...")

    # Check for API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY environment variable not set")
        print("   Run: export OPENAI_API_KEY='sk-...'")
        return False

    print(f"✓ API key found: {api_key[:10]}...")

    try:
        client = OpenAI()
        response = client.chat.completions.create(
            model='gpt-4o',
            messages=[{'role': 'user', 'content': 'Say hi in JSON format'}],
            response_format={'type': 'json_object'},
            max_tokens=50
        )
        result = json.loads(response.choices[0].message.content)
        print(f"✓ API test passed: {result}")
        return True
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

def test_ontology_query():
    """Test querying the ontology graph with OpenAI"""
    print("\nTesting ontology query...")

    # Load stub graph
    try:
        with open('ontology_graph.json', 'r') as f:
            graph = json.load(f)
        print(f"✓ Loaded graph with {len(graph['nodes'])} nodes and {len(graph['edges'])} edges")
    except Exception as e:
        print(f"❌ Failed to load graph: {e}")
        return False

    # Test query
    test_question = "What data should I use to predict target_outcome?"
    print(f"  Query: '{test_question}'")

    try:
        client = OpenAI()
        response = client.chat.completions.create(
            model='gpt-4o',
            messages=[
                {
                    'role': 'system',
                    'content': '''You are an ontology traversal agent. You have a knowledge graph of Databricks data assets as JSON. Answer the user's question by traversing the graph. Return ONLY valid JSON with this schema:
{
  "target": {"table": str, "column": str, "reason": str},
  "features": [{"table": str, "columns": [str], "join_key": str, "confidence": str, "reason": str}],
  "gaps": str
}
Only recommend tables and columns that exist in the graph JSON. Never invent assets. If confidence is low, say so in gaps.'''
                },
                {
                    'role': 'user',
                    'content': f'Graph: {json.dumps(graph)}\n\nQuestion: {test_question}'
                }
            ],
            response_format={'type': 'json_object'},
            temperature=0.0
        )

        result = json.loads(response.choices[0].message.content)
        print("\n✓ Agent response:")
        print(json.dumps(result, indent=2))

        # Validate response structure
        if 'target' in result and 'features' in result and 'gaps' in result:
            print("\n✓ Response has correct structure")
            return True
        else:
            print("\n❌ Response missing required fields")
            return False

    except Exception as e:
        print(f"❌ Query failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("OpenAI API Test Script")
    print("=" * 60)

    # Run tests
    api_ok = test_api_connection()
    if api_ok:
        query_ok = test_ontology_query()

        if query_ok:
            print("\n" + "=" * 60)
            print("✅ ALL TESTS PASSED - Ready to build Streamlit app")
            print("=" * 60)
        else:
            print("\n" + "=" * 60)
            print("⚠️  API works but query logic needs adjustment")
            print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ Fix API key before proceeding")
        print("=" * 60)

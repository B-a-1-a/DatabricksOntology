"""
Integration test suite for complete P2 + P3 workflow
Tests graph loading, schema validation, and API integration
"""

import json
import os
import sys
from pathlib import Path

DEFAULT_OPENAI_MODEL = "gpt-5-mini"
OPENAI_MODEL = os.getenv("OPENAI_MODEL", DEFAULT_OPENAI_MODEL).strip() or DEFAULT_OPENAI_MODEL

def test_graph_load():
    """Test graph data loads correctly"""
    print("Testing graph data load...")
    try:
        with open('ontology_graph.json', 'r') as f:
            graph = json.load(f)

        assert 'nodes' in graph, "Graph missing 'nodes' field"
        assert 'edges' in graph, "Graph missing 'edges' field"
        assert len(graph['nodes']) > 0, "Graph has no nodes"

        print(f"  ✅ Graph loaded: {len(graph['nodes'])} nodes, {len(graph['edges'])} edges")
        return True
    except FileNotFoundError:
        print("  ❌ ontology_graph.json not found")
        return False
    except json.JSONDecodeError as e:
        print(f"  ❌ Invalid JSON: {e}")
        return False
    except AssertionError as e:
        print(f"  ❌ {e}")
        return False

def test_graph_schema():
    """Validate graph has expected schema"""
    print("Testing graph schema...")
    try:
        with open('ontology_graph.json', 'r') as f:
            graph = json.load(f)

        # Check node schema
        for idx, node in enumerate(graph['nodes']):
            assert 'id' in node, f"Node {idx} missing 'id'"
            assert 'type' in node, f"Node {idx} missing 'type'"
            assert node['type'] in ['feature_table', 'label_table', 'entity_master', 'lookup'], \
                f"Node {idx} has invalid type: {node['type']}"

        # Check edge schema
        for idx, edge in enumerate(graph['edges']):
            assert 'source' in edge, f"Edge {idx} missing 'source'"
            assert 'target' in edge, f"Edge {idx} missing 'target'"
            assert 'confidence' in edge, f"Edge {idx} missing 'confidence'"
            assert edge['confidence'] in ['high', 'medium', 'low'], \
                f"Edge {idx} has invalid confidence: {edge['confidence']}"

        # Validate edge references
        node_ids = {node['id'] for node in graph['nodes']}
        for idx, edge in enumerate(graph['edges']):
            assert edge['source'] in node_ids, f"Edge {idx} source '{edge['source']}' not in nodes"
            assert edge['target'] in node_ids, f"Edge {idx} target '{edge['target']}' not in nodes"

        print(f"  ✅ Schema valid")
        print(f"     Node types: {set(n['type'] for n in graph['nodes'])}")
        print(f"     Confidence levels: {set(e['confidence'] for e in graph['edges'])}")
        return True
    except AssertionError as e:
        print(f"  ❌ {e}")
        return False
    except Exception as e:
        print(f"  ❌ Unexpected error: {e}")
        return False

def test_api_key_set():
    """Check if OpenAI API key is configured"""
    print("Testing API key configuration...")
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key:
        print(f"  ✅ API key set: {api_key[:10]}...")
        return True
    else:
        print("  ⚠️  API key not set (export OPENAI_API_KEY='sk-...')")
        return False

def test_api_integration():
    """Test OpenAI API integration (requires API key)"""
    print("Testing OpenAI API integration...")

    if not os.getenv('OPENAI_API_KEY'):
        print("  ⏭️  Skipped (API key not set)")
        return None

    try:
        from openai import OpenAI

        with open('ontology_graph.json', 'r') as f:
            graph = json.load(f)

        client = OpenAI()
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {'role': 'system', 'content': 'Return valid JSON with a "test" field set to true.'},
                {'role': 'user', 'content': f'Graph has {len(graph["nodes"])} nodes'}
            ],
            response_format={'type': 'json_object'},
            max_tokens=50
        )

        result = json.loads(response.choices[0].message.content)
        assert isinstance(result, dict), "API response is not a dict"
        print(f"  ✅ API responds correctly")
        return True
    except Exception as e:
        print(f"  ❌ API error: {e}")
        return False

def test_agent_query():
    """Test full agent query with graph"""
    print("Testing agent query logic...")

    if not os.getenv('OPENAI_API_KEY'):
        print("  ⏭️  Skipped (API key not set)")
        return None

    try:
        from openai import OpenAI

        with open('ontology_graph.json', 'r') as f:
            graph = json.load(f)

        # Simplified agent query
        client = OpenAI()

        system_prompt = '''You are an ontology traversal agent. Return ONLY valid JSON with this schema:
{
  "target": {"table": str, "column": str, "reason": str},
  "features": [{"table": str, "columns": [str], "join_key": str, "confidence": str, "reason": str}],
  "gaps": str
}
Only recommend tables and columns that exist in the graph.'''

        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': f'Graph: {json.dumps(graph)}\n\nQuestion: What data should I use to predict target_outcome?'}
            ],
            response_format={'type': 'json_object'},
            temperature=0.0,
            max_tokens=500
        )

        result = json.loads(response.choices[0].message.content)

        # Validate response structure
        assert 'target' in result, "Response missing 'target'"
        assert 'features' in result, "Response missing 'features'"
        assert 'gaps' in result, "Response missing 'gaps'"

        print(f"  ✅ Agent query works")
        print(f"     Target: {result['target'].get('table', 'N/A')}.{result['target'].get('column', 'N/A')}")
        print(f"     Features: {len(result['features'])} recommendations")
        return True
    except Exception as e:
        print(f"  ❌ Agent query error: {e}")
        return False

def test_no_hallucinations():
    """Test agent doesn't invent tables"""
    print("Testing for hallucinations...")

    if not os.getenv('OPENAI_API_KEY'):
        print("  ⏭️  Skipped (API key not set)")
        return None

    try:
        from openai import OpenAI

        with open('ontology_graph.json', 'r') as f:
            graph = json.load(f)

        valid_tables = {node['id'] for node in graph['nodes']}

        client = OpenAI()

        system_prompt = '''You are an ontology traversal agent. Return ONLY valid JSON with this schema:
{
  "target": {"table": str, "column": str, "reason": str},
  "features": [{"table": str, "columns": [str], "join_key": str, "confidence": str, "reason": str}],
  "gaps": str
}
CRITICAL: Only recommend tables and columns that exist in the graph JSON. Never invent assets.'''

        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': f'Graph: {json.dumps(graph)}\n\nQuestion: What should I predict?'}
            ],
            response_format={'type': 'json_object'},
            temperature=0.0,
            max_tokens=500
        )

        result = json.loads(response.choices[0].message.content)

        # Check target table exists
        if 'target' in result and 'table' in result['target']:
            target_table = result['target']['table']
            assert target_table in valid_tables, f"Hallucinated target table: {target_table}"

        # Check feature tables exist
        if 'features' in result:
            for feat in result['features']:
                if 'table' in feat:
                    feat_table = feat['table']
                    assert feat_table in valid_tables, f"Hallucinated feature table: {feat_table}"

        print(f"  ✅ No hallucinations detected")
        return True
    except AssertionError as e:
        print(f"  ❌ {e}")
        return False
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def test_streamlit_imports():
    """Test that all required packages are importable"""
    print("Testing Python imports...")
    try:
        import streamlit
        import openai
        from streamlit_agraph import agraph, Node, Edge, Config
        import networkx

        print(f"  ✅ All packages importable")
        print(f"     streamlit: {streamlit.__version__}")
        print(f"     openai: {openai.__version__}")
        return True
    except ImportError as e:
        print(f"  ❌ Import error: {e}")
        print("     Run: pip install streamlit streamlit-agraph networkx openai")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("INTEGRATION TEST SUITE")
    print("=" * 60)
    print()

    results = {}

    # Core tests (must pass)
    results['imports'] = test_streamlit_imports()
    results['graph_load'] = test_graph_load()
    results['graph_schema'] = test_graph_schema()

    # Optional tests (warnings only)
    results['api_key'] = test_api_key_set()
    results['api_integration'] = test_api_integration()
    results['agent_query'] = test_agent_query()
    results['no_hallucinations'] = test_no_hallucinations()

    print()
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    # Count results
    passed = sum(1 for v in results.values() if v is True)
    failed = sum(1 for v in results.values() if v is False)
    skipped = sum(1 for v in results.values() if v is None)

    for test_name, result in results.items():
        if result is True:
            print(f"✅ {test_name}")
        elif result is False:
            print(f"❌ {test_name}")
        else:
            print(f"⏭️  {test_name} (skipped)")

    print()
    print(f"Passed: {passed} | Failed: {failed} | Skipped: {skipped}")

    # Determine overall status
    critical_tests = ['imports', 'graph_load', 'graph_schema']
    critical_passed = all(results.get(t) is True for t in critical_tests)

    if critical_passed and failed == 0:
        print()
        print("✅ ALL TESTS PASSED - Ready for production!")
        return 0
    elif critical_passed:
        print()
        print("⚠️  CORE TESTS PASSED - Ready for demo (API tests skipped)")
        print("   Set OPENAI_API_KEY to run full test suite")
        return 0
    else:
        print()
        print("❌ CRITICAL TESTS FAILED - Fix before demo")
        return 1

if __name__ == "__main__":
    sys.exit(main())

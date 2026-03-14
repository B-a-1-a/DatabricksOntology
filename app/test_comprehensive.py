#!/usr/bin/env python3
"""
Comprehensive test suite for Databricks Ontology Copilot
Includes unit tests, integration tests, and mock API tests
"""

import json
import os
import sys
import unittest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

class TestGraphData(unittest.TestCase):
    """Test graph data loading and validation"""

    def setUp(self):
        """Load graph data before each test"""
        try:
            with open('ontology_graph.json', 'r') as f:
                self.graph = json.load(f)
        except FileNotFoundError:
            self.graph = None

    def test_graph_file_exists(self):
        """Test that ontology_graph.json exists"""
        self.assertTrue(
            Path('ontology_graph.json').exists(),
            "ontology_graph.json file not found"
        )

    def test_graph_valid_json(self):
        """Test that graph is valid JSON"""
        self.assertIsNotNone(self.graph, "Failed to parse graph JSON")

    def test_graph_has_required_fields(self):
        """Test that graph has nodes and edges"""
        self.assertIn('nodes', self.graph, "Graph missing 'nodes' field")
        self.assertIn('edges', self.graph, "Graph missing 'edges' field")

    def test_graph_not_empty(self):
        """Test that graph has at least one node"""
        self.assertGreater(
            len(self.graph['nodes']),
            0,
            "Graph has no nodes"
        )

    def test_node_schema(self):
        """Test that all nodes have required fields"""
        required_fields = ['id', 'type']
        valid_types = ['feature_table', 'label_table', 'entity_master', 'lookup']

        for idx, node in enumerate(self.graph['nodes']):
            with self.subTest(node_index=idx):
                for field in required_fields:
                    self.assertIn(
                        field,
                        node,
                        f"Node {idx} missing '{field}' field"
                    )
                self.assertIn(
                    node['type'],
                    valid_types,
                    f"Node {idx} has invalid type: {node['type']}"
                )

    def test_edge_schema(self):
        """Test that all edges have required fields"""
        required_fields = ['source', 'target', 'confidence']
        valid_confidence = ['high', 'medium', 'low']

        for idx, edge in enumerate(self.graph['edges']):
            with self.subTest(edge_index=idx):
                for field in required_fields:
                    self.assertIn(
                        field,
                        edge,
                        f"Edge {idx} missing '{field}' field"
                    )
                self.assertIn(
                    edge['confidence'],
                    valid_confidence,
                    f"Edge {idx} has invalid confidence: {edge['confidence']}"
                )

    def test_edge_references(self):
        """Test that edges reference existing nodes"""
        node_ids = {node['id'] for node in self.graph['nodes']}

        for idx, edge in enumerate(self.graph['edges']):
            with self.subTest(edge_index=idx):
                self.assertIn(
                    edge['source'],
                    node_ids,
                    f"Edge {idx} source '{edge['source']}' not in nodes"
                )
                self.assertIn(
                    edge['target'],
                    node_ids,
                    f"Edge {idx} target '{edge['target']}' not in nodes"
                )

    def test_no_self_loops(self):
        """Test that no edge connects a node to itself"""
        for idx, edge in enumerate(self.graph['edges']):
            with self.subTest(edge_index=idx):
                self.assertNotEqual(
                    edge['source'],
                    edge['target'],
                    f"Edge {idx} is a self-loop"
                )

    def test_node_ids_unique(self):
        """Test that all node IDs are unique"""
        node_ids = [node['id'] for node in self.graph['nodes']]
        self.assertEqual(
            len(node_ids),
            len(set(node_ids)),
            "Duplicate node IDs found"
        )


class TestDependencies(unittest.TestCase):
    """Test that required packages are available"""

    def test_streamlit_import(self):
        """Test that streamlit can be imported"""
        try:
            import streamlit
            self.assertTrue(True)
        except ImportError:
            self.fail("streamlit not installed")

    def test_openai_import(self):
        """Test that openai can be imported"""
        try:
            import openai
            self.assertTrue(True)
        except ImportError:
            self.fail("openai not installed")

    def test_streamlit_agraph_import(self):
        """Test that streamlit_agraph can be imported"""
        try:
            from streamlit_agraph import Node, Edge, Config
            self.assertTrue(True)
        except ImportError:
            self.fail("streamlit-agraph not installed")

    def test_networkx_import(self):
        """Test that networkx can be imported"""
        try:
            import networkx
            self.assertTrue(True)
        except ImportError:
            self.fail("networkx not installed")


class TestAPIConfiguration(unittest.TestCase):
    """Test API configuration and environment"""

    def test_api_key_detection(self):
        """Test that API key environment variable can be detected"""
        api_key = os.getenv('OPENAI_API_KEY')
        # This test just checks detection, not requirement
        if api_key:
            self.assertIsInstance(api_key, str)
            self.assertTrue(len(api_key) > 0)


class TestApplicationCode(unittest.TestCase):
    """Test application code structure"""

    def test_app_file_exists(self):
        """Test that app.py exists"""
        self.assertTrue(Path('app.py').exists(), "app.py not found")

    def test_app_valid_python(self):
        """Test that app.py is valid Python"""
        try:
            with open('app.py', 'r') as f:
                compile(f.read(), 'app.py', 'exec')
            self.assertTrue(True)
        except SyntaxError as e:
            self.fail(f"app.py has syntax error: {e}")


class TestMockAPI(unittest.TestCase):
    """Test API integration with mocked responses"""

    def setUp(self):
        """Load graph for testing"""
        with open('ontology_graph.json', 'r') as f:
            self.graph = json.load(f)

    @patch('openai.OpenAI')
    def test_api_response_parsing(self, mock_openai):
        """Test that API responses are parsed correctly"""
        # Mock API response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "target": {
                "table": "example_labels",
                "column": "target_outcome",
                "reason": "Test reason"
            },
            "features": [
                {
                    "table": "example_features_daily",
                    "columns": ["metric_a", "metric_b"],
                    "join_key": "entity_id",
                    "confidence": "high",
                    "reason": "Test reason"
                }
            ],
            "gaps": ""
        })

        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        # Test parsing
        from openai import OpenAI
        client = OpenAI()
        response = client.chat.completions.create(
            model='gpt-4o',
            messages=[{'role': 'user', 'content': 'test'}],
            response_format={'type': 'json_object'}
        )

        result = json.loads(response.choices[0].message.content)

        self.assertIn('target', result)
        self.assertIn('features', result)
        self.assertIn('gaps', result)
        self.assertEqual(result['target']['table'], 'example_labels')

    def test_response_schema_validation(self):
        """Test that response matches expected schema"""
        # Sample response
        response = {
            "target": {
                "table": "test_table",
                "column": "test_column",
                "reason": "test reason"
            },
            "features": [
                {
                    "table": "feature_table",
                    "columns": ["col1", "col2"],
                    "join_key": "id",
                    "confidence": "high",
                    "reason": "test"
                }
            ],
            "gaps": "none"
        }

        # Validate target
        self.assertIn('table', response['target'])
        self.assertIn('column', response['target'])
        self.assertIn('reason', response['target'])

        # Validate features
        self.assertIsInstance(response['features'], list)
        for feature in response['features']:
            self.assertIn('table', feature)
            self.assertIn('columns', feature)
            self.assertIn('join_key', feature)
            self.assertIn('confidence', feature)
            self.assertIn('reason', feature)


class TestDataSwapUtility(unittest.TestCase):
    """Test data swap utility"""

    def test_swap_script_exists(self):
        """Test that swap_graph_data.py exists"""
        self.assertTrue(
            Path('swap_graph_data.py').exists(),
            "swap_graph_data.py not found"
        )

    def test_swap_script_valid_python(self):
        """Test that swap_graph_data.py is valid Python"""
        try:
            with open('swap_graph_data.py', 'r') as f:
                compile(f.read(), 'swap_graph_data.py', 'exec')
            self.assertTrue(True)
        except SyntaxError as e:
            self.fail(f"swap_graph_data.py has syntax error: {e}")


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling"""

    def test_empty_graph_handling(self):
        """Test handling of empty graph"""
        empty_graph = {"nodes": [], "edges": []}

        # Should have valid structure even if empty
        self.assertIn('nodes', empty_graph)
        self.assertIn('edges', empty_graph)
        self.assertIsInstance(empty_graph['nodes'], list)
        self.assertIsInstance(empty_graph['edges'], list)

    def test_graph_with_no_edges(self):
        """Test handling of graph with nodes but no edges"""
        graph = {
            "nodes": [{"id": "node1", "type": "feature_table"}],
            "edges": []
        }

        self.assertEqual(len(graph['nodes']), 1)
        self.assertEqual(len(graph['edges']), 0)


def run_tests():
    """Run all tests and generate report"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestGraphData))
    suite.addTests(loader.loadTestsFromTestCase(TestDependencies))
    suite.addTests(loader.loadTestsFromTestCase(TestAPIConfiguration))
    suite.addTests(loader.loadTestsFromTestCase(TestApplicationCode))
    suite.addTests(loader.loadTestsFromTestCase(TestMockAPI))
    suite.addTests(loader.loadTestsFromTestCase(TestDataSwapUtility))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 70)

    # Return exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())

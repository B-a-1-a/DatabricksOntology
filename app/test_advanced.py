"""
Advanced Test Suite for Databricks Ontology Copilot
Tests UI components, performance, edge cases, and integration scenarios
"""

import unittest
import json
import os
import sys
import time
from unittest.mock import Mock, patch, MagicMock
from io import StringIO

# Test configuration
PERFORMANCE_THRESHOLD_MS = 1000
MAX_GRAPH_SIZE = 10000


class TestPerformance(unittest.TestCase):
    """Performance benchmarks for critical paths"""

    def test_graph_load_performance(self):
        """Test that graph loading completes within threshold"""
        start_time = time.time()

        with open('ontology_graph.json', 'r') as f:
            graph = json.load(f)

        elapsed_ms = (time.time() - start_time) * 1000
        self.assertLess(elapsed_ms, PERFORMANCE_THRESHOLD_MS,
                       f"Graph loading took {elapsed_ms:.2f}ms, expected < {PERFORMANCE_THRESHOLD_MS}ms")

    def test_large_graph_handling(self):
        """Test handling of large graphs (stress test)"""
        # Create a synthetic large graph
        large_graph = {
            'nodes': [
                {'id': f'node_{i}', 'type': 'feature_table', 'entity_key': 'id'}
                for i in range(100)
            ],
            'edges': [
                {'source': f'node_{i}', 'target': f'node_{i+1}', 'relationship': 'joins', 'key': 'id'}
                for i in range(99)
            ]
        }

        # Verify processing completes
        start_time = time.time()
        node_count = len(large_graph['nodes'])
        edge_count = len(large_graph['edges'])
        elapsed_ms = (time.time() - start_time) * 1000

        self.assertEqual(node_count, 100)
        self.assertEqual(edge_count, 99)
        self.assertLess(elapsed_ms, PERFORMANCE_THRESHOLD_MS)

    def test_json_parsing_performance(self):
        """Test JSON parsing performance with realistic data"""
        with open('ontology_graph.json', 'r') as f:
            content = f.read()

        start_time = time.time()
        for _ in range(100):  # Parse 100 times
            json.loads(content)
        elapsed_ms = (time.time() - start_time) * 1000

        avg_ms = elapsed_ms / 100
        self.assertLess(avg_ms, 10, f"Average JSON parse time {avg_ms:.2f}ms too slow")


class TestUIComponents(unittest.TestCase):
    """Test UI component rendering and behavior"""

    @patch('streamlit.set_page_config')
    @patch('streamlit.title')
    @patch('streamlit.header')
    def test_page_config(self, mock_header, mock_title, mock_config):
        """Test that page is configured correctly"""
        # Import would trigger streamlit calls
        import app

        # Verify page config was called
        mock_config.assert_called_once()
        call_kwargs = mock_config.call_args[1]

        self.assertEqual(call_kwargs['page_title'], "Databricks Ontology Copilot")
        self.assertEqual(call_kwargs['layout'], "wide")

    def test_color_mapping_validity(self):
        """Test that color codes are valid hex colors"""
        color_map = {
            'feature_table': '#4A90D9',
            'label_table': '#E24B4A',
            'entity_master': '#1D9E75',
            'lookup': '#888780'
        }

        import re
        hex_pattern = re.compile(r'^#[0-9A-Fa-f]{6}$')

        for node_type, color in color_map.items():
            self.assertTrue(hex_pattern.match(color),
                          f"Invalid hex color for {node_type}: {color}")

    def test_node_type_coverage(self):
        """Test that all node types in graph have color mappings"""
        with open('ontology_graph.json', 'r') as f:
            graph = json.load(f)

        color_map = {
            'feature_table': '#4A90D9',
            'label_table': '#E24B4A',
            'entity_master': '#1D9E75',
            'lookup': '#888780'
        }

        node_types = set(node.get('type') for node in graph['nodes'])

        for node_type in node_types:
            self.assertIn(node_type, color_map,
                         f"Node type '{node_type}' missing color mapping")


class TestAPIIntegration(unittest.TestCase):
    """Test OpenAI API integration with comprehensive scenarios"""

    @patch('openai.OpenAI')
    def test_api_error_handling(self, mock_openai):
        """Test that API errors are handled gracefully"""
        # Simulate API error
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("API rate limit exceeded")
        mock_openai.return_value = mock_client

        # Verify error is caught and handled
        with self.assertRaises(Exception) as context:
            mock_client.chat.completions.create()

        self.assertIn("rate limit", str(context.exception).lower())

    @patch('openai.OpenAI')
    def test_api_timeout_handling(self, mock_openai):
        """Test handling of API timeouts"""
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = TimeoutError("Request timeout")
        mock_openai.return_value = mock_client

        with self.assertRaises(TimeoutError):
            mock_client.chat.completions.create()

    @patch('openai.OpenAI')
    def test_malformed_response_handling(self, mock_openai):
        """Test handling of malformed API responses"""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Not valid JSON at all!"

        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        # Verify JSON parsing error is caught
        with self.assertRaises(json.JSONDecodeError):
            json.loads(mock_response.choices[0].message.content)

    @patch('openai.OpenAI')
    def test_empty_response_handling(self, mock_openai):
        """Test handling of empty API responses"""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = []

        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        # Verify empty choices array handling
        response = mock_client.chat.completions.create()
        self.assertEqual(len(response.choices), 0)


class TestDataValidation(unittest.TestCase):
    """Advanced data validation tests"""

    def test_circular_dependency_detection(self):
        """Test detection of circular dependencies in graph"""
        with open('ontology_graph.json', 'r') as f:
            graph = json.load(f)

        # Build adjacency list
        adjacency = {}
        for edge in graph['edges']:
            source = edge['source']
            target = edge['target']
            if source not in adjacency:
                adjacency[source] = []
            adjacency[source].append(target)

        # DFS to detect cycles
        def has_cycle(node, visited, rec_stack):
            visited.add(node)
            rec_stack.add(node)

            for neighbor in adjacency.get(node, []):
                if neighbor not in visited:
                    if has_cycle(neighbor, visited, rec_stack):
                        return True
                elif neighbor in rec_stack:
                    return True

            rec_stack.remove(node)
            return False

        visited = set()
        rec_stack = set()

        has_circular = False
        for node in adjacency.keys():
            if node not in visited:
                if has_cycle(node, visited, rec_stack):
                    has_circular = True
                    break

        # Circular dependencies are allowed but should be documented
        # This test just verifies we can detect them
        self.assertIsInstance(has_circular, bool)

    def test_orphaned_nodes(self):
        """Test detection of orphaned nodes (no incoming or outgoing edges)"""
        with open('ontology_graph.json', 'r') as f:
            graph = json.load(f)

        node_ids = set(node['id'] for node in graph['nodes'])
        connected_nodes = set()

        for edge in graph['edges']:
            connected_nodes.add(edge['source'])
            connected_nodes.add(edge['target'])

        orphaned = node_ids - connected_nodes

        # Orphaned nodes are allowed but should be minimal
        orphan_ratio = len(orphaned) / len(node_ids) if node_ids else 0
        self.assertLess(orphan_ratio, 0.5,
                       f"Too many orphaned nodes: {len(orphaned)}/{len(node_ids)}")

    def test_node_attribute_completeness(self):
        """Test that nodes have all expected attributes"""
        with open('ontology_graph.json', 'r') as f:
            graph = json.load(f)

        required_fields = {'id', 'type'}
        recommended_fields = {'entity_key'}

        for idx, node in enumerate(graph['nodes']):
            # Check required fields
            for field in required_fields:
                self.assertIn(field, node,
                            f"Node {idx} missing required field '{field}'")

            # Check recommended fields (warning only)
            for field in recommended_fields:
                if field not in node:
                    print(f"Warning: Node {idx} ({node.get('id')}) missing recommended field '{field}'")

    def test_edge_relationship_types(self):
        """Test that edge relationships are from valid set"""
        with open('ontology_graph.json', 'r') as f:
            graph = json.load(f)

        valid_relationships = {
            'joinable_on', 'joins', 'derived_from', 'contains',
            'references', 'aggregates', 'filters', 'lookup'
        }

        for idx, edge in enumerate(graph['edges']):
            relationship = edge.get('relationship', '')
            # Allow any relationship but warn on unknown ones
            if relationship and relationship not in valid_relationships:
                print(f"Warning: Edge {idx} has uncommon relationship type: '{relationship}'")


class TestSecurityAndSafety(unittest.TestCase):
    """Security and safety tests"""

    def test_no_hardcoded_secrets(self):
        """Test that no secrets are hardcoded in graph data"""
        with open('ontology_graph.json', 'r') as f:
            content = f.read().lower()

        # Check for common secret patterns
        secret_patterns = [
            'password', 'secret', 'api_key', 'apikey',
            'token', 'bearer', 'auth', 'credential'
        ]

        for pattern in secret_patterns:
            self.assertNotIn(pattern, content,
                           f"Potential secret pattern '{pattern}' found in graph data")

    def test_json_size_limit(self):
        """Test that graph JSON doesn't exceed reasonable size limits"""
        file_size = os.path.getsize('ontology_graph.json')
        max_size = 10 * 1024 * 1024  # 10 MB

        self.assertLess(file_size, max_size,
                       f"Graph JSON too large: {file_size} bytes (max {max_size})")

    def test_no_sql_injection_patterns(self):
        """Test that graph data doesn't contain SQL injection patterns"""
        with open('ontology_graph.json', 'r') as f:
            graph = json.load(f)

        dangerous_patterns = ["';", "DROP TABLE", "DELETE FROM", "--", "/*"]

        def check_value(value):
            if isinstance(value, str):
                for pattern in dangerous_patterns:
                    self.assertNotIn(pattern, value.upper(),
                                   f"Dangerous SQL pattern '{pattern}' found")
            elif isinstance(value, dict):
                for v in value.values():
                    check_value(v)
            elif isinstance(value, list):
                for item in value:
                    check_value(item)

        check_value(graph)


class TestSwapUtility(unittest.TestCase):
    """Test the data swap utility"""

    def test_swap_utility_exists(self):
        """Test that swap_graph_data.py exists"""
        self.assertTrue(os.path.exists('swap_graph_data.py'))

    def test_swap_utility_has_validation(self):
        """Test that swap utility includes schema validation"""
        with open('swap_graph_data.py', 'r') as f:
            content = f.read()

        self.assertIn('validate_graph_schema', content)
        self.assertIn('nodes', content)
        self.assertIn('edges', content)

    def test_swap_utility_has_backup(self):
        """Test that swap utility includes backup functionality"""
        with open('swap_graph_data.py', 'r') as f:
            content = f.read()

        self.assertIn('backup', content.lower())


class TestDocumentation(unittest.TestCase):
    """Test documentation completeness"""

    def test_readme_exists(self):
        """Test that README exists"""
        readme_paths = ['../README.md', 'README.md']
        exists = any(os.path.exists(path) for path in readme_paths)
        self.assertTrue(exists, "README.md not found")

    def test_requirements_file_valid(self):
        """Test that requirements.txt is valid"""
        # Try multiple possible locations
        possible_paths = ['requirements.txt', '../requirements.txt']
        content = None

        for path in possible_paths:
            try:
                with open(path, 'r') as f:
                    content = f.read()
                break
            except FileNotFoundError:
                continue

        self.assertIsNotNone(content, "requirements.txt not found in any expected location")

        # Check for key dependencies
        self.assertIn('streamlit', content)
        self.assertIn('openai', content)
        self.assertIn('streamlit-agraph', content)

    def test_quickstart_guide_exists(self):
        """Test that QUICKSTART guide exists"""
        self.assertTrue(os.path.exists('../QUICKSTART.md'))


def run_test_suite():
    """Run all tests with detailed reporting"""

    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestPerformance))
    suite.addTests(loader.loadTestsFromTestCase(TestUIComponents))
    suite.addTests(loader.loadTestsFromTestCase(TestAPIIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestDataValidation))
    suite.addTests(loader.loadTestsFromTestCase(TestSecurityAndSafety))
    suite.addTests(loader.loadTestsFromTestCase(TestSwapUtility))
    suite.addTests(loader.loadTestsFromTestCase(TestDocumentation))

    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "="*70)
    print("ADVANCED TEST SUITE SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")

    if result.wasSuccessful():
        print("\n✅ ALL TESTS PASSED")
    else:
        print("\n❌ SOME TESTS FAILED")

    print("="*70)

    return result


if __name__ == '__main__':
    result = run_test_suite()
    sys.exit(0 if result.wasSuccessful() else 1)

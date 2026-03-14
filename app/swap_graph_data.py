#!/usr/bin/env python3
"""
Data Swap Script for P1 Integration
Swaps ontology_graph.json when P1 delivers real data at 3:30 PM checkpoint

Usage:
    python swap_graph_data.py <path_to_new_graph.json>

Example:
    python swap_graph_data.py ../p1_deliverables/ontology_graph.json
"""

import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

def backup_current_graph():
    """Backup current graph with timestamp"""
    if not Path('ontology_graph.json').exists():
        print("⚠️  No existing graph to backup")
        return None

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"ontology_graph_backup_{timestamp}.json"

    shutil.copy('ontology_graph.json', backup_name)
    print(f"✅ Backed up current graph to: {backup_name}")
    return backup_name

def validate_graph_schema(filepath):
    """Validate graph has expected schema"""
    print(f"🔍 Validating schema of: {filepath}")

    try:
        with open(filepath, 'r') as f:
            graph = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}")

    # Required top-level fields
    if 'nodes' not in graph:
        raise ValueError("Missing 'nodes' field")
    if 'edges' not in graph:
        raise ValueError("Missing 'edges' field")

    if not isinstance(graph['nodes'], list):
        raise ValueError("'nodes' must be a list")
    if not isinstance(graph['edges'], list):
        raise ValueError("'edges' must be a list")

    # Validate nodes
    for idx, node in enumerate(graph['nodes']):
        if 'id' not in node:
            raise ValueError(f"Node {idx} missing 'id' field")
        if 'type' not in node:
            raise ValueError(f"Node {idx} missing 'type' field")
        if node['type'] not in ['feature_table', 'label_table', 'entity_master', 'lookup']:
            raise ValueError(f"Node {idx} has invalid type: {node['type']}")

    # Validate edges
    node_ids = {node['id'] for node in graph['nodes']}
    for idx, edge in enumerate(graph['edges']):
        if 'source' not in edge:
            raise ValueError(f"Edge {idx} missing 'source' field")
        if 'target' not in edge:
            raise ValueError(f"Edge {idx} missing 'target' field")
        if 'confidence' not in edge:
            raise ValueError(f"Edge {idx} missing 'confidence' field")

        # Validate references
        if edge['source'] not in node_ids:
            raise ValueError(f"Edge {idx} source '{edge['source']}' not in nodes")
        if edge['target'] not in node_ids:
            raise ValueError(f"Edge {idx} target '{edge['target']}' not in nodes")

    print(f"✅ Schema validated successfully")
    return graph

def show_graph_summary(graph):
    """Display summary of graph structure"""
    print("\n" + "=" * 60)
    print("GRAPH SUMMARY")
    print("=" * 60)

    # Node statistics
    node_types = {}
    for node in graph['nodes']:
        node_type = node['type']
        node_types[node_type] = node_types.get(node_type, 0) + 1

    print(f"Total Nodes: {len(graph['nodes'])}")
    for node_type, count in sorted(node_types.items()):
        print(f"  - {node_type}: {count}")

    # Edge statistics
    confidence_levels = {}
    for edge in graph['edges']:
        conf = edge['confidence']
        confidence_levels[conf] = confidence_levels.get(conf, 0) + 1

    print(f"\nTotal Edges: {len(graph['edges'])}")
    for conf, count in sorted(confidence_levels.items()):
        print(f"  - {conf} confidence: {count}")

    # Sample nodes
    print(f"\nSample Nodes:")
    for node in graph['nodes'][:5]:
        print(f"  - {node['id']} ({node['type']})")
    if len(graph['nodes']) > 5:
        print(f"  ... and {len(graph['nodes']) - 5} more")

    print("=" * 60 + "\n")

def swap_graph(new_graph_path):
    """Main swap logic"""
    new_graph_path = Path(new_graph_path)

    # Validate new graph exists
    if not new_graph_path.exists():
        print(f"❌ File not found: {new_graph_path}")
        return False

    print(f"📥 Loading new graph from: {new_graph_path}")

    # Validate schema
    try:
        new_graph = validate_graph_schema(new_graph_path)
    except Exception as e:
        print(f"❌ Schema validation failed: {e}")
        return False

    # Show what we're about to install
    show_graph_summary(new_graph)

    # Confirm swap
    print("⚠️  This will replace the current ontology_graph.json")
    response = input("Continue? [y/N]: ")
    if response.lower() not in ['y', 'yes']:
        print("❌ Swap cancelled")
        return False

    # Backup current graph
    backup_current_graph()

    # Install new graph
    shutil.copy(new_graph_path, 'ontology_graph.json')
    print(f"✅ New graph installed: ontology_graph.json")

    # Next steps
    print("\n" + "=" * 60)
    print("NEXT STEPS")
    print("=" * 60)
    print("1. Restart Streamlit to clear cache:")
    print("   pkill -f streamlit && streamlit run app.py")
    print()
    print("2. Test with real data queries")
    print()
    print("3. Verify agent doesn't hallucinate:")
    print("   python test_integration.py")
    print()
    print("4. Capture screenshots for demo backup:")
    print("   - Graph visualization")
    print("   - Agent recommendation")
    print("=" * 60)

    return True

def main():
    """Entry point"""
    if len(sys.argv) < 2:
        print("Usage: python swap_graph_data.py <path_to_new_graph.json>")
        print()
        print("Example:")
        print("  python swap_graph_data.py ../p1_deliverables/ontology_graph.json")
        print()
        print("This script will:")
        print("  1. Validate the new graph schema")
        print("  2. Backup the current graph (if exists)")
        print("  3. Install the new graph")
        print("  4. Show next steps for integration")
        sys.exit(1)

    new_graph_path = sys.argv[1]

    print("=" * 60)
    print("DATA SWAP SCRIPT - P1 INTEGRATION")
    print("=" * 60)
    print()

    success = swap_graph(new_graph_path)

    if success:
        print("\n✅ Graph swap completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Graph swap failed")
        sys.exit(1)

if __name__ == "__main__":
    main()

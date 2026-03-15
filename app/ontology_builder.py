"""
Ontology graph builder from crawled Databricks catalog metadata.

Converts structured metadata (schemas, tables, columns) into a
node/edge graph JSON compatible with the existing streamlit-agraph
visualization and agent query system.
"""


def classify_table_type(schema_name, table_name, columns, comment):
    """Classify a table's ontology type using schema/name/comment heuristics.

    Args:
        schema_name: Schema the table belongs to
        table_name: Table name
        columns: List of column dicts with 'name', 'data_type', 'comment'
        comment: Table comment string

    Returns:
        One of: 'feature_table', 'label_table', 'entity_master', 'lookup'
    """
    s = schema_name.lower()
    c = (comment or "").lower()

    if "feature" in s or "agent_feature" in s:
        return "feature_table"
    if "label" in c or "target" in c:
        return "label_table"
    if "dimension" in s or "dim" in s:
        return "entity_master"
    if "entit" in s or "identity" in s or "customer" in s:
        return "entity_master"
    if "fact" in s or "transaction" in s or "event" in s:
        return "feature_table"
    if "supply" in s or "channel" in s or "product" in s:
        return "entity_master"

    # Check column names for label/target indicators
    col_names = [col["name"].lower() for col in columns]
    if any("target" in n or "label" in n for n in col_names):
        return "label_table"

    return "lookup"


def _find_key_columns(columns):
    """Find columns that look like join keys (_id or _key suffix).

    Args:
        columns: List of column dicts

    Returns:
        List of column name strings that end in _id or _key
    """
    keys = []
    for col in columns:
        name = col["name"].lower()
        if name.endswith("_id") or name.endswith("_key") or name.endswith("_sk"):
            keys.append(col["name"])
    return keys


def build_ontology_graph(metadata):
    """Build an ontology graph from crawled catalog metadata.

    Creates nodes for each table and edges where tables share
    join-key columns (columns ending in _id, _key, or _sk).

    Args:
        metadata: Structured metadata dict from crawl_catalog_metadata()

    Returns:
        Dict with 'nodes' and 'edges' lists matching ontology_graph.json schema
    """
    nodes = []
    # Map of column_name -> list of (table_id, data_type) for join detection
    key_column_index = {}

    for schema in metadata.get("schemas", []):
        schema_name = schema["name"]
        for table in schema.get("tables", []):
            table_name = table["name"]
            columns = table.get("columns", [])
            table_id = f"{schema_name}.{table_name}"

            table_type = classify_table_type(
                schema_name, table_name, columns, table.get("comment", "")
            )

            key_cols = _find_key_columns(columns)
            non_key_cols = [
                col["name"]
                for col in columns
                if col["name"] not in key_cols
            ]

            node = {
                "id": table_id,
                "type": table_type,
                "schema": schema_name,
                "entity_key": key_cols[0] if key_cols else None,
                "comment": table.get("comment", ""),
            }

            if table_type == "feature_table":
                node["candidate_features"] = non_key_cols
            elif table_type == "label_table":
                node["candidate_targets"] = [
                    c for c in non_key_cols
                    if "target" in c.lower() or "label" in c.lower()
                ] or non_key_cols
            else:
                node["attributes"] = non_key_cols

            nodes.append(node)

            # Index key columns for edge detection
            for key_col in key_cols:
                col_lower = key_col.lower()
                col_type = next(
                    (c["data_type"] for c in columns if c["name"] == key_col),
                    "",
                )
                if col_lower not in key_column_index:
                    key_column_index[col_lower] = []
                key_column_index[col_lower].append((table_id, col_type))

    # Build edges from shared key columns
    edges = []
    seen_edges = set()

    for col_name, table_entries in key_column_index.items():
        if len(table_entries) < 2:
            continue

        for i, (table_a, type_a) in enumerate(table_entries):
            for table_b, type_b in table_entries[i + 1 :]:
                edge_key = tuple(sorted([table_a, table_b]) + [col_name])
                if edge_key in seen_edges:
                    continue
                seen_edges.add(edge_key)

                confidence = "high" if type_a == type_b else "medium"

                # Determine relationship type
                node_a_type = next(
                    (n["type"] for n in nodes if n["id"] == table_a), ""
                )
                node_b_type = next(
                    (n["type"] for n in nodes if n["id"] == table_b), ""
                )

                if node_a_type == "entity_master" or node_b_type == "entity_master":
                    relationship = "entity_of"
                else:
                    relationship = "joinable_on"

                edges.append(
                    {
                        "source": table_a,
                        "target": table_b,
                        "relationship": relationship,
                        "key": col_name,
                        "confidence": confidence,
                    }
                )

    return {"nodes": nodes, "edges": edges}

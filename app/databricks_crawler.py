"""
Databricks catalog metadata crawler using the Databricks SDK.

Connects to a Databricks workspace and crawls catalog metadata
(schemas, tables, columns) via information_schema SQL queries.
"""

import re
import time
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.sql import StatementState


def create_workspace_client(host, token):
    """Create a Databricks WorkspaceClient with token auth.

    Args:
        host: Databricks workspace URL (e.g., https://xxx.cloud.databricks.com)
        token: Personal access token

    Returns:
        WorkspaceClient instance
    """
    host = host.rstrip("/")
    if not host.startswith("https://"):
        host = f"https://{host}"
    return WorkspaceClient(host=host, token=token)


def test_connection(client, warehouse_id):
    """Test connectivity by executing SELECT 1.

    Args:
        client: WorkspaceClient instance
        warehouse_id: SQL warehouse ID

    Returns:
        True if connection succeeds

    Raises:
        Exception on connection failure
    """
    response = client.statement_execution.execute_statement(
        warehouse_id=warehouse_id,
        statement="SELECT 1",
        wait_timeout="30s",
    )
    if response.status and response.status.state == StatementState.SUCCEEDED:
        return True
    error_msg = ""
    if response.status and response.status.error:
        error_msg = response.status.error.message
    raise ConnectionError(f"Connection test failed: {error_msg}")


def _execute_sql(client, warehouse_id, statement):
    """Execute a SQL statement and return rows as list of dicts.

    Args:
        client: WorkspaceClient instance
        warehouse_id: SQL warehouse ID
        statement: SQL string to execute

    Returns:
        List of dicts, one per row
    """
    response = client.statement_execution.execute_statement(
        warehouse_id=warehouse_id,
        statement=statement,
        wait_timeout="50s",
    )

    # Poll if still pending
    if response.status and response.status.state in (
        StatementState.PENDING,
        StatementState.RUNNING,
    ):
        statement_id = response.statement_id
        for _ in range(30):
            time.sleep(2)
            response = client.statement_execution.get_statement(statement_id)
            if response.status.state not in (
                StatementState.PENDING,
                StatementState.RUNNING,
            ):
                break

    if response.status and response.status.state != StatementState.SUCCEEDED:
        error_msg = ""
        if response.status.error:
            error_msg = response.status.error.message
        raise RuntimeError(f"SQL execution failed: {error_msg}")

    # Parse results
    columns = []
    if response.manifest and response.manifest.schema and response.manifest.schema.columns:
        columns = [col.name for col in response.manifest.schema.columns]

    rows = []
    if response.result and response.result.data_array:
        for row_data in response.result.data_array:
            rows.append(dict(zip(columns, row_data)))

    return rows


def crawl_catalog_metadata(client, warehouse_id, catalog_name):
    """Crawl all metadata from a Databricks catalog.

    Executes three information_schema queries to retrieve schemas,
    tables, and columns with their comments.

    Args:
        client: WorkspaceClient instance
        warehouse_id: SQL warehouse ID
        catalog_name: Name of the catalog to crawl

    Returns:
        Structured metadata dict with catalog, schemas, tables, columns

    Raises:
        ValueError: If catalog_name contains invalid characters
    """
    if not re.match(r"^[a-zA-Z0-9_]+$", catalog_name):
        raise ValueError(
            f"Invalid catalog name '{catalog_name}'. "
            "Only alphanumeric characters and underscores are allowed."
        )

    # Query schemas
    schema_rows = _execute_sql(
        client,
        warehouse_id,
        f"SELECT schema_name, comment "
        f"FROM system.information_schema.schemata "
        f"WHERE catalog_name = '{catalog_name}' "
        f"ORDER BY schema_name",
    )

    # Query tables
    table_rows = _execute_sql(
        client,
        warehouse_id,
        f"SELECT table_schema, table_name, table_type, comment "
        f"FROM system.information_schema.tables "
        f"WHERE table_catalog = '{catalog_name}' "
        f"ORDER BY table_schema, table_name",
    )

    # Query columns
    column_rows = _execute_sql(
        client,
        warehouse_id,
        f"SELECT table_schema, table_name, column_name, data_type, comment "
        f"FROM system.information_schema.columns "
        f"WHERE table_catalog = '{catalog_name}' "
        f"ORDER BY table_schema, table_name, ordinal_position",
    )

    # Build structured metadata
    schemas_dict = {}
    for row in schema_rows:
        name = row.get("schema_name", "")
        if name and name != "information_schema":
            schemas_dict[name] = {
                "name": name,
                "comment": row.get("comment") or "",
                "tables": {},
            }

    for row in table_rows:
        schema_name = row.get("table_schema", "")
        table_name = row.get("table_name", "")
        if schema_name not in schemas_dict:
            schemas_dict[schema_name] = {
                "name": schema_name,
                "comment": "",
                "tables": {},
            }
        schemas_dict[schema_name]["tables"][table_name] = {
            "name": table_name,
            "full_name": f"{catalog_name}.{schema_name}.{table_name}",
            "table_type": row.get("table_type") or "",
            "comment": row.get("comment") or "",
            "columns": [],
        }

    for row in column_rows:
        schema_name = row.get("table_schema", "")
        table_name = row.get("table_name", "")
        if (
            schema_name in schemas_dict
            and table_name in schemas_dict[schema_name]["tables"]
        ):
            schemas_dict[schema_name]["tables"][table_name]["columns"].append(
                {
                    "name": row.get("column_name", ""),
                    "data_type": row.get("data_type") or "",
                    "comment": row.get("comment") or "",
                }
            )

    # Convert to list format
    result = {
        "catalog": catalog_name,
        "schemas": [],
    }
    for schema in sorted(schemas_dict.values(), key=lambda s: s["name"]):
        schema_entry = {
            "name": schema["name"],
            "comment": schema["comment"],
            "tables": sorted(
                schema["tables"].values(), key=lambda t: t["name"]
            ),
        }
        result["schemas"].append(schema_entry)

    return result

"""
ChromaDB-based in-memory RAG store for Databricks catalog metadata.

Embeds table and column descriptions into a vector store for
semantic retrieval during agent queries.
"""

import chromadb


def create_metadata_store():
    """Create an in-memory ChromaDB collection for catalog metadata.

    Returns:
        ChromaDB Collection instance
    """
    client = chromadb.Client()
    # Delete if exists (for re-crawl scenarios)
    try:
        client.delete_collection("catalog_metadata")
    except Exception:
        pass
    collection = client.create_collection(
        name="catalog_metadata",
        metadata={"hnsw:space": "cosine"},
    )
    return collection


def _table_to_document(schema, table):
    """Convert a table's metadata into a text document for embedding.

    Args:
        schema: Schema dict with 'name' and 'comment'
        table: Table dict with 'name', 'full_name', 'comment', 'columns'

    Returns:
        Formatted text string describing the table
    """
    lines = [
        f"Table: {table['full_name']}",
        f"Schema: {schema['name']} ({schema.get('comment', '')})",
    ]
    if table.get("comment"):
        lines.append(f"Description: {table['comment']}")

    if table.get("columns"):
        lines.append("Columns:")
        for col in table["columns"]:
            col_desc = f"  - {col['name']} ({col.get('data_type', 'UNKNOWN')})"
            if col.get("comment"):
                col_desc += f": {col['comment']}"
            lines.append(col_desc)

    return "\n".join(lines)


def populate_store(collection, metadata):
    """Index crawled catalog metadata into the ChromaDB collection.

    Creates one document per table containing the table's full name,
    schema, comment, and all column names/types/comments.

    Args:
        collection: ChromaDB Collection instance
        metadata: Structured metadata dict from crawl_catalog_metadata()

    Returns:
        Number of documents indexed
    """
    documents = []
    ids = []
    metadatas = []

    for schema in metadata.get("schemas", []):
        for table in schema.get("tables", []):
            doc_text = _table_to_document(schema, table)
            doc_id = table["full_name"]

            documents.append(doc_text)
            ids.append(doc_id)
            metadatas.append(
                {
                    "schema_name": schema["name"],
                    "table_name": table["name"],
                    "full_name": table["full_name"],
                    "table_type": table.get("table_type", ""),
                }
            )

    if documents:
        # ChromaDB has batch size limits, add in chunks
        batch_size = 100
        for i in range(0, len(documents), batch_size):
            collection.add(
                documents=documents[i : i + batch_size],
                ids=ids[i : i + batch_size],
                metadatas=metadatas[i : i + batch_size],
            )

    return len(documents)


def query_store(collection, question, n_results=10):
    """Retrieve the most relevant table documents for a question.

    Args:
        collection: ChromaDB Collection instance
        question: User's natural language question
        n_results: Number of results to return (default 10)

    Returns:
        List of document strings ranked by relevance
    """
    count = collection.count()
    if count == 0:
        return []

    actual_n = min(n_results, count)
    results = collection.query(
        query_texts=[question],
        n_results=actual_n,
    )
    return results["documents"][0] if results["documents"] else []


def get_rag_context(collection, question, n_results=10):
    """Retrieve relevant metadata and format as LLM context.

    Args:
        collection: ChromaDB Collection instance
        question: User's natural language question
        n_results: Number of table documents to retrieve

    Returns:
        Formatted context string for the LLM prompt
    """
    docs = query_store(collection, question, n_results)
    if not docs:
        return ""

    header = (
        f"The following {len(docs)} table descriptions were retrieved "
        f"from the catalog metadata based on relevance to the question:\n\n"
    )
    separator = "\n" + "=" * 60 + "\n"
    return header + separator.join(docs)

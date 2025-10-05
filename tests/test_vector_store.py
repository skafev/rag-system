import tempfile
import shutil
import pytest
from app.vector_store import DocumentStore

@pytest.fixture(scope="module")
def store():
    """
    Fixture to create an isolated test collection with known chunks,
    including chunk_index for semantic search compatibility.
    """
    temp_dir = tempfile.mkdtemp()
    store = DocumentStore(collection_name="test_collection", persist_directory=temp_dir)

    # Known test chunks
    chunks = [
        {"content": "Alice works at OpenAI.", "source": "test_doc.txt", "chunk_index": 0},
        {"content": "Bob lives in the UK.", "source": "test_doc.txt", "chunk_index": 1}
    ]

    store.collection.add(
        documents=[c["content"] for c in chunks],
        metadatas=[{"source": c["source"], "chunk_index": c["chunk_index"]} for c in chunks],
        ids=[str(i) for i in range(len(chunks))]
    )

    yield store
    shutil.rmtree(temp_dir)


def get_doc_content(result):
    """
    Extract the document text safely from different return types:
    - tuple (doc_dict, score) for hybrid search
    - dict with 'content' key
    """
    if isinstance(result, tuple) or isinstance(result, list):
        doc = result[0]
    else:
        doc = result

    if isinstance(doc, dict):
        return doc.get("content", "")
    return str(doc)


def test_semantic_search(store):
    results = store.semantic_search("Alice", top_k=1)
    assert isinstance(results, list)
    assert len(results) > 0
    doc = results[0]
    # Ensure chunk_index exists and content contains Alice
    assert "chunk_index" in doc
    assert "Alice" in get_doc_content(doc)


def test_keyword_search(store):
    results = store.keyword_search("Bob", top_k=1)
    assert isinstance(results, list)
    assert len(results) > 0
    content = get_doc_content(results[0])
    assert "Bob" in content


def test_hybrid_search(store):
    results = store.hybrid_search("Alice", top_k=2)
    assert isinstance(results, list)
    # Check that at least one result contains "Alice"
    assert any("Alice" in get_doc_content(r) for r in results)


def test_metadata_filter(store):
    results = store.hybrid_search(
        "Bob",
        top_k=2,
        metadata_filter={"source": "test_doc.txt"}
    )
    for r in results:
        # Extract doc dict
        if isinstance(r, tuple) or isinstance(r, list):
            doc = r[0]
        else:
            doc = r
        assert doc["source"] == "test_doc.txt"

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "RAG API is running"}


def get_doc_content(result):
    """
    Helper to extract content text from API result item.
    """
    if "content" in result:
        return result["content"]
    return str(result)


def test_advanced_search_endpoint():
    payload = {"query": "Alice 30 USA", "top_k": 2}
    response = client.post("/advanced_search", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert isinstance(data["results"], list)

    if data["results"]:
        first = data["results"][0]
        # Check the actual keys your API returns
        assert "content" in first
        assert "source" in first
        # Optional: check text presence
        content = get_doc_content(first)
        assert len(content) > 0

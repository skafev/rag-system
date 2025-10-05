import random
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, Dict
from app.vector_store import DocumentStore


class SearchRequest(BaseModel):
    query: str
    top_k: Optional[int] = 3
    metadata_filter: Optional[Dict[str, str]] = None
    w_semantic: Optional[float] = 0.7
    w_keyword: Optional[float] = 0.3


app = FastAPI(title="RAG Search API")
store = DocumentStore()
store.collection.delete(where={"source": "test_doc.txt"})
print("Test chunks deleted successfully!")
store.ingest_chunks()


def serialize_chunks(chunks):
    serialized = []
    for chunk in chunks:
        serialized.append({
            "source": chunk["metadata"]["source"],
            "chunk_index": chunk["metadata"]["chunk_index"],
            "content": chunk["content"],
            "score": float(chunk.get("score", 0))  # convert numpy.float32 to float
        })
    return serialized


@app.get("/")
def root():
    return {"message": "RAG API is running"}


@app.post("/semantic_search")
def semantic_search(req: SearchRequest):
    try:
        results = store.semantic_search(req.query, top_k=req.top_k, metadata_filter=req.metadata_filter)
        return {"query": req.query, "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/keyword_search")
def keyword_search(req: SearchRequest):
    try:
        results = store.keyword_search(req.query, top_k=req.top_k, metadata_filter=req.metadata_filter)
        return {"query": req.query, "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/hybrid_search")
def hybrid_search(req: SearchRequest):
    try:
        raw_results = store.hybrid_search(
            query=req.query,
            top_k=req.top_k,
            w_semantic=req.w_semantic,
            w_keyword=req.w_keyword,
            metadata_filter=req.metadata_filter
        )
        results = serialize_chunks([chunk for score, chunk in raw_results])
        return {"query": req.query, "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/advanced_search")
def advanced_search(req: SearchRequest):
    try:
        raw_results = store.advanced_search(
            query=req.query,
            top_k=req.top_k,
            w_semantic=req.w_semantic,
            w_keyword=req.w_keyword,
            metadata_filter=req.metadata_filter
        )
        results = serialize_chunks([chunk for score, chunk in raw_results])
        return {"query": req.query, "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ab_test")
async def ab_test(request: SearchRequest, strategy: str = Query(None, description="semantic | keyword | hybrid | auto")):
    """
    Run A/B testing between different retrieval strategies.
    If strategy='auto', randomly choose one (semantic vs hybrid).
    """
    query = request.query

    if strategy == "semantic":
        results = store.semantic_search(query, top_k=request.top_k)
    elif strategy == "keyword":
        results = store.keyword_search(query, top_k=request.top_k)
    elif strategy == "hybrid":
        results = store.hybrid_search(query, top_k=request.top_k, w_semantic=request.w_semantic, w_keyword=request.w_keyword)
    elif strategy == "auto":
        chosen = random.choice(["semantic", "hybrid"])
        results = (
            store.semantic_search(query, top_k=request.top_k)
            if chosen == "semantic"
            else store.hybrid_search(query, top_k=request.top_k, w_semantic=request.w_semantic, w_keyword=request.w_keyword)
        )
        return {"chosen_strategy": chosen, "results": results}
    else:
        return {"error": "Invalid strategy. Use semantic | keyword | hybrid | auto."}

    return {"strategy": strategy, "results": results}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)

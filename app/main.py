from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict
from .vector_store import DocumentStore


class SearchRequest(BaseModel):
    query: str
    top_k: Optional[int] = 3
    metadata_filter: Optional[Dict[str, str]] = None
    w_semantic: Optional[float] = 0.7
    w_keyword: Optional[float] = 0.3


app = FastAPI(title="RAG Search API")
store = DocumentStore()
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

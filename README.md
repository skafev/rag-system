# Production-ready RAG Application — README

**Project goal:** a reproducible Retrieval-Augmented Generation (RAG) system that demonstrates enterprise-grade engineering practices — document ingestion, smart chunking, hybrid retrieval (semantic + lexical), advanced RAG features (query expansion, cross-encoder reranking), metadata filtering, a REST API, caching, and containerization.
* Primary Language: Python 3.11.
* Vector Database: ChromaDB
Rationale: Lightweight, local, open-source, fast for small-to-medium datasets.
* Orchestration Framework: Native Python scripts and FastAPI.
* LLM / Embeddings: Hugging Face models
Reasoning: Free or low-cost inference.
---
## Table of contents

1. Setup & Quick Start
2. Project structure
3. Step-by-step usage (local + Docker)
4. Architecture overview (diagram + components)
5. Technical decisions & trade-offs
6. API documentation (endpoints, inputs, examples)
7. Caching strategy
8. Scaling strategy (10x–100x)
9. Monitoring, testing & evaluation
10. Troubleshooting & common issues
11. Cost Analysis
12. Next steps and optional features

---

## 1. Setup & Quick Start

### Requirements

* Python 3.10+ (3.11 recommended)
* Git
* Docker (optional, required for container)
* ~10 GB disk recommended for model caches and Docker images (smaller models are used by default)

### Install (local / development)

1. Clone the repo:

```bash
git clone https://github.com/skafev/rag-system rag-app
cd rag-app
```

2. Create & activate a virtual environment (Windows PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
```

> `requirements.txt` contains only the packages used in the project (FastAPI, uvicorn, sentence-transformers, transformers, rank_bm25, chromadb, cachetools, PyMuPDF, python-docx, beautifulsoup4, nltk, etc.)

3. Ensure `documents/` contains your files (pdf/docx/html/json). Example structure:

```
Documents/
  pdfs/
  docx/
  html/
  json/
```

4. Build chunks (ingest pipeline):

```powershell
python build_chunks.py
# writes: output/chunks.json
```

5. Ingest into local Chroma DB and run server:

```powershell
python main.py         # or: python -m uvicorn app.main:app --reload
# The API will start at http://127.0.0.1:8000
```

6. Try interactive API docs:
   Open: `http://127.0.0.1:8000/docs`

---

## 2. Project structure

```
.
rag-system/
│
├── app/                        # Main application code
│   ├── __init__.py
│   ├── main.py                 # FastAPI API entrypoint
│   ├── vector_store.py         # Hybrid search, embeddings, cache
│   ├── chunking.py             # Chunking logic
│   ├── parsers/                # Document parsers
│   │   ├── __init__.py
│   │   ├── parsers.py
│   ├── utils/                  # Helpers
│   │   ├── __init__.py
│   │   └── preprocessing.py
│   └── config.py               # Central place for constants
│
├── documents/                  # Example documents
│   ├── pdfs/
│   ├── docx/
│   ├── html/
│   └── json/
│
├── output/                     # Generated chunks, ChromaDB, logs
│   ├── chunks.json
│   └── chroma_db/
│
├── data_gen_scripts/                    # Scripts for data generation, ingestion
│   ├── build_chunks.py
│   ├── generate_pdfs.py
│   ├── generate_docx.py
│   ├── generate_html.py
│   └── generate_json.py
│   ├── generate_messy_pdf.py
│   ├── generate_messy_docx.py
│   ├── generate_messy_html.py
│   └── generate_messy_json.py
│
├── tests/                      # Tests and load/stress testing
│   ├── __init__.py
│   ├── test_chunking.py
│   ├── test_vector_store.py 
│   ├── test_api.py            
│   └── stress_test.py
│
├── requirements.txt
├── Dockerfile
├── README.md
├── .gitignore
```

---

## 3. Step-by-step usage

### 3.1 Build `chunks.json` (single command)

`build_chunks.py`:

* Walks `documents/`, parses each file (pdf/docx/html/json).
* Preprocesses text (normalize whitespace, lists → `-`, tables → `|`).
* Calls `chunk_document(parsed_doc, max_lines=..., overlap=...)`.
* Outputs `output/chunks.json`, each entry:

```json
{
  "id": "messy_pdf.pdf_chunk2",
  "content": "Name | Age | Country\nAlice | 30 | USA",
  "metadata": {"source": "Documents/pdfs/messy_pdf.pdf", "doc_type": "pdf", "chunk_index": 2}
}
```

Run:

```powershell
python build_chunks.py
```

### 3.2 Ingest into vector store (Chroma) — local by default

`DocumentStore.ingest_chunks()` reads `output/chunks.json`, computes embeddings (local sentence-transformers) and upserts into ChromaDB with metadata and documents.

Run (via API or direct):

```python
from vector_store import DocumentStore
store = DocumentStore()
store.ingest_chunks()
```

### 3.3 Start the API

```powershell
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
# or docker run -p 8000:8000 -v "<documents_path>" rag-api
```

### 3.4 Example local test (CLI)

Use the provided `stress_test.py` or `curl`:

```bash
curl -X POST "http://127.0.0.1:8000/advanced_search" \
  -H "Content-Type: application/json" \
  -d '{"query":"Alice 30 USA", "top_k":3, "metadata_filter":{"doc_type":"pdf"}}'
```

---

## 4. Architecture overview

### High-level diagram

```
flowchart LR
  A[Documents (PDF/DOCX/HTML/JSON)] --> B[Parsers]
  B --> C[Preprocessor & Normalizer]
  C --> D[Chunker (semantic + overlap + type-specific)]
  D --> E[Chunks JSON (output/chunks.json)]
  E --> F[Ingest -> Vector DB (Chroma) & BM25 index]
  F --> G[DocumentStore (semantic, BM25, hybrid)]
  G --> H[Advanced RAG: query expansion + cross-encoder rerank]
  G --> I[REST API (FastAPI)]
  I --> J[Clients (Web UI, CLI, Agents)]
  I --> K[Cache Layer (embedding / query / LLM outputs) - cachetools / Redis]
```

### Component descriptions

* **Parsers**: file-format readers (PyMuPDF for PDF, python-docx for DOCX, BeautifulSoup for HTML, json module for JSON).
* **Preprocessor**: normalizes text, converts bullets & tables to structured text, removes navigation/boilerplate heuristics for HTML, cleans whitespace.
* **Chunker**: `semantic_chunk_with_line_overlap` + `chunk_document` wrapper; preserves lists/tables and supports type-specific strategies.
* **Chunks JSON**: canonical intermediate (reproducible).
* **Vector store (Chroma)**: stores embeddings, documents, and metadata; supports queries by embedding and metadata payloads.
* **BM25**: rank_bm25 index built from `chunks.json` for lexical retrieval.
* **DocumentStore**: class that encapsulates ingestion, semantic and lexical retrieval, hybrid scoring, query expansion, cross-encoder reranking.
* **Advanced RAG**:

  * *Query expansion*: FLAN-T5 small (Hugging Face) local model.
  * *Cross-encoder reranking*: `cross-encoder/ms-marco-MiniLM-L-6-v2` for query-document pair scoring.
* **API**: FastAPI endpoints exposing search functionality (semantic, keyword, hybrid, advanced).
* **Cache**: in-memory TTL LRU caches (cachetools) for embeddings & query results. Optionally Redis for distributed caching.
* **Containerization**: Dockerfile that builds image, pre-downloads NLTK data and ensures `/app/Documents` exists; support for mounting host documents.

---

## 5. Technical decisions & trade-offs

### Vector store selection: **ChromaDB (local)** — why

* **Pros**

  * Zero-cost local prototyping (fits $10 budget).
  * Simple to run (no extra server); persistent storage via DuckDB+Parquet.
  * Easy to swap out later (Qdrant, Pinecone, pgvector) with a thin adapter.
* **Cons**

  * Not optimized for large scale/low-latency nearest-neighbor at tens/hundreds of thousands of vectors.
  * Less feature-rich than Qdrant/Pinecone for payload filters, replication, and managed hosting.
* **Trade-off**: Chroma is *practical for development and small production systems*. For 10x–100x growth, migrate to Qdrant / Pinecone / pgvector + Postgres.

### Embeddings choice

* **Local**: `sentence-transformers` (`all-MiniLM-L6-v2`) — fast, small, no cost.
* **Alternative**: OpenAI `text-embedding-3-small` — higher quality but cost and quota constraints.
* **Decision**: local embeddings by default for reproducibility and cost control; README documents how to switch to OpenAI.

### Keyword retrieval

* **BM25** (rank_bm25) chosen for fast lexical matching, complements semantic embeddings.

### Reranker and query rewriting

* **Cross-encoder** for reranking (small cross-encoder) to significantly improve precision on final candidate set.
* **FLAN-T5-small** for local query rewriting (no API cost).

### API & concurrency

* **FastAPI + Uvicorn** (or Gunicorn + Uvicorn workers) — chosen for async, type-safe endpoints, and automatic OpenAPI docs.

---

## 6. API Documentation

### Base URL

* Local: `http://127.0.0.1:8000`

### Common request model

All endpoints accept the same JSON body:

```json
{
  "query": "string",
  "top_k": 3,
  "metadata_filter": {"doc_type": "pdf"},
  "w_semantic": 0.7,
  "w_keyword": 0.3
}
```

* `query` (string) — required.
* `top_k` (int) — optional, default 3.
* `metadata_filter` (dict) — optional, e.g., `{"doc_type":"pdf"}` or `{"source":"policy"}`.
* `w_semantic`, `w_keyword` for hybrid weighting (only used by hybrid/advanced endpoints).

### Endpoints

#### GET /

* Root endpoint / health check. Confirms that the API is running..
* Example `curl`:

```bash
curl -X GET "http://127.0.0.1:8000/"'
```
### Response format (JSON)

```json
{
  "message": "RAG API is running"
}
```

#### POST `/semantic_search`

* Returns top-k documents by semantic similarity (embedding search).
* Example `curl`:

```bash
curl -X POST "http://127.0.0.1:8000/semantic_search" -H "Content-Type: application/json" \
  -d '{"query":"What tables are in the messy documents?", "top_k":3}'
```

#### POST `/keyword_search`

* Returns top-k documents by BM25 lexical score.
* Example:

```bash
curl -X POST "http://127.0.0.1:8000/keyword_search" -H "Content-Type: application/json" \
 -d '{"query":"Alice 30 USA","top_k":3}'
```

#### POST `/hybrid_search`

* Pulls candidates from both semantic and keyword and combines scores:
  `final = w_semantic * semantic_norm + w_keyword * bm25_norm`.
* Example:

```bash
curl -X POST "http://127.0.0.1:8000/hybrid_search" -H "Content-Type: application/json" \
  -d '{"query":"Alice", "top_k":5, "w_semantic":0.6, "w_keyword":0.4}'
```

#### POST `/advanced_search`

* Pipeline: query expansion → hybrid retrieval (top N candidates) → cross-encoder rerank → return top_k.
* Example:

```bash
curl -X POST "http://127.0.0.1:8000/advanced_search" -H "Content-Type: application/json" \
  -d '{"query":"Alice 30 USA", "top_k":3, "metadata_filter":{"doc_type":"pdf"}}'
```

### Response format (JSON)

```json
{
  "query": "Alice 30 USA",
  "results": [
    {
      "source": "Documents/pdfs/messy_pdf.pdf",
      "chunk_index": 2,
      "content": "Name | Age | Country\nAlice | 30 | USA",
      "score": 0.9234
    }
  ]
}
```

### Error handling

* The API returns HTTP status codes:

  * `200` success
  * `400` bad request (missing query, invalid params)
  * `500` server error (exceptions)
* Validation is done via Pydantic — malformed JSON or wrong field types will produce `400`.

---

## 7. Caching strategy (implemented)

### Cache levels implemented

1. **Embedding cache** (`embedding_cache`) — avoid recomputing embeddings for repeated identical queries.
2. **Query results cache** (`query_cache`) — caches hybrid/advanced search outputs for repeated queries (key includes query, top_k, weights, metadata filter).
3. **TTL & eviction** — TTLCache (cachetools) with defaults:

   * `maxsize=100` (configurable)
   * `ttl=600` seconds (10 minutes)
   * eviction policy: **LRU** (least recently used)

### Why TTL + LRU

* TTL ensures caches don't serve stale results when the corpus changes.
* LRU ensures frequently used queries remain cached while limiting memory consumption.

### Cache invalidation

* After ingesting new documents or re-running `build_chunks.py`, call:

```python
store.embedding_cache.clear()
store.query_cache.clear()
```

* In production with Redis: include a version key or cache-busting token that increments on ingestion, so caches automatically become stale.

### Performance impact (approx)

* For local experiments: cache hits reduce response times from ~200–500 ms (embedding + hybrid) to ~5–20 ms.
* Cross-encoder reranking remains expensive; cache final reranked outputs if queries repeat.

---

## 8. Scaling strategy (10x–100x)

### Short-term (small scale)

* **ChromaDB local** + Sentence-Transformers, single machine:

  * Good up to a few tens of thousands of chunks.
  * Use `gunicorn` with multiple workers to handle concurrency.

### Medium-scale (production)

* **Vector DB**: migrate to **Qdrant** or **Pinecone** for:

  * efficient ANN search (HNSW), payload/metadata filtering, and persistence.
  * Qdrant/pinecone handle large indexes and produce lower latency at scale.
* **Keyword search**: move BM25 to **Elasticsearch/OpenSearch** for distributed lexical retrieval and advanced filtering.
* **Reranker**: move cross-encoder to GPU-backed service or batch requests; consider a dedicated reranker microservice.
* **Caching**: move from in-memory to **Redis** (shared across instances).
* **Batching & async**: batch queries to embeddings model; use async endpoints.
* **Autoscaling**: containerize and deploy to Kubernetes, add horizontal pod autoscaler.

### Large-scale (100x+)

* **ANN indexers**: FAISS + GPU, HNSWlib, or managed Pinecone with sharding.
* **Sharding**: shard indices by business unit or taxonomy.
* **Monitoring & A/B testing**: continuously measure recall@k and latency.
* **CI/CD**: container images + Helm charts for Kubernetes deployment.

---

## 9. Monitoring, testing & evaluation

### Monitoring

* Track:

  * Request latency & throughput (Prometheus + Grafana).
  * Cache hit/miss rate.
  * Embedding & reranker latencies.
  * Error rates and 5xx counts.

### Testing / Evaluation

* Build labeled queries with expected chunk IDs. Compute:

  * **Recall@k**, **MRR**, **Precision@k**.
* Unit tests:

  * Parsers produce expected outputs for sample docs.
  * Chunker respects type-specific rules (tables, bullets).
  * Hybrid ranking returns top expected results.
* Load test: `stress_test.py` or k6, simulate concurrency and measure p95 latency.

---

## 10. Troubleshooting & common issues

* **`ModuleNotFoundError: nltk`** in Docker: ensure `nltk` is in `requirements.txt` and Dockerfile runs `python -m nltk.downloader punkt punkt_tab`.
* **No results for a query**: ensure `output/chunks.json` exists and ingestion ran. Use `store.collection.count()` to check.
* **Unexpected unrelated results** (short queries): use metadata filters or hybrid weighting (increase `w_keyword` or use hybrid/advanced).
* **Unhashable type: dict** in cache: use cachetools `cachedmethod` with a custom key that converts dict to `tuple(sorted(dict.items()))`.

---

## 11. Cost Analysis

* Hugging Face embeddings (free, runs locally on CPU/GPU).
* OpenAI embeddings (~$0.0001 per 1K tokens) – switching to OpenAI would cost ~$1–3 for 10K queries..
* This design keeps compute under $10/month by:
   * Using local embeddings
   * Adding caching for repeated queries
   * Supporting hybrid retrieval to reduce over-reliance on LLMs

## 12. Next steps & optional features

* **Agentic RAG**  build an agent orchestration layer that decomposes complex tasks.
* **UI**: minimal web UI to query and show provenance + highlight snippets.
* **Authentication & rate limiting**: integrate API key auth, rate limit per client (FastAPI middleware).
* **Dataset & evaluation**: prepare labeled testset with expected snippet IDs for evaluation.

---

## Appendix — Useful commands

### Build & run (local)

```powershell
# rebuild chunks if you change parser/chunking rules:
python build_chunks.py

# run server
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Docker

```powershell
docker build -t rag-api .
docker run -p 8000:8000 -v "<documents_path>" rag-api
# interactive shell for debugging:
docker run -it -v "<documents_path>" rag-api /bin/bash
```

### Stress test locally (Python)

```powershell
python stress_test.py
```

---

## Contact / Notes

* https://github.com/skafev

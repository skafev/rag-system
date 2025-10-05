import chromadb
import json
import nltk
import numpy as np
import os
from sentence_transformers import SentenceTransformer, CrossEncoder
from rank_bm25 import BM25Okapi
from transformers import pipeline
from nltk.tokenize import word_tokenize
from cachetools import TTLCache, cachedmethod
from operator import attrgetter
from app.config import CHUNKS_FILE, CHROMA_DB_DIR, QUERY_CACHE_TTL, QUERY_CACHE_SIZE


# Download tokenizer
nltk.download("punkt")


class DocumentStore:
    def __init__(self, chunks_path=CHUNKS_FILE, collection_name="documents"):
        """DocumentStore initializer."""
        self.chunks_path = chunks_path
        self.collection_name = collection_name
        self.embedding_cache = TTLCache(maxsize=QUERY_CACHE_SIZE, ttl=QUERY_CACHE_TTL)
        self.query_cache = TTLCache(maxsize=QUERY_CACHE_SIZE, ttl=QUERY_CACHE_TTL)
        self.chroma_client = chromadb.PersistentClient(path=CHROMA_DB_DIR)
        self.collection = self.chroma_client.get_or_create_collection(self.collection_name)

        # Load chunks
        if not os.path.exists(chunks_path):
            raise FileNotFoundError(f"{chunks_path} not found. Please run chunking first.")
        with open(chunks_path, "r", encoding="utf-8") as f:
            self.chunks = json.load(f)

        # Build BM25 index
        self.tokenized_chunks = [word_tokenize(c["content"].lower()) for c in self.chunks]
        self.bm25 = BM25Okapi(self.tokenized_chunks)

        # Load embedding model
        self.embed_model = SentenceTransformer("all-MiniLM-L6-v2")
        self.cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
        self.query_rewriter = pipeline("text2text-generation", model="google/flan-t5-small")

    def _query_cache_key(self, *args, **kwargs):
        default_top_k = 5
        default_w_semantic = 0.7
        default_w_keyword = 0.3
        query = kwargs.get("query", args[0] if len(args) > 0 else None)
        top_k = kwargs.get("top_k", args[1] if len(args) > 1 else default_top_k)
        w_semantic = kwargs.get("w_semantic", args[2] if len(args) > 2 else default_w_semantic)
        w_keyword = kwargs.get("w_keyword", args[3] if len(args) > 3 else default_w_keyword)
        metadata_filter = kwargs.get("metadata_filter", args[4] if len(args) > 4 else None)
        try:
            top_k = int(top_k)
        except Exception:
            top_k = default_top_k
        try:
            w_semantic = float(w_semantic)
        except Exception:
            w_semantic = default_w_semantic
        try:
            w_keyword = float(w_keyword)
        except Exception:
            w_keyword = default_w_keyword
        if metadata_filter is None:
            mf_tuple = tuple()
        elif isinstance(metadata_filter, dict):
            mf_tuple = tuple(sorted(metadata_filter.items()))
        else:
            mf_tuple = (str(metadata_filter),)
        return str(query), top_k, round(w_semantic, 6), round(w_keyword, 6), mf_tuple

    def expand_query(self, query: str):
        """Expand query using Hugging Face."""
        expanded = self.query_rewriter(
            f"Rewrite this query to improve search results. Keep the meaning, add synonyms and context {query}"
        )
        return expanded[0]['generated_text']

    @cachedmethod(attrgetter("embedding_cache"))
    def embed_text(self, text: str):
        emb = self.embed_model.encode(text)
        if isinstance(emb, np.ndarray):
            emb = emb.tolist()
        return emb

    def ingest_chunks(self):
        """Ingest chunks into ChromaDB if empty."""
        if self.collection.count() > 0:
            print(f"Collection already has {self.collection.count()} chunks.")
            return
        print("Collection empty — ingesting chunks...")
        ids, embeddings, metadatas, documents = [], [], [], []

        for idx, chunk in enumerate(self.chunks):
            ids.append(str(idx))
            emb = self.embed_text(chunk["content"])
            embeddings.append(emb)
            metadatas.append(chunk["metadata"])
            documents.append(chunk["content"])
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas,
            documents=documents
        )
        print(f"Ingested {len(documents)} chunks into ChromaDB.")

    def semantic_search(self, query: str, top_k: int = 3, metadata_filter: dict = None):
        """Semantic search."""
        query_emb = self.embed_text(query)
        results = self.collection.query(
            query_embeddings=[query_emb],
            n_results=top_k,
            where=metadata_filter
        )

        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]

        print(f"\nSemantic Search Results for: '{query}'")
        if not docs:
            print("No results found. (Check if you ingested chunks or try a different query)")
        else:
            for doc, meta in zip(docs, metas):
                print(f"- {meta['source']} (chunk {meta['chunk_index']})")
                print(f"  {doc[:200]}...\n")
        return results

    def keyword_search(self, query: str, top_k: int = 3, metadata_filter: dict = None):
        """Keyword search."""
        query_tokens = word_tokenize(query.lower())
        scores = self.bm25.get_scores(query_tokens)
        top_indices = np.argsort(scores)[-top_k:][::-1]

        print(f"\nKeyword Search Results for: '{query}'")
        results = []
        for idx in top_indices:
            chunk = self.chunks[idx]
            if metadata_filter:
                match = all(chunk["metadata"].get(k) == v for k, v in metadata_filter.items())
                if not match:
                    continue
            results.append(chunk)
            meta = chunk["metadata"]
            doc = chunk["content"]
            print(f"- {meta['source']} (chunk {meta['chunk_index']})")
            print(f"  {doc[:200]}...\n")
        return results

    @cachedmethod(attrgetter("query_cache"), key=_query_cache_key)
    def hybrid_search(self, query: str, top_k: int = 3, w_semantic: float = 0.7, w_keyword: float = 0.3,
                      metadata_filter: dict = None, called_from_advanced: bool = False):
        """Combine semantic + keyword scores with weights."""
        # Semantic
        query_emb = self.embed_text(query)
        sem_results = self.collection.query(
            query_embeddings=[query_emb],
            n_results=len(self.chunks),
            where=metadata_filter
        )
        sem_scores = sem_results.get("distances", [[]])[0]
        sem_scores = [1 - s for s in sem_scores]
        # Keyword
        query_tokens = word_tokenize(query.lower())
        kw_scores = self.bm25.get_scores(query_tokens)
        # Combine
        final_scores = []
        for i, chunk in enumerate(self.chunks):
            if metadata_filter:
                match = all(chunk["metadata"].get(k) == v for k, v in metadata_filter.items())
                if not match:
                    continue
            sem_score = sem_scores[i] if i < len(sem_scores) else 0
            kw_score = kw_scores[i] if i < len(kw_scores) else 0
            final_score = w_semantic * sem_score + w_keyword * kw_score
            final_scores.append((final_score, chunk))
        # Sort by score
        final_scores.sort(key=lambda x: x[0], reverse=True)
        top_results = final_scores[:top_k]
        if not called_from_advanced:
            print(f"\n Hybrid Search Results for: '{query}' ")
            for score, chunk in top_results:
                meta = chunk["metadata"]
                doc = chunk["content"]
                print(f"- {meta['source']} (chunk {meta['chunk_index']}) | score: {score:.4f}")
                print(f"  {doc[:200]}...\n")
        return top_results

    @cachedmethod(attrgetter("query_cache"), key=_query_cache_key)
    def advanced_search(self, query: str, top_k=3, w_semantic=0.7, w_keyword=0.3, metadata_filter=None):
        # Step 1: Query expansion
        expanded_query = self.expand_query(query)
        print(f"\nExpanded query: {expanded_query}")
        # Step 2: Hybrid search
        top_chunks = self.hybrid_search(expanded_query, top_k=3, w_semantic=w_semantic, w_keyword=w_keyword,
                                        metadata_filter=metadata_filter, called_from_advanced=True)
        # Step 3: Cross-encoder re-ranking
        reranked = self.cross_encoder_rerank(expanded_query, [c[1] for c in top_chunks])

        print(f"\n Advanced Search Results for: '{query}'")
        for score, chunk in reranked[:top_k]:
            meta = chunk["metadata"]
            print(f"- {meta['source']} (chunk {meta['chunk_index']}) | CE score: {score:.4f}")
            print(f"  {chunk['content'][:200]}...\n")
        return reranked[:top_k]

    def cross_encoder_rerank(self, query: str, chunks: list):
        texts = [chunk["content"] for chunk in chunks]
        scores = self.cross_encoder.predict([[query, text] for text in texts])
        reranked = sorted(zip(scores, chunks), key=lambda x: x[0], reverse=True)
        return reranked


if __name__ == "__main__":
    store = DocumentStore()
    store.ingest_chunks()
    example_query = "Alice 30 USA"
    metadata_filter = {"doc_type": "pdf"}
    store.semantic_search(example_query, top_k=3, metadata_filter=metadata_filter)
    store.keyword_search(example_query, top_k=3, metadata_filter=metadata_filter)
    store.hybrid_search(example_query, top_k=3, w_semantic=0.7, w_keyword=0.3, metadata_filter=metadata_filter)
    store.advanced_search(example_query, top_k=3, w_semantic=0.7, w_keyword=0.3, metadata_filter=metadata_filter)

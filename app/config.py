import os

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DOCUMENTS_DIR = os.path.join(BASE_DIR, "documents")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
CHROMA_DB_DIR = os.path.join(OUTPUT_DIR, "chroma_db")
CHUNKS_FILE = os.path.join(OUTPUT_DIR, "chunks.json")

# Chunking defaults
MAX_LINES = 5
OVERLAP = 1

# Cache
QUERY_CACHE_TTL = 600
QUERY_CACHE_SIZE = 100

import os
from app.parsers.parsers import parse_pdf, parse_html
from app.utils.preprocess import preprocess
from app.chunking import semantic_chunk

documents_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "documents")
html_dir = os.path.join(documents_dir, "html")
doc = parse_html(os.path.join(html_dir, 'messy_html.html'))
cleaned = preprocess(doc["content"])
chunks = semantic_chunk(cleaned, max_chunk_size=150)

print("Semantic Chunking Example (HTML)")
for i, chunk in enumerate(chunks, 1):
    print(f"--- Chunk {i} ---")
    print(chunk)

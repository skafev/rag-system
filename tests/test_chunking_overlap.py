import os
from app.parsers.parsers import parse_pdf
from app.utils.preprocess import preprocess
from app.chunking import semantic_chunk_with_line_overlap

documents_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "documents")
pdf_dir = os.path.join(documents_dir, "pdfs")
doc = parse_pdf(os.path.join(pdf_dir, "messy_pdf.pdf"))
cleaned = preprocess(doc["content"])
chunks = semantic_chunk_with_line_overlap(cleaned, max_lines=3, overlap=1)

print("Line-based Chunking with Overlap (PDF)")
for i, chunk in enumerate(chunks, 1):
    print(f"--- Chunk {i} ---")
    print(chunk)
    print()

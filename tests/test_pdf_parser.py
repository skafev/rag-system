import os
from app.parsers.parsers import parse_pdf

documents_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "documents")
pdf_path = "pdfs/sample_1.pdf"
parsed_doc = parse_pdf(os.path.join(documents_dir, pdf_path))

print("Parsed PDF:")
print("Doc ID:", parsed_doc["doc_id"])
print("Metadata:", parsed_doc["metadata"])
print("\n--- Content Preview ---")
print(parsed_doc["content"][:200])

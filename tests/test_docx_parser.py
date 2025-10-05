import os
from app.parsers.parsers import parse_docx

documents_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "documents")
docx_path = "docx/notes_1.docx"
parsed_doc = parse_docx(os.path.join(documents_dir, docx_path))

print("Parsed DOCX:")
print("Doc ID:", parsed_doc["doc_id"])
print("Metadata:", parsed_doc["metadata"])
print("\n--- Content Preview ---")
print(parsed_doc["content"][:200])

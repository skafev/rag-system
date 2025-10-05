import os
from app.parsers.parsers import parse_html

documents_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "documents")
html_path = "html/article_1.html"
parsed_doc = parse_html(os.path.join(documents_dir, html_path))

print("Parsed HTML:")
print("Doc ID:", parsed_doc["doc_id"])
print("Metadata:", parsed_doc["metadata"])
print("\n--- Content Preview ---")
print(parsed_doc["content"][:200])

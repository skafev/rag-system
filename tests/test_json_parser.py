import os
from app.parsers.parsers import parse_json

documents_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "documents")
json_path = "json/product_1.json"
parsed_doc = parse_json(os.path.join(documents_dir, json_path))

print("Parsed JSON:")
print("Doc ID:", parsed_doc["doc_id"])
print("Metadata:", parsed_doc["metadata"])
print("\n--- Content Preview ---")
print(parsed_doc["content"])

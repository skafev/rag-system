import os
from app.parsers.parsers import parse_pdf, parse_docx, parse_html, parse_json
from app.utils.preprocess import preprocess

project_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
docs_to_test = {
    "pdf": "documents/pdfs/messy_pdf.pdf",
    "docx": "documents/docx/messy_docx.docx",
    "html": "documents/html/messy_html.html",
    "json": "documents/json/messy_json.json",
}

for doc_type, path in docs_to_test.items():
    print(f"{doc_type.upper()}")

    if doc_type == "pdf":
        parsed = parse_pdf(os.path.join(project_dir, path))
    elif doc_type == "docx":
        parsed = parse_docx(os.path.join(project_dir, path))
    elif doc_type == "html":
        parsed = parse_html(os.path.join(project_dir, path))
    elif doc_type == "json":
        parsed = parse_json(os.path.join(project_dir, path))

    cleaned_content = preprocess(parsed["content"])

    print("Doc ID:", parsed["doc_id"])
    print("Metadata:", parsed["metadata"])
    print("\n--- Cleaned Content Preview ---")
    print(cleaned_content[:200])
    print("\n-----------------------------")

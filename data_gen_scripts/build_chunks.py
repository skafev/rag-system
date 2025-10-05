import os
import json
from app.parsers.parsers import parse_pdf, parse_docx, parse_html, parse_json
from app.utils.preprocess import preprocess
from app.chunking import chunk_document


def process_all_documents(input_dir="documents", output_file="output/chunks.json"):
    """Creates chunks file based on processed documents."""
    all_chunks = []
    # Walk through subdirectories (pdfs, docx, html, json)
    for subdir, _, files in os.walk(input_dir):
        for file in files:
            path = os.path.join(subdir, file)
            if file.endswith(".pdf"):
                parsed = parse_pdf(path)
            elif file.endswith(".docx"):
                parsed = parse_docx(path)
            elif file.endswith(".html"):
                parsed = parse_html(path)
            elif file.endswith(".json"):
                parsed = parse_json(path)
            else:
                continue
            # Preprocess text
            cleaned = preprocess(parsed["content"])
            parsed["content"] = cleaned

            chunks = chunk_document(parsed, max_lines=5, overlap=1)
            # Add metadata to each chunk
            for i, chunk in enumerate(chunks, 1):
                all_chunks.append({
                    "id": f"{os.path.basename(path)}_chunk{i}",
                    "content": chunk,
                    "metadata": {
                        "doc_type": parsed["metadata"]["type"],
                        "source": path,
                        "chunk_index": i
                    }
                })
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, ensure_ascii=False, indent=2)

    print(f"Processed {len(all_chunks)} chunks saved to {output_file}")


if __name__ == "__main__":
    process_all_documents()

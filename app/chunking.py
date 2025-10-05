from typing import List


def semantic_chunk(text: str, max_chunk_size: int = 500) -> List[str]:
    """
    Splits text into semantic chunks using paragraphs, sentences,
    and keeps bullets/tables together.
    """
    lines = text.split("\n")
    chunks = []
    current_chunk = ""

    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        # If line is a bullet or table row, always keep with current chunk
        is_special_block = line.startswith("-") or "|" in line
        if len(current_chunk) + len(line) + 1 > max_chunk_size and not is_special_block:
            chunks.append(current_chunk.strip())
            current_chunk = line
        else:
            if current_chunk:
                current_chunk += "\n" + line
            else:
                current_chunk = line
        if i == len(lines) - 1 and current_chunk:
            chunks.append(current_chunk.strip())
    return chunks


def semantic_chunk_with_overlap(text: str, max_chunk_size: int = 500, overlap: int = 1) -> list:
    """
    Splits text into semantic chunks using paragraphs/sentences with overlap.
    overlap = number of lines (or sentences) to repeat in the next chunk.
    """
    lines = text.split("\n")
    chunks = []
    current_chunk_lines = []

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        current_chunk_lines.append(line)
        # Check if chunk reached max size
        current_text = "\n".join(current_chunk_lines)
        if len(current_text) >= max_chunk_size:
            chunks.append(current_text.strip())
            # Prepare next chunk with overlap
            current_chunk_lines = current_chunk_lines[-overlap:] if overlap > 0 else []
        i += 1
    if current_chunk_lines:
        chunks.append("\n".join(current_chunk_lines).strip())
    return chunks


def semantic_chunk_with_line_overlap(text: str, max_lines: int = 5, overlap: int = 1):
    """
    Splits text into chunks based on number of lines, with overlap.
    """
    lines = [line for line in text.split("\n") if line.strip()]
    chunks = []
    i = 0

    while i < len(lines):
        chunk_lines = lines[i:i+max_lines]
        chunks.append("\n".join(chunk_lines).strip())
        i += max_lines - overlap
    return chunks


def chunk_document(parsed_doc, max_lines=5, overlap=1):
    """
    Chooses chunking strategy based on document type.

    parsed_doc: dict with keys 'content' and 'metadata'
    """
    doc_type = parsed_doc['metadata'].get('type', 'unknown')
    text = parsed_doc['content']

    if doc_type == 'pdf':
        return semantic_chunk_with_line_overlap(text, max_lines=max_lines, overlap=overlap)
    elif doc_type == 'docx':
        return semantic_chunk_with_line_overlap(text, max_lines=max_lines, overlap=overlap)
    elif doc_type == 'html':
        lines = text.split("\n")
        filtered_lines = [l for l in lines if len(l.strip()) > 3]
        filtered_text = "\n".join(filtered_lines)
        return semantic_chunk_with_line_overlap(filtered_text, max_lines=max_lines, overlap=overlap)
    elif doc_type == 'json':
        lines = [line for line in text.split("\n") if line.strip()]
        return semantic_chunk_with_line_overlap("\n".join(lines), max_lines=max_lines, overlap=overlap)
    else:
        return semantic_chunk_with_line_overlap(text, max_lines=max_lines, overlap=overlap)

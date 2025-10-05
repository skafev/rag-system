import re


def clean_text(text: str) -> str:
    """
    Basic cleaning: whitespace, lists, page markers.
    """
    # Remove page markers like "--- Page 1 ---"
    text = re.sub(r"--- Page \d+ ---", "", text)

    # Normalize bullet points (convert •, *, etc. into "-")
    text = re.sub(r"[•*▪‣]", "-", text)

    # Clean each line separately to preserve structure
    lines = []
    for line in text.splitlines():
        line = re.sub(r"\s+", " ", line)
        if line.strip():
            lines.append(line.strip())

    return "\n".join(lines)


def normalize_lists(text: str) -> str:
    """
    Converts lines that look like lists into consistent Markdown-style lists.
    """
    lines = text.splitlines()
    new_lines = []
    for line in lines:
        if re.match(r"^\s*[-*]\s+", line):
            new_lines.append(line.strip())
        elif re.match(r"^\s*\d+\.\s+", line):
            new_lines.append(line.strip())
        else:
            new_lines.append(line.strip())
    return "\n".join(new_lines)


def normalize_tables(text: str) -> str:
    """
    Very simple table handling: replace multiple spaces with '|'.
    Works for extracted tables where columns are aligned.
    """
    lines = text.splitlines()
    new_lines = []
    for line in lines:
        if re.search(r"\s{2,}", line):
            cols = re.split(r"\s{2,}", line.strip())
            new_lines.append(" | ".join(cols))
        else:
            new_lines.append(line)
    return "\n".join(new_lines)


def preprocess(text: str) -> str:
    """
    Full preprocessing pipeline.
    """
    text = clean_text(text)
    text = normalize_lists(text)
    text = normalize_tables(text)
    return text

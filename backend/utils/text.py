"""Text processing utilities for keyword extraction and normalization."""

import re
from typing import List


def normalize_keyword(kw: str) -> str:
    """Lowercase, strip, and collapse whitespace."""
    return re.sub(r"\s+", " ", kw.strip().lower())


def extract_keywords(text: str) -> List[str]:
    """Simple keyword extraction from text.
    Splits on common delimiters and normalizes.
    For production, swap with NLP-based extraction.
    """
    delimiters = r"[,;|/\n]"
    parts = re.split(delimiters, text)
    keywords = []
    for part in parts:
        normalized = normalize_keyword(part)
        if normalized and len(normalized) >= 2:
            keywords.append(normalized)
    return list(dict.fromkeys(keywords))  # deduplicate preserving order

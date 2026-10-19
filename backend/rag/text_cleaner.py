"""
backend/rag/text_cleaner.py

Deterministic biomedical text normalisation.

RULES:
  - Collapse excessive whitespace (multiple spaces → one space).
  - Collapse excessive blank lines (3+ consecutive → 2).
  - Remove soft-hyphen line-break artifacts (word- \\nword → wordword).
  - Strip leading/trailing whitespace per line.
  - Do NOT remove medical terminology, drug names, citations, or numbers.
  - Do NOT paraphrase or rewrite the source text.
"""

import re


# Pre-compiled patterns (compile once at module load)
_SOFT_HYPHEN_BREAK = re.compile(r"-\s*\n\s*")         # word- \n continuation
_MULTIPLE_SPACES = re.compile(r"[ \t]+")               # horizontal whitespace
_MULTIPLE_NEWLINES = re.compile(r"\n{3,}")             # 3+ blank lines → 2
_LEADING_TRAILING_LINE = re.compile(r"^[ \t]+|[ \t]+$", re.MULTILINE)


def clean_text(text: str) -> str:
    """
    Apply deterministic biomedical text normalisation.

    Args:
        text: Raw extracted text from a PDF page.

    Returns:
        Cleaned text preserving all medical content.
    """
    if not text:
        return ""

    # 1. Rejoin soft-hyphen line breaks (e.g. "cogni-\ntive" → "cognitive")
    text = _SOFT_HYPHEN_BREAK.sub("", text)

    # 2. Strip leading/trailing whitespace from each line
    text = _LEADING_TRAILING_LINE.sub("", text)

    # 3. Collapse multiple horizontal spaces to one
    text = _MULTIPLE_SPACES.sub(" ", text)

    # 4. Collapse 3+ consecutive blank lines to 2
    text = _MULTIPLE_NEWLINES.sub("\n\n", text)

    # 5. Final strip
    return text.strip()

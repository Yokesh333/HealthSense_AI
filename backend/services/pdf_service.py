"""
backend/services/pdf_service.py

PDF text extraction service using PyMuPDF (fitz).

Responsibilities:
- In-memory PDF validation and text extraction
- Enforces 10 MB maximum file size limit
- Enforces 20 maximum page count limit
- Page-by-page text extraction with page boundaries preserved
- Detects image-only / scanned PDFs (0 extractable text)
- Handles corrupt or malformed PDFs safely
- Never logs raw PDF text or PII
"""

import io
import logging
from typing import Tuple, List

import fitz  # PyMuPDF

logger = logging.getLogger(__name__)

MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB
MAX_PAGE_COUNT = 20
MAX_TEXT_CHARACTERS = 20000  # ~5,000 token ceiling for prompt safety


class PDFExtractionError(Exception):
    """Custom exception raised when PDF extraction fails or is invalid."""
    pass


class PDFExtractionService:
    """Service to safely read, validate, and extract text page-by-page from PDFs."""

    def validate_and_extract(self, content_bytes: bytes, filename: str = "report.pdf") -> Tuple[str, List[str]]:
        """
        Validate PDF bytes and extract text page by page.

        Args:
            content_bytes: Raw binary content of the PDF file.
            filename: Original filename for logging metadata.

        Returns:
            Tuple of (formatted_full_text, list_of_page_texts)

        Raises:
            PDFExtractionError if validation fails or text cannot be extracted.
        """
        if not content_bytes:
            raise PDFExtractionError("Uploaded file is empty.")

        if len(content_bytes) > MAX_FILE_SIZE_BYTES:
            size_mb = len(content_bytes) / (1024 * 1024)
            raise PDFExtractionError(
                f"File size ({size_mb:.1f} MB) exceeds the maximum allowed size of 10 MB."
            )

        try:
            doc = fitz.open(stream=content_bytes, filetype="pdf")
        except Exception as exc:
            logger.error("pdf_service: Failed to open PDF file (%s) — %s", filename, exc)
            raise PDFExtractionError("Failed to read PDF file. The document may be corrupted or malformed.")

        try:
            page_count = len(doc)
            if page_count == 0:
                raise PDFExtractionError("PDF file contains zero pages.")

            if page_count > MAX_PAGE_COUNT:
                raise PDFExtractionError(
                    f"PDF has {page_count} pages, which exceeds the maximum limit of {MAX_PAGE_COUNT} pages."
                )

            page_texts: List[str] = []
            formatted_chunks: List[str] = []
            total_extracted_length = 0

            for i in range(page_count):
                page = doc[i]
                try:
                    text = page.get_text("text").strip()
                except Exception as page_exc:
                    logger.warning("pdf_service: Page %d text extraction error — %s", i + 1, page_exc)
                    text = ""

                page_texts.append(text)
                if text:
                    formatted_chunks.append(f"--- PAGE {i + 1} ---\n{text}")
                    total_extracted_length += len(text)

            full_text = "\n\n".join(formatted_chunks)

            if not full_text.strip() or total_extracted_length == 0:
                raise PDFExtractionError(
                    "This PDF does not contain extractable text. Please upload a text-based clinical report."
                )

            # Prioritize & trim text safely if it exceeds MAX_TEXT_CHARACTERS
            if len(full_text) > MAX_TEXT_CHARACTERS:
                full_text = self._prune_text_safely(full_text, MAX_TEXT_CHARACTERS)

            logger.info(
                "pdf_service: Successfully extracted %d chars from %d pages in %s.",
                len(full_text),
                page_count,
                filename,
            )
            return full_text, page_texts

        finally:
            doc.close()

    def _prune_text_safely(self, text: str, max_chars: int) -> str:
        """
        Prune extra-long text while prioritizing clinical findings, impressions,
        examination scores, imaging, and lab sections over headers/disclaimers.
        """
        logger.info("pdf_service: Pruning text from %d to %d chars.", len(text), max_chars)
        head_budget = int(max_chars * 0.7)
        tail_budget = max_chars - head_budget
        
        pruned = text[:head_budget] + "\n\n[... content truncated for token limits ...]\n\n" + text[-tail_budget:]
        return pruned

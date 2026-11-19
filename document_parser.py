"""
DocuSpeak – Document Parser
Reads PDF, DOCX, TXT, RTF, EPUB, images (OCR), and plain text files.
Returns the raw text WITHOUT any modification of the original content.
"""
from __future__ import annotations
import io
import os
import re
import pathlib
import chardet

# ── PDF ─────────────────────────────────────────────────────────────────────
def _parse_pdf(data: bytes) -> str:
    """Use PyMuPDF for accurate PDF text extraction."""
    try:
        import pymupdf as fitz  # pymupdf >= 1.24
    except ImportError:
        import fitz  # older pymupdf
    doc = fitz.open(stream=data, filetype="pdf")
    pages = []
    for page in doc:
        pages.append(page.get_text("text"))
    doc.close()
    return "\n".join(pages)


# ── DOCX ─────────────────────────────────────────────────────────────────────
def _parse_docx(data: bytes) -> str:
    from docx import Document
    doc = Document(io.BytesIO(data))
    paragraphs = [p.text for p in doc.paragraphs]
    # Also read tables
    for table in doc.tables:
        for row in table.rows:
            paragraphs.append("\t".join(cell.text for cell in row.cells))
    return "\n".join(paragraphs)


# ── RTF ──────────────────────────────────────────────────────────────────────
def _parse_rtf(data: bytes) -> str:
    from striprtf.striprtf import rtf_to_text
    text = rtf_to_text(data.decode("utf-8", errors="replace"))
    return text


# ── EPUB ─────────────────────────────────────────────────────────────────────
def _parse_epub(data: bytes) -> str:
    import ebooklib
    from ebooklib import epub
    from html.parser import HTMLParser

    class _MLStripper(HTMLParser):
        def __init__(self):
            super().__init__()
            self.fed: list[str] = []
        def handle_data(self, d):
            self.fed.append(d)
        def get_data(self):
            return " ".join(self.fed)

    # ebooklib needs a file path; write to a temp file
    import tempfile, uuid
    tmp = pathlib.Path(tempfile.gettempdir()) / f"{uuid.uuid4()}.epub"
    tmp.write_bytes(data)
    try:
        book = epub.read_epub(str(tmp))
        chunks = []
        for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
            s = _MLStripper()
            s.feed(item.get_body_content().decode("utf-8", errors="replace"))
            chunks.append(s.get_data())
        return "\n".join(chunks)
    finally:
        tmp.unlink(missing_ok=True)


# ── Plain text / CSV / Markdown ───────────────────────────────────────────────
def _parse_text(data: bytes) -> str:
    detected = chardet.detect(data)
    enc = detected.get("encoding") or "utf-8"
    return data.decode(enc, errors="replace")


# ── Images with OCR ───────────────────────────────────────────────────────────
def _parse_image(data: bytes) -> str:
    """Extract text from images via pytesseract OCR (if available)."""
    try:
        import pytesseract
        from PIL import Image
        img = Image.open(io.BytesIO(data))
        return pytesseract.image_to_string(img)
    except ImportError:
        return "[OCR unavailable: install pytesseract + Tesseract binary]"
    except Exception as e:
        return f"[OCR error: {e}]"


# ── Dispatcher ────────────────────────────────────────────────────────────────
EXT_MAP = {
    ".pdf":  _parse_pdf,
    ".docx": _parse_docx,
    ".doc":  _parse_docx,   # legacy; works if saved as docx
    ".rtf":  _parse_rtf,
    ".epub": _parse_epub,
    ".txt":  _parse_text,
    ".md":   _parse_text,
    ".csv":  _parse_text,
    ".log":  _parse_text,
    ".json": _parse_text,
    ".xml":  _parse_text,
    ".html": _parse_text,
    ".htm":  _parse_text,
    ".png":  _parse_image,
    ".jpg":  _parse_image,
    ".jpeg": _parse_image,
    ".bmp":  _parse_image,
    ".tiff": _parse_image,
    ".tif":  _parse_image,
    ".webp": _parse_image,
}


def parse_document(filename: str, data: bytes) -> str:
    """
    Parse *data* bytes as a document named *filename*.
    Returns extracted text verbatim – no rewording or AI summarisation.
    """
    ext = pathlib.Path(filename).suffix.lower()
    parser = EXT_MAP.get(ext)
    if parser is None:
        # Try as plain text as a last resort
        try:
            return _parse_text(data)
        except Exception:
            raise ValueError(f"Unsupported file type: {ext!r}")
    try:
        text = parser(data)
    except Exception as exc:
        raise RuntimeError(f"Parsing failed for {filename!r}: {exc}") from exc

    # Normalise excessive blank lines (cosmetic only – no content change)
    text = re.sub(r"\n{4,}", "\n\n\n", text)
    return text.strip()

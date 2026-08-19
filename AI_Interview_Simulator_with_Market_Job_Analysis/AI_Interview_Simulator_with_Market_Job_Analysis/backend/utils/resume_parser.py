"""
Resume File Parser Utility
Extracts plain text from PDF and DOCX resume files.
Used before passing to resume_service for scoring.
"""
try:
    import fitz      # PyMuPDF — for PDF
except Exception:
    fitz = None

try:
    import docx      # python-docx — for DOCX
except Exception:
    docx = None
import io


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """
    Extract plain text from a PDF resume.

    Args:
        pdf_bytes: raw bytes of a PDF file

    Returns:
        Extracted text as a single string
    """
    text_parts = []
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        for page in doc:
            text_parts.append(page.get_text("text"))
        doc.close()
    except Exception as e:
        raise ValueError(f"Could not parse PDF: {str(e)}")

    return "\n".join(text_parts).strip()


def extract_text_from_docx(docx_bytes: bytes) -> str:
    """
    Extract plain text from a DOCX resume.

    Args:
        docx_bytes: raw bytes of a .docx file

    Returns:
        Extracted text as a single string
    """
    try:
        doc     = docx.Document(io.BytesIO(docx_bytes))
        text    = "\n".join(para.text for para in doc.paragraphs if para.text.strip())
        return text.strip()
    except Exception as e:
        raise ValueError(f"Could not parse DOCX: {str(e)}")


def extract_text_from_file(file_bytes: bytes, filename: str) -> str:
    """
    Auto-detect file type and extract text.

    Args:
        file_bytes: raw file bytes
        filename: original filename (to detect extension)

    Returns:
        Extracted text
    """
    ext = filename.rsplit(".", 1)[-1].lower()

    if ext == "pdf":
        return extract_text_from_pdf(file_bytes)
    elif ext in ("docx", "doc"):
        return extract_text_from_docx(file_bytes)
    elif ext == "txt":
        return file_bytes.decode("utf-8", errors="ignore")
    else:
        raise ValueError(f"Unsupported file type: .{ext}. Use PDF, DOCX, or TXT.")
    if fitz is None:
        raise ValueError("PDF parsing is unavailable: install PyMuPDF to enable PDF uploads.")

    if docx is None:
        raise ValueError("DOCX parsing is unavailable: install python-docx to enable DOCX uploads.")

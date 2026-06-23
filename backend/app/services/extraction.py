import logging
from pypdf import PdfReader
from docx import Document as DocxDocument

logger = logging.getLogger(__name__)

def extract_text_from_file(file_path: str, mime_type: str) -> str:
    """Extract text content based on file mime type."""
    try:
        if mime_type == "application/pdf":
            return _extract_from_pdf(file_path)
        elif mime_type in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/msword"]:
            return _extract_from_docx(file_path)
        elif mime_type == "text/plain":
            return _extract_from_txt(file_path)
        else:
            raise ValueError(f"Unsupported mime type: {mime_type}")
    except Exception as e:
        logger.error(f"Error extracting text from {file_path}: {str(e)}")
        raise

def _extract_from_pdf(file_path: str) -> str:
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + "\n"
    return text.strip()

def _extract_from_docx(file_path: str) -> str:
    doc = DocxDocument(file_path)
    return "\n".join([paragraph.text for paragraph in doc.paragraphs])

def _extract_from_txt(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

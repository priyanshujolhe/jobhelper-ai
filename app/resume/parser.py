import os
import pypdf
import docx
from pathlib import Path


class ResumeParseError(Exception):
    pass


def extract_text_from_pdf(file_path: str) -> str:
    """
    Extracts text from a PDF file using pypdf.
    Handles multi-page documents and handles scanned/unreadable PDFs gracefully.
    """
    try:
        reader = pypdf.PdfReader(file_path)
        if len(reader.pages) == 0:
            raise ResumeParseError("The uploaded PDF has no pages.")

        extracted_pages = []
        for i, page in enumerate(reader.pages):
            page_text = page.extract_text() or ""
            extracted_pages.append(page_text.strip())

        full_text = "\n\n".join(extracted_pages).strip()

        if len(full_text) < 30:
            # Document has virtually no text - likely scanned image PDF
            raise ResumeParseError(
                "Could not extract sufficient text from this PDF. "
                "It appears to be a scanned image or rasterized document without an OCR text layer. "
                "Please upload a text-selectable PDF or DOCX file."
            )

        return full_text
    except ResumeParseError:
        raise
    except Exception as e:
        raise ResumeParseError(f"Error reading PDF file: {str(e)}")


def extract_text_from_docx(file_path: str) -> str:
    """
    Extracts text from a DOCX file using python-docx, including paragraphs and tables.
    """
    try:
        doc = docx.Document(file_path)
        parts = []

        # Extract regular paragraphs
        for p in doc.paragraphs:
            text = p.text.strip()
            if text:
                parts.append(text)

        # Also extract text from any tables in the document
        for table in doc.tables:
            for row in table.rows:
                row_cells = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                if row_cells:
                    parts.append(" | ".join(row_cells))

        full_text = "\n".join(parts).strip()
        if len(full_text) < 20:
            raise ResumeParseError("The uploaded DOCX file appears to be empty or contains no readable text.")

        return full_text
    except ResumeParseError:
        raise
    except Exception as e:
        raise ResumeParseError(f"Error reading DOCX file: {str(e)}")


def parse_resume_file(file_path: str) -> str:
    """
    Detects file extension and extracts text.
    """
    ext = Path(file_path).suffix.lower()
    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif ext in {".docx", ".doc"}:
        return extract_text_from_docx(file_path)
    else:
        raise ResumeParseError(f"Unsupported file format '{ext}'. Please upload a PDF or DOCX resume.")

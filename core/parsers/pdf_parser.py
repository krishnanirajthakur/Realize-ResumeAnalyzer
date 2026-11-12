"""
PyMuPDF (fitz) PDF Document Parser
"""
import io
from typing import Dict, Any, Tuple
from core.preprocessing.text_cleaner import clean_text

class PDFParsingError(Exception):
    """Raised when a PDF cannot be parsed or is corrupted."""
    pass

def parse_pdf(file_input) -> Tuple[str, Dict[str, Any]]:
    """
    Extract text and metadata from PDF bytes, path, or file-like object using PyMuPDF.
    
    Returns:
        (extracted_text, metadata_dict)
    """
    try:
        import pymupdf as fitz
    except ImportError:
        import fitz  # PyMuPDF fallback
    
    try:
        if isinstance(file_input, (str, bytes)):
            if isinstance(file_input, str):
                doc = fitz.open(file_input)
            else:
                doc = fitz.open(stream=file_input, filetype="pdf")
        elif hasattr(file_input, "read"):
            content = file_input.read()
            if hasattr(file_input, "seek"):
                file_input.seek(0)
            doc = fitz.open(stream=content, filetype="pdf")
        else:
            raise PDFParsingError("Unsupported file input type for PDF parsing.")
            
        metadata = {
            "page_count": len(doc),
            "format": "PDF",
            "author": doc.metadata.get("author", ""),
            "title": doc.metadata.get("title", ""),
        }
        
        extracted_pages = []
        for page_num in range(len(doc)):
            page = doc[page_num]
            # Use sort=True to ensure logical reading order in multi-column layouts
            page_text = page.get_text("text", sort=True)
            if page_text:
                extracted_pages.append(page_text)
                
        doc.close()
        
        full_text = "\n\n".join(extracted_pages)
        sanitized_text = clean_text(full_text)
        
        if not sanitized_text.strip():
            metadata["warning"] = "PDF parsed but yielded empty text (may contain scanned image text)."
            
        return sanitized_text, metadata
        
    except Exception as e:
        raise PDFParsingError(f"Error parsing PDF document: {str(e)}") from e

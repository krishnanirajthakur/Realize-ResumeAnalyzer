"""
python-docx Document Parser
"""
import io
from typing import Dict, Any, Tuple
from core.preprocessing.text_cleaner import clean_text

class DOCXParsingError(Exception):
    """Raised when a DOCX cannot be parsed or is corrupted."""
    pass

def parse_docx(file_input) -> Tuple[str, Dict[str, Any]]:
    """
    Extract text and table content from DOCX bytes, path, or file-like object.
    
    Returns:
        (extracted_text, metadata_dict)
    """
    import docx
    
    try:
        if isinstance(file_input, str):
            doc = docx.Document(file_input)
        elif isinstance(file_input, bytes):
            doc = docx.Document(io.BytesIO(file_input))
        elif hasattr(file_input, "read"):
            content = file_input.read()
            if hasattr(file_input, "seek"):
                file_input.seek(0)
            doc = docx.Document(io.BytesIO(content))
        else:
            raise DOCXParsingError("Unsupported file input type for DOCX parsing.")
            
        paragraphs = []
        for p in doc.paragraphs:
            if p.text.strip():
                paragraphs.append(p.text.strip())
                
        # Also extract table text (often used in resumes for skills/experience matrices)
        table_rows = []
        for table in doc.tables:
            for row in table.rows:
                cells = [c.text.strip() for c in row.cells if c.text.strip()]
                if cells:
                    table_rows.append(" | ".join(cells))
                    
        metadata = {
            "paragraph_count": len(paragraphs),
            "table_count": len(doc.tables),
            "format": "DOCX"
        }
        
        full_text = "\n".join(paragraphs)
        if table_rows:
            full_text += "\n\n" + "\n".join(table_rows)
            
        sanitized_text = clean_text(full_text)
        return sanitized_text, metadata
        
    except Exception as e:
        raise DOCXParsingError(f"Error parsing DOCX document: {str(e)}") from e

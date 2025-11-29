import pdfplumber
from agents import function_tool
from tools.shared import log

@function_tool
def extract_text_from_pdf(file_path: str) -> str:
    """
    Extracts all text from a PDF file using pdfplumber for high accuracy.
    
    Args:
        file_path: The path to the PDF file.
        
    Returns:
        A string containing all the text extracted from the PDF.
    """
    log(f"📖 Extracting text from PDF: {file_path}")
    try:
        text_content = []
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    text_content.append(text)
        
        full_text = "\n".join(text_content)
        return full_text
    except Exception as e:
        return f"Error extracting text from PDF: {str(e)}"

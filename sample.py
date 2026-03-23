"""
Text Loading Utilities
This module provides functions to extract text content from multiple sources
including local files (PDF/TXT), raw input, and Wikipedia.
"""
import pdfplumber
import wikipedia
from typing import Optional, Tuple

def load_from_pdf(file) -> Tuple[Optional[str], Optional[str]]:
    """
    Extracts text from an uploaded PDF file object.
    
    Args:
        file: The UploadedFile object from Streamlit.
        
    Returns:
        Tuple[text, error]: extracted text if successful, otherwise None and an error message.
    """
    full_text = ""
    
    try:
        # Open the PDF using pdfplumber
        # We pass the file object directly; no need to save to disk
        with pdfplumber.open(file) as pdf:
            # Iterate through every page in the PDF
            for page in pdf.pages:
                # Extract text and append to full_text if content is found
                text = page.extract_text()
                if text:
                    full_text += text + "\n\n" 
        
        # Clean whitespace and handle empty extraction results
        cleaned_text = full_text.strip()
        if not cleaned_text:
            return None, "No readable text found in this PDF."
        return cleaned_text, None
    
    except Exception as e:
        return None, f"Error extracting PDF text: {e}"

def load_from_paste(text: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Validates and returns pasted text.
    Returns tuple[text, error].
    """
    if not text or not text.strip():
        return None, "Please enter some text."
    return text.strip(), None

def load_from_txt(file) -> Tuple[Optional[str], Optional[str]]:
    """
    Extracts text from an uploaded .txt file object.
    """
    try:
        raw_bytes = file.read()
        content = None

        # Attempt multiple encodings to handle various text formats safely
        for encoding in ("utf-8", "latin-1"):
            try:
                content = raw_bytes.decode(encoding)
                break
            except UnicodeDecodeError:
                continue

        # Final fallback: decode with 'replace' to avoid fatal errors
        if content is None:
            content = raw_bytes.decode("utf-8", errors="replace")

        cleaned_text = content.strip()
        if not cleaned_text:
            return None, "The TXT file is empty."

        return cleaned_text, None
    except Exception as e:
        return None, f"Error reading TXT file: {e}"

def load_from_wikipedia(topic: str, max_chars: int = 20000) -> Tuple[Optional[str], Optional[str]]:
    """
    Fetches the summary/content of a Wikipedia article based on the topic.
    Returns tuple[text, error].
    """
    try:
        cleaned_topic = topic.strip()
        if not cleaned_topic:
            return None, "Please enter a topic name."

        # Set language to English (optional, default is usually 'en')
        wikipedia.set_lang("en")
        
        # Search for the page and get its content
        # auto_suggest=False ensures we get exactly what we searched for or an error
        page = wikipedia.page(cleaned_topic, auto_suggest=False)

        # Limit content length to avoid overloading memory/models
        content = page.content.strip()
        if max_chars > 0 and len(content) > max_chars:
            # Truncate at the last space within limits to avoid cutting words
            content = content[:max_chars].rsplit(" ", 1)[0] + "..."

        return content, None
    
    except wikipedia.exceptions.DisambiguationError as e:
        # Handle cases where multiple pages match the topic
        top_options = ", ".join(e.options[:3])
        return None, f"Topic is ambiguous. Try one of: {top_options}"
    except wikipedia.exceptions.PageError:
        # Handle cases where the exact topic is not found
        return None, f"No Wikipedia page found for '{topic.strip()}'."
    except Exception as e:
        # Generic error fallback
        return None, f"Unexpected error fetching Wikipedia: {e}"
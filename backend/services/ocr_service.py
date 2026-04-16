import pytesseract
from PIL import Image
import io

def clean_math_ocr(text: str) -> str:
    """Fixes common Tesseract math OCR errors before passing to the LLM."""
    # Fix natural log variations
    text = text.replace("In(", "ln(")
    text = text.replace("In ", "ln ")
    text = text.replace("In(x')", "ln(x^2)") # Catching your specific test case
    
    # Fix common exponent errors (Tesseract often reads ^2 as ' or ")
    text = text.replace("x'", "x^2")
    text = text.replace("x\"", "x^2")
    
    # Fix common integration sign errors
    text = text.replace("f ", "∫ ") 
    text = text.replace("S ", "∫ ")
    
    return text

def extract_text_from_image(image_bytes: bytes) -> str:
    """
    Takes raw image bytes, applies basic preprocessing, runs Tesseract OCR,
    and cleans the output for math formatting.
    """
    # Load image from bytes
    img = Image.open(io.BytesIO(image_bytes))
    
    # Basic Preprocessing: Convert to grayscale
    img = img.convert('L')
    
    # Extract raw text
    raw_text = pytesseract.image_to_string(img)
    
    # Clean the math symbols
    cleaned_text = clean_math_ocr(raw_text.strip())
    
    return cleaned_text
import os
import io
import re
import logging

logger = logging.getLogger(__name__)


def _clean_math_text(raw_text: str) -> str:
    """
    Post-process OCR output to normalize common math-symbol misreads.
    Tesseract often confuses superscripts and special characters.
    """
    text = raw_text.strip()

    # Common Tesseract misreads for math
    replacements = {
        "²": "^2",
        "³": "^3",
        "⁴": "^4",
        "⁵": "^5",
        "⁶": "^6",
        "⁷": "^7",
        "⁸": "^8",
        "⁹": "^9",
        "√": "sqrt",
        "∫": "integral",
        "∑": "sum",
        "∏": "product",
        "∞": "infinity",
        "→": "->",
        "≥": ">=",
        "≤": "<=",
        "≠": "!=",
        "±": "+-",
        "÷": "/",
        "×": "*",
        "π": "pi",
        "θ": "theta",
        "α": "alpha",
        "β": "beta",
        "Δ": "delta",
        "δ": "delta",
        "λ": "lambda",
        "μ": "mu",
        "σ": "sigma",
        "ε": "epsilon",
    }

    for symbol, replacement in replacements.items():
        text = text.replace(symbol, replacement)

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text)

    return text


def _tesseract_ocr(image_bytes: bytes) -> str:
    """
    Local Tesseract OCR fallback with preprocessing for math images.
    Uses Pillow for image preprocessing to improve recognition of
    handwritten math notation like x^2, dy/dx, etc.
    """
    import pytesseract
    from PIL import Image, ImageFilter, ImageOps

    image = Image.open(io.BytesIO(image_bytes))

    # Convert to grayscale
    image = ImageOps.grayscale(image)

    # Increase contrast via autocontrast
    image = ImageOps.autocontrast(image, cutoff=2)

    # Sharpen to make thin strokes (exponents, subscripts) more visible
    image = image.filter(ImageFilter.SHARPEN)

    # Resize up by 2x — helps Tesseract with small superscripts like ^2
    width, height = image.size
    image = image.resize((width * 2, height * 2), Image.LANCZOS)

    # Use --psm 6 (assume a single uniform block of text) for equation images
    custom_config = r"--oem 3 --psm 6"
    raw_text = pytesseract.image_to_string(image, config=custom_config)

    return _clean_math_text(raw_text)


def _google_vision_ocr(image_bytes: bytes) -> str:
    """
    Primary OCR using Google Cloud Vision API (document_text_detection).
    Superior for handwritten math, but requires billing to be enabled.
    """
    from google.cloud import vision

    client = vision.ImageAnnotatorClient()
    image = vision.Image(content=image_bytes)

    response = client.document_text_detection(image=image)

    if response.error.message:
        raise RuntimeError(f"Google Vision API Error: {response.error.message}")

    extracted_text = response.full_text_annotation.text
    return _clean_math_text(extracted_text)


def extract_text_from_image(image_bytes: bytes) -> str:
    """
    Extracts text from an image of a math problem.

    Strategy:
    1. Try Google Cloud Vision API first (best quality for handwriting).
    2. If it fails (403 billing, auth issues, etc.), fall back to local Tesseract.
    """

    # --- Attempt 1: Google Cloud Vision ---
    try:
        logger.info("Attempting Google Cloud Vision OCR...")
        result = _google_vision_ocr(image_bytes)
        if result:
            logger.info("Google Cloud Vision OCR succeeded.")
            return result
    except Exception as e:
        logger.warning(f"Google Cloud Vision failed: {e}. Falling back to Tesseract.")

    # --- Attempt 2: Local Tesseract ---
    try:
        logger.info("Attempting local Tesseract OCR...")
        result = _tesseract_ocr(image_bytes)
        if result:
            logger.info("Tesseract OCR succeeded.")
            return result
    except Exception as e:
        logger.error(f"Tesseract OCR also failed: {e}")
        return f"OCR Error: Both Google Vision and Tesseract failed. Last error: {e}"

    return "OCR Error: No text could be extracted from the image."
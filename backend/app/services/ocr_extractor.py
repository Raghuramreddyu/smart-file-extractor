import pytesseract
from PIL import Image

# Set the path to the Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def extract_text(image: Image.Image) -> str:
    text = pytesseract.image_to_string(image)
    print("\n📝 OCR Extracted Text:\n", text)  # Add this line for debugging
    return text

import io
import re
import cv2
import numpy as np
import pytesseract
import pdfplumber
from PIL import Image, ImageEnhance, ImageFilter


def preprocess_image(image: Image.Image) -> np.ndarray:
    """Preprocess image to enhance OCR accuracy."""
    image = image.convert("L")  # grayscale
    image = image.resize((image.width * 3, image.height * 3), Image.LANCZOS)
    image = ImageEnhance.Contrast(image).enhance(2.5)
    image = image.filter(ImageFilter.EDGE_ENHANCE_MORE)
    return np.array(image)


def clean_text(text: str) -> str:
    """Clean text by removing unwanted characters."""
    return re.sub(r"[^\w\s.,:/()-]", "", text.replace("\n", " ")).strip()


def is_valid_cell(cell: str) -> bool:
    """Return True if cell has alphanumeric characters."""
    return bool(re.search(r"[A-Za-z0-9]", cell))


def is_noise_cell(cell: str) -> bool:
    """Detect if cell is mostly gibberish/noise."""
    cleaned = re.sub(r"[^\w]", "", cell)
    if len(cell) == 0:
        return True
    return len(cleaned) / len(cell) < 0.4


def is_valid_row(row, min_valid=0.5):
    """Check if a row is valid based on number of good cells."""
    valid_cells = sum(1 for cell in row if is_valid_cell(cell))
    return valid_cells >= int(len(row) * min_valid)


def fix_row_length(row, length):
    """Pad or trim rows to match header length."""
    return row + [""] * (length - len(row)) if len(row) < length else row[:length]


def is_likely_header(row):
    """Detect if row is probably a header."""
    return sum(1 for cell in row if re.search(r"[A-Za-z]{2,}", cell)) >= 2


def extract_table_data_from_pdf(pdf_bytes: bytes):
    """Extract tables from text-based PDFs using pdfplumber."""
    try:
        tables = []
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            for page in pdf.pages:
                for table in page.extract_tables():
                    if not table or len(table) < 2:
                        continue
                    headers = [clean_text(cell or "") for cell in table[0]]
                    rows = [
                        fix_row_length([clean_text(cell or "") for cell in row], len(headers))
                        for row in table[1:]
                        if any(is_valid_cell(cell or "") for cell in row)
                    ]
                    tables.append({"headers": headers, "rows": rows})
        return tables
    except Exception as e:
        print("❌ PDF table extraction failed:", e)
        return []


def extract_table_data_from_image(image: Image.Image):
    """Extract tables from images using OpenCV + Tesseract OCR."""
    try:
        processed = preprocess_image(image)
        _, binary = cv2.threshold(processed, 180, 255, cv2.THRESH_BINARY_INV)

        # Detect lines (table structure)
        kernel_h = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
        kernel_v = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))
        mask = cv2.add(
            cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel_h),
            cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel_v)
        )

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        boxes = sorted([cv2.boundingRect(c) for c in contours if cv2.contourArea(c) > 100], key=lambda b: (b[1], b[0]))

        # Group into rows
        rows, current_row, last_y = [], [], -1
        for x, y, w, h in boxes:
            if last_y == -1 or abs(y - last_y) <= 15:
                current_row.append((x, y, w, h))
                last_y = y
            else:
                rows.append(sorted(current_row, key=lambda b: b[0]))
                current_row = [(x, y, w, h)]
                last_y = y
        if current_row:
            rows.append(sorted(current_row, key=lambda b: b[0]))

        # OCR each cell
        table = []
        for row in rows:
            row_data = []
            for x, y, w, h in row:
                roi = processed[y:y+h, x:x+w]
                text = clean_text(pytesseract.image_to_string(roi, config="--psm 6"))
                row_data.append(text)
            if any(is_valid_cell(cell) for cell in row_data):
                table.append(row_data)

        if not table or len(table) < 2:
            return []

        # Detect header
        for i, row in enumerate(table):
            if is_likely_header(row):
                headers = [cell for cell in row if not is_noise_cell(cell)]
                body = table[i + 1:]
                break
        else:
            headers, body = table[0], table[1:]

        # Clean and normalize rows
        cleaned_rows = [
            fix_row_length(row, len(headers))
            for row in body
            if is_valid_row(row)
        ]

        if not headers or not cleaned_rows:
            return []

        return [{"headers": headers, "rows": cleaned_rows}]
    except Exception as e:
        print("❌ Image table extraction failed:", e)
        return []

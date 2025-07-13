import traceback
from fastapi import UploadFile
from fastapi.responses import JSONResponse
from pdf2image import convert_from_bytes
from PIL import Image, UnidentifiedImageError
from io import StringIO
import sys

from app.services.ocr_extractor import extract_text
from app.services.ner_extractor import extract_entities
from app.services.table_extractor import (
    extract_table_data_from_pdf,
    extract_table_data_from_image
)
from app.schemas.models import ExtractionResult

POPPLER_PATH = r"C:\Users\91630\Downloads\poppler-24.08.0\Library\bin"

async def process_file(file: UploadFile):
    try:
        # Capture stdout logs for debug
        log_stream = StringIO()
        sys.stdout = log_stream

        # Step 1: Read file
        content = await file.read()
        extension = file.filename.split('.')[-1].lower()

        image = None
        table_data = []

        # Step 2: PDF or image logic
        if extension == "pdf":
            print("📄 Processing PDF...")
            table_data = extract_table_data_from_pdf(content)

            image = convert_from_bytes(content, poppler_path=POPPLER_PATH)[0]

            if not table_data:
                print("⚠️ No structured tables found in PDF. Using OCR fallback...")
                table_data = extract_table_data_from_image(image)

        else:
            try:
                image = Image.open(file.file)
                table_data = extract_table_data_from_image(image)
            except UnidentifiedImageError:
                raise ValueError("Unsupported or corrupted image format.")

        # Step 3: OCR text + NER
        print("\n🧠 Running OCR + Entity Extraction...")
        text = extract_text(image)
        entity_data = extract_entities(text)

        # Final step: Capture logs + return response
        sys.stdout = sys.__stdout__
        debug_log = log_stream.getvalue()

        # Ensure tables conform to list of dicts with 'headers' and 'rows'
        formatted_tables = []
        for t in table_data:
            if "headers" in t and "rows" in t:
                formatted_tables.append({
                    "headers": [str(h).strip() for h in t["headers"]],
                    "rows": [[str(cell).strip() for cell in row] for row in t["rows"]]
                })

        return {
            "entities": entity_data.get("entities", []),
            "dates": entity_data.get("dates", []),
            "addresses": entity_data.get("addresses", []),
            "tables": formatted_tables,
            "debug": debug_log.strip().splitlines()
        }

    except Exception as e:
        sys.stdout = sys.__stdout__
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": str(e)})

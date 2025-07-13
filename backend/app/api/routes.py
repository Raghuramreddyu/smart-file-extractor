from fastapi import APIRouter, File, UploadFile
from app.services.file_processor import process_file
from app.schemas.models import ExtractionResult

router = APIRouter()

@router.post("/extract", response_model=ExtractionResult)
async def extract_data(file: UploadFile = File(...)):
    return await process_file(file)

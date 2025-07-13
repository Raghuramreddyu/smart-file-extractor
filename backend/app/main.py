from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # ✅ Add this
from app.api.routes import router

app = FastAPI(
    title="Piazza Data Extraction API",
    description="Extracts structured data from PDFs and images using Hugging Face and Tesseract",
    version="1.0.0"
)

# ✅ Allow requests from your frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Or ["*"] for testing only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")

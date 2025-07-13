# 🧠 Smart File Extractor

Smart File Extractor is a full-stack application designed to extract structured data from PDF and image files.

✨ It supports:

- 📌 Named Entity Recognition (NER)
- 📊 Table extraction (with OCR fallback for scanned documents)
- 🧾 Downloading the extracted result as JSON

---

## 🛠️ Tech Stack

- 🖥️ Frontend: React (with drag-and-drop and JSON download)
- ⚙️ Backend: FastAPI + Tesseract OCR + pdfplumber + Transformers
- 🧠 NER Model: HuggingFace `bert-base-NER`

---

## 🚀 Features

- Upload PDF or image using drag & drop or file input
- Extracts:
  - 🧍 Named entities (PER, LOC, etc.)
  - 📋 Tables (from both scanned images and digital PDFs)
- 🔍 Shows extracted JSON in a structured view
- 💾 One-click JSON download

---

## 📦 Setup Instructions

### 🔧 Backend (FastAPI)

#### 1. Create virtual environment

```bash
python -m venv venv
# For Windows
venv\Scripts\activate
# For macOS/Linux
source venv/bin/activate

## 2. Install Python dependencies

pip install -r requirements.txt

### 3. Install system dependencies
✅ Tesseract OCR

Add to system PATH

Verify: tesseract --version

✅ Poppler for Windows

Set the POPPLER_PATH in file_processor.py

##4. Start the backend server

uvicorn app.main:app --reload

💻 Frontend (React)
## 1. Navigate and install dependencies

cd frontend
npm install


## 2. Start the React frontend
bash
Copy
Edit
npm start

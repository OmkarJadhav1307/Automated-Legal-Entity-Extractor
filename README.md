# 🔍 LexiScan Auto — Automated Legal Entity Extractor

> An end-to-end deep learning pipeline for extracting key legal entities (dates, parties, amounts, jurisdiction) from unstructured PDF contracts using OCR + Custom NER + Rule-Based Heuristics.

---

## 📌 What Does It Do?

LexiScan Auto is designed for law firms and fintech organizations that need to process thousands of PDF contracts daily. It replaces slow, error-prone manual extraction with a production-ready pipeline that:

- 📄 Reads scanned or digital PDF contracts via **Tesseract OCR**
- 🧠 Extracts key entities using a **custom-trained Spacy NER model** (Bi-LSTM based)
- 📐 Applies **rule-based heuristics** to standardize formats (ISO 8601 dates, currency cleanup) and validate logic (e.g., Expiration Date must be after Effective Date)
- 🌐 Serves results as **structured JSON** via a **FastAPI** REST endpoint

### Entities Extracted
| Entity | Example |
|---|---|
| `AGREEMENT_DATE` | March 15, 2027 → `2027-03-15` |
| `EFFECTIVE_DATE` | 04/01/2027 → `2027-04-01` |
| `EXPIRATION_DATE` | December 31, 2029 → `2029-12-31` |
| `PARTIES` | Nexus Cyber Solutions |
| `AMOUNT` | $1,500,000 |
| `GOVERNING_LAW` | State of California |

---

## 🏗 System Architecture

```
PDF / Image File
      │
      ▼
┌─────────────────────┐
│   OCR Engine        │  (Tesseract + pdf2image + OpenCV preprocessing)
└────────┬────────────┘
         │ raw text
         ▼
┌─────────────────────┐
│   NER Model         │  (Custom Spacy Bi-LSTM trained on legal contracts)
└────────┬────────────┘
         │ raw entities
         ▼
┌─────────────────────┐
│   Heuristics Engine │  (ISO 8601 dates, currency cleanup, logical validation)
└────────┬────────────┘
         │ clean JSON
         ▼
   FastAPI /extract endpoint
```

---

## 🚀 Quick Start — Docker (Recommended)

**Prerequisites:** [Docker Desktop](https://www.docker.com/products/docker-desktop) installed and running.

```bash
# 1. Clone the repository
git clone https://github.com/OmkarJadhav1307/Automated-Legal-Entity-Extractor.git
cd Automated-Legal-Entity-Extractor

# 2. Set up your environment file (REQUIRED)
copy .env.example .env       # Windows
cp .env.example .env         # Mac/Linux
# Then open .env and set GOOGLE_API_KEY if you plan to run annotation scripts

# 3. Build and start the server
docker-compose up --build -d
```

✅ The server is now live!

- **Swagger UI (Interactive):** http://localhost:5000/docs
- **Health Check:** http://localhost:5000/

To stop the server:
```bash
docker-compose down
```

---

## 💻 Manual Setup (Without Docker)

### Step 1 — Install System Dependencies

Install these tools **before** installing Python packages:

| Tool | Purpose | Download |
|---|---|---|
| **Tesseract OCR** | Core OCR engine | [Download](https://github.com/UB-Mannheim/tesseract/wiki) |
| **Poppler** | PDF-to-image converter | [Download (Windows)](http://blog.alivate.com.au/poppler-windows/) |

> ⚠️ After installing, update the paths in your `.env` file (see Step 2).

### Step 2 — Configure Environment

```bash
# Copy the example config
copy .env.example .env      # Windows
cp .env.example .env        # Mac/Linux
```

Open `.env` and set the correct paths for your system:
```env
TESSERACT_CMD_PATH="C:\Program Files\Tesseract-OCR\tesseract.exe"
POPPLER_PATH="C:\Program Files\poppler-24.08.0\Library\bin"
GOOGLE_API_KEY=your_gemini_api_key_here   # Only needed for annotation scripts
```

### Step 3 — Python Environment

```bash
# Create and activate virtual environment
python -m venv venv

venv\Scripts\activate         # Windows
source venv/bin/activate      # Mac/Linux

# Install Python dependencies
pip install -r requirements.txt

# Download Spacy base model
python -m spacy download en_core_web_sm
```

### Step 4 — Run the API Server

```bash
# Windows (PowerShell)
$env:PYTHONPATH="."
python src/main.py --server --port 5000

# Mac/Linux
PYTHONPATH="." python src/main.py --server --port 5000
```

Navigate to http://localhost:5000/docs to use the API.

---

## 🧪 Running Tests

```bash
# Windows
$env:PYTHONPATH="."; python -m pytest tests/ -v

# Mac/Linux
PYTHONPATH="." python -m pytest tests/ -v
```

Tests cover OCR text cleaning, heuristics validation (date standardization, logical rules), API health checks, and an end-to-end contract extraction test.

---

## 📁 Directory Structure

```
Automated-Legal-Entity-Extractor/
│
├── src/
│   ├── api/
│   │   ├── app.py                  # FastAPI app and /extract endpoint
│   │   └── services/
│   │       └── inference.py        # End-to-end inference pipeline (OCR → NER → Heuristics)
│   ├── ocr/
│   │   ├── engine.py               # Tesseract OCR wrapper for PDFs and images
│   │   ├── preprocess.py           # OpenCV image preprocessing (grayscale, thresholding)
│   │   └── cleaner.py              # Post-OCR text cleanup
│   ├── utils/
│   │   ├── heuristics.py           # Rule-based entity post-processing and validation
│   │   └── logger.py               # Centralized application logger
│   ├── annotate_contracts.py       # Automated annotation script (Gemini LLM + Doccano export)
│   └── main.py                     # CLI entrypoint (--server or --file modes)
│
├── tests/
│   ├── test_ocr.py                 # Unit tests for OCR text cleaner
│   ├── test_heuristics.py          # Unit tests for rule-based heuristics
│   ├── test_api.py                 # FastAPI endpoint tests (health check, validation)
│   └── test_e2e.py                 # End-to-end test: uploads a real PDF, validates JSON output
│
├── data/
│   ├── raw/synthetic_contracts/    # 360 synthetic legal PDF contracts for training
│   └── processed/                  # OCR-extracted text and Spacy training binary (.spacy)
│
├── models/
│   └── legalbert_lexiscan/         # Trained custom Spacy NER model (Bi-LSTM)
│       └── model-best/
│
├── Dockerfile                      # Docker build instructions (Python + Tesseract + Poppler)
├── docker-compose.yml              # Service orchestration for the API container
├── requirements.txt                # Python package dependencies
├── .env.example                    # Template for environment configuration
└── .gitignore
```

---

## 🔌 API Reference

### `POST /extract`

Upload a PDF or image file and receive extracted entities as structured JSON.

**Request:**
```bash
curl -X POST http://localhost:5000/extract \
  -F "file=@data/raw/synthetic_contracts/Contract_126.pdf"
```

**Response:**
```json
{
  "status": "success",
  "extracted_text": "SERVICE AGREEMENT\nThis Agreement is made on...",
  "entities": [
    {
      "label": "EFFECTIVE_DATE",
      "text": "April 1, 2027",
      "standardized_value": "2027-04-01",
      "start": 120,
      "end": 133
    },
    {
      "label": "AMOUNT",
      "text": "$1,500,000 USD",
      "standardized_value": "$1,500,000",
      "start": 210,
      "end": 224
    }
  ]
}
```

<div align="center">
  <h1>LexiScan Auto</h1>
  <p><strong>Automated Legal Entity Extractor</strong></p>
</div>

## 📌 Project Overview
**LexiScan Auto** is a sophisticated fintech/legal-tech pipeline designed to process high-volume unstructured PDF contracts. Built for law firms and fintech organizations, it replaces slow, manual entity extraction with a state-of-the-art Deep Learning Named Entity Recognition (NER) system.

The pipeline combines robust Optical Character Recognition (OCR), contextual NLP models, and rule-based heuristics to reliably extract:
*   Effective & Expiration Dates
*   Monetary Values / Amounts
*   Legal Jurisdictions / Governing Law
*   Contracting Parties

## 🏗 System Architecture
1.  **Ingestion & OCR:** Processes incoming PDFs or images using `Tesseract` and `pdf2image`.
2.  **NER Processing:** Applies a customized Spacy/TensorFlow Bi-LSTM model trained on legal terminology to extract raw entities.
3.  **Heuristics Engine:** Refines the raw NLP output by standardizing formats (e.g., ISO 8601 Dates) and enforcing logical rules (e.g., "Expiration must be after Effective Date").
4.  **API Delivery:** Returns structured JSON via a fully containerized `FastAPI` service.

---

## 🚀 Quick Start - Easy Installation (Docker)

The absolute easiest way to run the entire backend and OCR environment is using Docker. Ensure you have [Docker Desktop](https://www.docker.com/products/docker-desktop) running in the background.

```bash
# 1. Clone the repository
git clone https://github.com/OmkarJadhav1307/Automated-Legal-Entity-Extractor.git
cd Automated-Legal-Entity-Extractor

# 2. Build and start the container
docker-compose up --build -d
```
The server is now live! 
*   **Swagger API Docs:** Go to http://localhost:5000/docs in your browser to interactively upload a PDF contract and see the entity extraction.

To shut down the server later, simply run:
```bash
docker-compose down
```

---

## 💻 Manual Developer Setup (Without Docker)
If you wish to develop locally without Docker, you must install the system requirements strictly.

### 1. Install System Dependencies (Windows/Linux)
*   **Tesseract OCR:** Requires [Tesseract Engine](https://github.com/UB-Mannheim/tesseract/wiki) installed on your system.
*   **Poppler:** Requires [Poppler](http://blog.alivate.com.au/poppler-windows/) for PDF conversion. 

*Make sure both tools are added to your System `PATH`.*

### 2. Setup Python Environment
```bash
# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate       # On Linux/Mac
venv\Scripts\activate          # On Windows

# Install Python requirements
pip install -r requirements.txt

# Download Spacy static base model (Required)
python -m spacy download en_core_web_sm
```

### 3. Run the API Server
```bash
# Set your PYTHONPATH to the current directory
export PYTHONPATH="."          # On Linux/Mac
$env:PYTHONPATH="."            # On Windows (PowerShell)

# Start the local server
python src/main.py --server --port 5000
```

---

## 🧪 Running Tests
The project contains an automated test-suite using `pytest`, including testing the OCR cleaner heuristics, and End-to-End API endpoint testing:
```bash
python -m pytest tests/ -v
```

## 📁 Directory Structure
```text
LexiScan2/
├── data/                  # Contains raw synthetic contracts and processed AI doccano labels
├── models/                # Saved legal Spacy NLP models
├── src/                   
│   ├── api/               # FastAPI endpoints and Inference pipeline classes
│   ├── ocr/               # Tesseract Engine integrations and Image preprocessing
│   └── utils/             # Heuristics rules and Loggers
├── tests/                 # End-to-End validation scripts
├── Dockerfile             # Container configuration
└── docker-compose.yml     # Service manager
```

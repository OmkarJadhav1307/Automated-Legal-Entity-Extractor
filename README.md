# LexiScan2: Automated Legal Entity Extractor

LexiScan2 is an end-to-end automated platform for extracting custom legal entities from contracts. It seamlessly integrates Optical Character Recognition (OCR), document preprocessing, and a fine-tuned Named Entity Recognition (NER) model (LegalBERT) into a single FastAPI backend.

## Features
- **PDF & Image OCR:** Leverages Tesseract and Poppler to seamlessly extract text from images and PDF files of any length.
- **Robust Text Cleaning:** Implements regex-patterened parsing to normalize whitespace, handle broken lines, and remove OCR artifacts.
- **State-of-the-Art NLP:** Utilizes a fine-tuned LegalBERT NER model for precise entity resolution.
- **API & CLI Interfaces:** Use the FastAPI REST backend for easy integration, or test directly from the command line interface.

## Quickstart

### 1. Requirements
Ensure the following are installed:
- Python 3.10+
- Tesseract-OCR
- Poppler (for `pdf2image`)

Configure the tool paths inside your `.env` file!

### 2. Installation
```sh
# Clone directory & setup Python virtual env
python -m venv venv
.\venv\Scripts\Activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Usage

#### Run the API Server
Start the FastAPI endpoint locally:
```sh
python -m src.main --server
```
The application will listen on `http://127.0.0.1:5000`. Use the `/extract` endpoint to upload your PDF and receive a JSON of extracted entities.

#### Run the CLI Pipeline
Verify individual files using the simple orchestrator script:
```sh
python -m src.main --file "data/raw/synthetic_contracts.pdf"
```
The model will execute its complete pipeline (OCR -> Preprocessing -> Inference) and print the detected terms directly into your console.

## Project Structure
- `src/api/`: FastAPI endpoint server and inference pipelines.
- `src/models/`: Loading and testing scripts for PyTorch/Spacy models.
- `src/ocr/`: Deep PDF conversion, Tesseract settings, layout processors.
- `src/utils/`: Custom helpers including logging.
- `data/`: Raw unedited contracts and our fully structured export models. 
- `tests/`: End-to-end integration and functionality checks with PyTest.

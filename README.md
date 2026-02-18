#  LexiScan: Automated Legal Entity Extractor

**LexiScan** is a production-ready NLP pipeline designed to automate the extraction of critical legal entities (like Names, Dates, Clauses, and Jurisdictions) from unstructured PDF contracts.

Built for high-volume law firms, this system addresses the inefficiencies of manual review by combining OCR (Optical Character Recognition) and heuristic validation into a scalable solution.

---

## 🛠 Project Progress: Week 1 (OCR & Data Pipeline)

In the first phase, we successfully built the foundation of the pipeline:

- **OCR Engine**: Integrated `pytesseract` and `pdf2image` to convert scanned PDF documents into machine-readable text.
- **Preprocessing**: Implemented noise reduction and formatting to ensure high-quality text extraction.
- **Data Annotation**: Created a custom labeling workflow using `.jsonl` (JSON Lines) to prepare the ground-truth data for NLP training.
- **Project Structure**: Organized the codebase for scalability.

---

## 📂 Folder Structure

```text
LexiScan/
├── data/
│   ├── raw_pdfs/           # Original legal documents
│   ├── extracted_text.txt  # Clean text from OCR
│   └── annotations.jsonl   # Labeled data for NER training
├── ocr_engine.py           # Main logic for PDF processing
├── requirements.txt        # Project dependencies
├── .gitignore              # Prevents venv and junk files from being uploaded
└── README.md               # Project documentation
```
---

## 🚀 Tech Stack

-**Language**: Python 3.12+
-**OCR Engine**: Tesseract OCR
-**PDF Converter**: Poppler
-**Key Libraries**: pytesseract, pdf2image, json

---

## ⚙️ Setup & Installation
Clone the repo:

Bash
git clone [https://github.com/OmkarJadhav1307/Automated-Legal-Entity-Extractor.git](https://github.com/OmkarJadhav1307/Automated-Legal-Entity-Extractor.git)
cd LexiScan
Create Virtual Environment:

Bash
python -m venv venv
source venv/Scripts/activate  # For Windows
Install Dependencies:

Bash
pip install -r requirements.txt

---

## 📅 Roadmap
-**[✅] Week 1**: OCR Pipeline & Data Extraction.
-**[ ] Week 2**: Training a Custom Named Entity Recognition (NER) model using SpaCy/HuggingFace.
-**[ ] Week 3**: Heuristic Validation & Accuracy Benchmarking.
-**[ ] Week 4**: Deployment and API Integration.

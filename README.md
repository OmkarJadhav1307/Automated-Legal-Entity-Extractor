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

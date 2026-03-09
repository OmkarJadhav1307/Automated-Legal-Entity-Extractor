# LexiScan Auto - Implementation Plan & ML Pipeline

## 1. Project Objective
Build an Automated Legal Entity Extractor capable of taking raw legal contracts (PDFs) and extracting 6 key entities:
- `AGREEMENT_DATE`
- `EFFECTIVE_DATE`
- `EXPIRATION_DATE`
- `PARTIES`
- `GOVERNING_LAW`
- `AMOUNT`

## 2. Revised Architecture & ML Pipeline
Based on infrastructure constraints (No local GPU) and experimental best practices, the ML pipeline has been cleanly separated into local data preparation and cloud-based training.

### Stage 1: Data Generation & Annotation (Complete Local)
- **Source:** 500 Synthetic Legal Contracts.
- **Engine:** `src/annotate_contracts.py` using OCR (Tesseract) and Gemini (`flash-lite`, `gemma`) for zero-shot silver standard extraction.
- **Output:** `data/annotations/doccano_export.jsonl` (Validated locally via Doccano).

### Stage 2: Data Preprocessing (Immediate Next Step Local)
- **Script:** `src/data/format_data.py`. 
- **Goal:** Read the `doccano_export.jsonl` file, realign character offsets to exact Spacy/Token spans, and resolve overlaps.
- **Output Split:** Generates binary files ready for the neural networks. 
  - `train.spacy` (80% / 400 docs)
  - `dev.spacy` (20% / 100 docs)
- *Note:* This step remains completely local on the CPU as it is fast.

### Stage 3: Experimental Cloud Training (Google Colab)
Since the user does not have a local GPU, all heavy training will be performed in Google Colab (Free Tier GPU). We will test three distinct Model Architectures across two totally isolated Jupyter Notebooks to prevent Memory (OOM) crashes and Library conflicts.

**Notebook 1: Deep Learning Foundations**
Contains PyTorch implementations of classic deep neural network architectures:
1. **SpaCy CNN (Baseline):** Fast, Convolutional Neural Network. Tests if lightweight models can solve the problem.
2. **Bi-LSTM + CRF:** Bidirectional Long Short-Term Memory Network. Reads contract context forwards and backwards; excellent at handling extremely long legal phrases.

**Notebook 2: The Transformer State-of-the-Art**
Contains Heavy HuggingFace Transformer integrations:
3. **LegalBERT Fine-Tuning:** Leveraging `spacy-transformers` to fine-tune a massive pre-trained Legal model using only the 6 core LexiScan entities defined in `train.spacy`.

### Stage 4: Evaluation & Deployment
- Once models finish training in Colab, download the best performing `.spacy` model folder (determined by highest F1-Score on the `dev.spacy` dataset) back to the local `LexiScan2/models/` directory.
- Build lightweight API/Inference layer for standard use.

---

## Next Action Item
Create and execute `src/data/format_data.py` locally to convert the JSONL into `.spacy` objects for upload to Google Colab.

import os
import json
import glob
from tqdm import tqdm
import google.generativeai as genai
from dotenv import load_dotenv

from src.ocr.engine import OCREngine
from src.utils.logger import get_logger

# Ensure environment is loaded
load_dotenv()
logger = get_logger(__name__)

# --- CONFIGURATION ---
SOURCE_DIR = os.path.join("data", "raw", "synthetic_contracts")
PROCESSED_DIR = os.path.join("data", "processed", "synthetic_contracts")
OUTPUT_FILE = os.path.join("data", "processed", "doccano_import.jsonl")
ENTITIES = [
    "AGREEMENT_DATE",
    "EFFECTIVE_DATE",
    "EXPIRATION_DATE",
    "PARTIES",
    "GOVERNING_LAW",
    "AMOUNT"
]

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    logger.error("GOOGLE_API_KEY not found in environment. Please set it in your .env file.")
else:
    genai.configure(api_key=GOOGLE_API_KEY)

# Use a rotating list of models to maximize daily quota
MODEL_NAMES = [
    "models/gemini-flash-lite-latest",
    "models/gemini-3-flash-preview",
    "models/gemini-2.5-flash",
    "models/gemma-3-27b-it",
    "models/gemma-3-12b-it"
]

class ModelPool:
    def __init__(self, api_key):
        self.api_key = api_key
        self.models = []
        self.current_idx = 0
        for name in MODEL_NAMES:
            try:
                m = genai.GenerativeModel(name)
                self.models.append(m)
            except:
                continue
        logger.info(f"Initialized ModelPool with {len(self.models)} models.")

    def get_current_model(self):
        if not self.models:
            return None
        return self.models[self.current_idx]

    def rotate(self):
        self.current_idx = (self.current_idx + 1) % len(self.models)
        logger.info(f"Rotated to model: {self.models[self.current_idx].model_name}")
        return self.models[self.current_idx]

pool = None
if GOOGLE_API_KEY:
    pool = ModelPool(GOOGLE_API_KEY)

def get_llm_predictions(text):
    """
    Sends contract text to Gemini (using the pool) and returns entities.
    """
    prompt = f"""
    You are an expert legal annotator. Extract the following entities from the legal contract text provided:
    {", ".join(ENTITIES)}

    Return the result ONLY as a JSON object with a key "entities" containing a list of objects.
    Each object must have "text", "start_offset", "end_offset", and "label".
    The offsets MUST be character offsets within the provided text.
    Ensure the "text" exactly matches the substring in the provided text.

    Contract Text:
    {text[:8000]}
    """
    
    if not pool or not pool.get_current_model():
        logger.error("No Gemini models available. Skipping extraction.")
        return []

    max_retries = len(pool.models)
    for attempt in range(max_retries):
        model = pool.get_current_model()
        try:
            logger.info(f"Calling {model.model_name} (Length: {len(text)})...")
            response = model.generate_content(prompt)
            text_response = response.text
            
            if "```json" in text_response:
                text_response = text_response.split("```json")[1].split("```")[0].strip()
            elif "```" in text_response:
                text_response = text_response.split("```")[1].split("```")[0].strip()
                
            data = json.loads(text_response)
            entities = data.get("entities", [])

            # --- VALIDATION ---
            validated_entities = []
            for ent in entities:
                if ent['start_offset'] < 0 or ent['end_offset'] > len(text):
                    continue
                extracted_text = text[ent['start_offset']:ent['end_offset']]
                if extracted_text.strip().lower() == ent['text'].strip().lower():
                     validated_entities.append(ent)
                else:
                    start_idx = text.find(ent['text'])
                    if start_idx != -1:
                        ent['start_offset'] = start_idx
                        ent['end_offset'] = start_idx + len(ent['text'])
                        validated_entities.append(ent)
            return validated_entities

        except Exception as e:
            if "429" in str(e):
                logger.warning(f"Quota exceeded for {model.model_name}. Rotating...")
                pool.rotate()
                continue
            else:
                logger.error(f"Extraction failed for {model.model_name}: {e}")
                return []
    return []

def main():
    engine = OCREngine()
    pdf_files = glob.glob(os.path.join(SOURCE_DIR, "*.pdf"))
    
    if not pdf_files:
        logger.warning(f"No PDF files found in {SOURCE_DIR}")
        return

    # Check existing progress
    processed_files = set()
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    processed_files.add(entry["meta"]["source"])
                except:
                    continue
    
    logger.info(f"Resuming: {len(processed_files)} already processed. {len(pdf_files) - len(processed_files)} remaining.")
    
    if not os.path.exists(PROCESSED_DIR):
        os.makedirs(PROCESSED_DIR)

    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        for pdf_path in tqdm(pdf_files):
            base_name = os.path.basename(pdf_path)
            if base_name in processed_files:
                continue

            try:
                txt_name = os.path.splitext(base_name)[0] + ".txt"
                txt_path = os.path.join(PROCESSED_DIR, txt_name)

                # 1. OCR (if text file exists, skip OCR and load)
                if os.path.exists(txt_path):
                    with open(txt_path, "r", encoding="utf-8") as tf:
                        text = tf.read()
                else:
                    text = engine.process_pdf(pdf_path)
                    with open(txt_path, "w", encoding="utf-8") as tf:
                        tf.write(text)
                
                # 2. LLM Labeling
                labels = get_llm_predictions(text)
                
                # 3. Format for Doccano
                doccano_entry = {
                    "text": text,
                    "label": [[l['start_offset'], l['end_offset'], l['label']] for l in labels],
                    "meta": {"source": base_name}
                }
                
                f.write(json.dumps(doccano_entry) + "\n")
                f.flush()
                
                # Small delay to keep RPM low
                import time
                time.sleep(3) 

            except Exception as e:
                logger.error(f"Failed to process {pdf_path}: {e}")

if __name__ == "__main__":
    main()

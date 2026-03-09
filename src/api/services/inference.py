import os
import spacy
from typing import Dict, Any, List
from src.utils.logger import get_logger
from src.utils.heuristics import apply_heuristics
from src.ocr.engine import OCREngine

logger = get_logger(__name__)

# Path to our chosen Bi-LSTM NER model from Colab
MODEL_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "models", "legalbert_lexiscan", "model-best"))

class InferencePipeline:
    def __init__(self):
        logger.info("Initializing Inference Pipeline...")
        self.ocr_engine = OCREngine()
        self.nlp = None
        self.load_model()
    
    def load_model(self):
        try:
            logger.info(f"Loading NER model from {MODEL_PATH}")
            if os.path.exists(MODEL_PATH):
                self.nlp = spacy.load(MODEL_PATH)
                logger.info("Model loaded successfully.")
            else:
                logger.error(f"Model path does not exist: {MODEL_PATH}")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
    
    def process_file(self, file_path: str, is_pdf: bool = True) -> Dict[str, Any]:
        """
        Runs OCR on the file and then extracts entities.
        """
        logger.info(f"Starting inference on {file_path}")
        try:
            # 1. OCR Extraction
            if is_pdf:
                text = self.ocr_engine.process_pdf(file_path)
            else:
                text = self.ocr_engine.process_image(file_path)
            
            logger.info(f"OCR extracted {len(text)} characters.")
            
            # 2. NER Extraction
            raw_entities = self.extract_entities(text)
            
            # 3. Rule-Based Heuristics (ISO 8601 Dates, Money formats, Logic)
            entities = apply_heuristics(raw_entities)
            
            return {
                "status": "success",
                "extracted_text": text,
                "entities": entities
            }
        except Exception as e:
            logger.error(f"Inference failed: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }
            
    def extract_entities(self, text: str) -> List[Dict[str, str]]:
        if not self.nlp:
            logger.warning("NER model not loaded. Skipping entity extraction.")
            return []
            
        try:
            doc = self.nlp(text)
            entities = []
            for ent in doc.ents:
                entities.append({
                    "label": ent.label_,
                    "text": ent.text.strip(),
                    "start": ent.start_char,
                    "end": ent.end_char
                })
        except Exception as e:
            logger.error(f"NER Extraction crashed (likely missing vectors): {str(e)}")
            entities = []
            
        return entities

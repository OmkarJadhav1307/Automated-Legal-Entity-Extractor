from datetime import datetime
from dateutil import parser
from typing import List, Dict, Any
import re

from src.utils.logger import get_logger

logger = get_logger(__name__)

def standardize_date(date_text: str) -> str:
    """
    Attempts to parse a natural language or messy date string
    into an ISO 8601 formatted date (YYYY-MM-DD).
    Returns the original string if parsing fails.
    """
    try:
        # dateutil.parser is very robust against messy text (e.g. "15th of March, 2027")
        parsed_date = parser.parse(date_text, fuzzy=True)
        return parsed_date.strftime("%Y-%m-%d")
    except Exception as e:
        logger.debug(f"Could not parse date '{date_text}': {e}")
        return date_text

def clean_amount(amount_text: str) -> str:
    """
    Strips away alphabetic characters that might have been accidentally 
    included by OCR next to a currency value.
    Example: 'Value is $1,500,000 USD' -> '$1,500,000'
    """
    # Look for anything resembling a currency and numbers
    match = re.search(r"[$€£¥]\s*[\d,]+(?:\.\d{2})?", amount_text)
    if match:
        return match.group(0)
    return amount_text.strip()

def apply_heuristics(entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Takes the raw entities extracted by the ML model (Bi-LSTM) and 
    cleans them using rule-based heuristics to ensure high precision.
    """
    processed_entities = []
    
    dates_extracted = {}
    
    for ent in entities:
        label = ent["label"]
        text = ent["text"]
        confidence = ent.get("confidence", 1.0) # Assume confidence if available 
        
        # 1. Date Standardization
        if label in ["AGREEMENT_DATE", "EFFECTIVE_DATE", "EXPIRATION_DATE"]:
            iso_date = standardize_date(text)
            
            # Store them to check logical sequence later
            if iso_date != text: 
                dates_extracted[label] = iso_date
                
            processed_entities.append({
                "label": label,
                "text": text,
                "standardized_value": iso_date,
                "start": ent.get("start"),
                "end": ent.get("end")
            })
            
        # 2. Money Standardization
        elif label == "AMOUNT":
            clean_amt = clean_amount(text)
            processed_entities.append({
                "label": label,
                "text": text,
                "standardized_value": clean_amt,
                "start": ent.get("start"),
                "end": ent.get("end")
            })
            
        # 3. Text Pass-through (Parties, Governing Law)
        else:
            processed_entities.append({
                "label": label,
                "text": text,
                "standardized_value": text.strip(".,;: \n\t"),
                "start": ent.get("start"),
                "end": ent.get("end")
            })
            
    # 4. Logical Sequence Validation (e.g., Expiration > Effective)
    effective = dates_extracted.get("EFFECTIVE_DATE") or dates_extracted.get("AGREEMENT_DATE")
    expiration = dates_extracted.get("EXPIRATION_DATE")
    
    if effective and expiration:
        try:
            eff_dt = datetime.strptime(effective, "%Y-%m-%d")
            exp_dt = datetime.strptime(expiration, "%Y-%m-%d")
            if exp_dt <= eff_dt:
                logger.warning(f"Heuristic Flag: EXPIRATION_DATE ({expiration}) "
                               f"is not after EFFECTIVE_DATE ({effective}). Possible OCR/NER error.")
                # We append a systemic flag without breaking the JSON dictionary
                for e in processed_entities:
                    if e["label"] == "EXPIRATION_DATE":
                        e["heuristic_warning"] = "Expiration date precedes or equals effective date."
        except Exception as e:
            logger.debug(f"Failed to run sequence validation on parsed dates: {e}")

    return processed_entities

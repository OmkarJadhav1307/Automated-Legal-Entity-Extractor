import re
import unicodedata

def clean_ocr_text(text: str) -> str:
    """
    Cleans raw OCR text by standardizing whitespace, removing common artifacts,
    and normalizing unicode.
    """
    if not text:
        return ""

    # Normalize unicode (e.g., smart quotes to straight quotes, ligatures to separate letters)
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')

    # Replace multiple spaces with a single space
    text = re.sub(r'[ \t]+', ' ', text)

    # Standardize line breaks (remove multiple empty lines)
    text = re.sub(r'\n\s*\n', '\n\n', text)

    # Remove common OCR artifacts (e.g., random isolated symbols at the start of a line)
    text = re.sub(r'^[^\w\s]\s*', '', text, flags=re.MULTILINE)

    return text.strip()

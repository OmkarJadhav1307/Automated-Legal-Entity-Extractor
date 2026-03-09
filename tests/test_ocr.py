import pytest
from src.ocr.cleaner import clean_ocr_text

def test_clean_ocr_text():
    raw_text = "This   is\n\n\na test\ntext."
    cleaned = clean_ocr_text(raw_text)
    
    # Should standardize new lines and excessive spaces
    assert "This is" in cleaned
    assert "a test" in cleaned
    assert "\n\n\n" not in cleaned # Two newlines should be reduced to one

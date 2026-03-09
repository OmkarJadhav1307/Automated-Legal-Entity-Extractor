import pytest
from src.utils.heuristics import standardize_date, clean_amount, apply_heuristics

class TestHeuristics:
    
    # --- 1. Edge Cases: Noisy/Garbage Dates ---
    def test_standardize_date_clean(self):
        """Test perfect date formatting."""
        assert standardize_date("March 15, 2027") == "2027-03-15"
        assert standardize_date("04/01/2027") == "2027-04-01"

    def test_standardize_date_noisy_ocr(self):
        """Test fuzzy parsing of noisy OCR text."""
        # Dateutil's fuzzy parser should extract the date from the surrounding noise
        assert standardize_date("The date is 15th of March 2027") == "2027-03-15"
        
    def test_standardize_date_complete_garbage(self):
        """Test fallback when given unparseable text."""
        # Should fail parsing gracefully and just return the raw string
        assert standardize_date("NOT_A_DATE_AT_ALL") == "NOT_A_DATE_AT_ALL"


    # --- 2. Edge Cases: OCR Merging Money with Text ---
    def test_clean_amount_standard(self):
        """Test clean currency values."""
        assert clean_amount("$1,500,000") == "$1,500,000"
        assert clean_amount("€500.00") == "€500.00"

    def test_clean_amount_merged_text(self):
        """Test extraction when OCR fails to add spaces."""
        assert clean_amount("$1,500,000USD") == "$1,500,000"
        assert clean_amount("payable amount is $25,000.50xyz") == "$25,000.50"

    def test_clean_amount_no_currency(self):
        """Test fallback when no currency symbol is found."""
        assert clean_amount("One Million Dollars") == "One Million Dollars"

    # --- 3. Edge Cases: Illogical Model Predictions (Time Travel) ---
    def test_apply_heuristics_logical_dates(self):
        """Test that correct dates pass through without warnings."""
        entities = [
            {"label": "EFFECTIVE_DATE", "text": "January 1, 2027"},
            {"label": "EXPIRATION_DATE", "text": "December 31, 2029"}
        ]
        
        result = apply_heuristics(entities)
        
        assert len(result) == 2
        assert result[0]["standardized_value"] == "2027-01-01"
        assert result[1]["standardized_value"] == "2029-12-31"
        assert "heuristic_warning" not in result[1]

    def test_apply_heuristics_illogical_dates(self):
        """Test the safety net when Expiration happens BEFORE Effective Date."""
        entities = [
            {"label": "EFFECTIVE_DATE", "text": "January 1, 2027"},
            {"label": "EXPIRATION_DATE", "text": "January 1, 1999"} # Hallucinated 1999 Date
        ]
        
        result = apply_heuristics(entities)
        
        assert len(result) == 2
        # Verify the dates were still extracted and formatted...
        assert result[0]["standardized_value"] == "2027-01-01"
        assert result[1]["standardized_value"] == "1999-01-01"
        
        # ... BUT verify the warning flag was injected for human review
        assert "heuristic_warning" in result[1]
        assert "precedes" in result[1]["heuristic_warning"]

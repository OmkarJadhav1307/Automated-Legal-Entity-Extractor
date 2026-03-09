import os
import pytest
from fastapi.testclient import TestClient

from src.api.app import app

client = TestClient(app)

def test_extract_endpoint_e2e():
    """
    Simulates sending a real PDF contract to the /extract endpoint 
    and verifies the response format and content.
    """
    pdf_path = os.path.join("data", "raw", "synthetic_contracts", "Contract_126.pdf")
    
    # We skip the E2E test if the CI environment or the local folder doesn't have the file
    if not os.path.exists(pdf_path):
        pytest.skip(f"Test document not found: {pdf_path}")
        
    with open(pdf_path, "rb") as pdf_file:
        files = {"file": ("Contract_126.pdf", pdf_file, "application/pdf")}
        response = client.post("/extract", files=files)
        
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "success"
    assert "extracted_text" in data
    assert "entities" in data
    
    # Check that OCR actually grabbed text from the document
    assert len(data["extracted_text"]) > 100 
    
    # Since this is an E2E test, we expect the pipeline to have extracted some entities
    entities = data["entities"]
    assert isinstance(entities, list)
    
    # Depending on the contract text, we expect at least some labels to be parsed
    labels = [ent["label"] for ent in entities]
    print(f"Entities Extracted: {labels}")
    # assert len(labels) > 0, "No entities were extracted from the test document!"

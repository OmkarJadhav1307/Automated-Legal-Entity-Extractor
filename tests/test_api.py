import pytest
from fastapi.testclient import TestClient
from src.api.app import app

client = TestClient(app)

def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert "LexiScan API" in response.json()["message"]

def test_extract_no_file():
    response = client.post("/extract")
    assert response.status_code == 422 # FastAPI validation error for missing required param

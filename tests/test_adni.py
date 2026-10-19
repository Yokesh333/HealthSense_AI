from fastapi.testclient import TestClient
from backend.main import app
import pytest

client = TestClient(app)

valid_payload = {
    "AGE": 72,
    "EDUCATION": 16,
    "ADAS": 12.0,
    "CDR": 0.5,
    "FAQ": 5.0,
    "MMSE": 25.0,
    "MOCA": 21.0,
    "SEX": "Male",
    "RACE": "White",
    "ETHNICITY": "Not Hispanic or Latino"
}

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_predict_valid_complete():
    # Lifespan events are handled correctly by TestClient in recent FastAPI versions,
    # but we need to use it in a context manager to trigger lifespan events.
    with TestClient(app) as client:
        response = client.post("/api/adni/predict", json=valid_payload)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "prediction" in data
        assert data["prediction"] in ["CN", "MCI", "AD"]
        
        assert "probabilities" in data
        probs = data["probabilities"]
        assert "CN" in probs
        assert "MCI" in probs
        assert "AD" in probs
        
        # Check sum approx 1
        sum_probs = sum(probs.values())
        assert abs(sum_probs - 1.0) < 0.01
        
        assert "clinical_notice" in data

def test_predict_missing_moca():
    payload = valid_payload.copy()
    payload["MOCA"] = None
    
    with TestClient(app) as client:
        response = client.post("/api/adni/predict", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["prediction"] in ["CN", "MCI", "AD"]

def test_predict_missing_required_fields():
    payload = valid_payload.copy()
    del payload["AGE"]
    
    with TestClient(app) as client:
        response = client.post("/api/adni/predict", json=payload)
        assert response.status_code == 422

def test_predict_invalid_data_type():
    payload = valid_payload.copy()
    payload["AGE"] = "invalid_string"
    
    with TestClient(app) as client:
        response = client.post("/api/adni/predict", json=payload)
        assert response.status_code == 422

"""Quick test: does PDF extraction actually work right now?"""
import json
from fastapi.testclient import TestClient
from backend.main import app

with TestClient(app) as client:
    # Test with Parkinson PDF
    pdf_path = "tests/fixtures/synthetic_parkinson_clinical_report.pdf"
    with open(pdf_path, "rb") as f:
        response = client.post(
            "/api/reports/extract",
            files={"file": ("test.pdf", f, "application/pdf")}
        )
    
    print("STATUS:", response.status_code)
    data = response.json()
    print("\ndisease_context:", data.get("disease_context"))
    pi = data.get("patient_information", {})
    print("age:", pi.get("age"))
    print("sex:", pi.get("sex"))
    print("education:", pi.get("education"))
    cs = data.get("clinical_scores", {})
    print("moca:", cs.get("moca"))
    print("updrs:", cs.get("updrs"))
    print("hoehn_yahr:", cs.get("hoehn_yahr"))
    print("symptoms:", data.get("symptoms"))
    print("clinical_impression:", data.get("clinical_impression"))
    
    if data.get("disease_context") == ["unknown"] or not pi.get("age"):
        print("\n*** EXTRACTION FAILED — returning empty/fallback profile ***")
    else:
        print("\n*** EXTRACTION WORKING CORRECTLY ***")

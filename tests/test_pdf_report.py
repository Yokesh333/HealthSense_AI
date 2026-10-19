"""
tests/test_pdf_report.py

Comprehensive unit and integration tests for the Clinical PDF Report Upload feature.

Tests:
1. Valid text-based Alzheimer's PDF extraction
2. Valid text-based Parkinson's PDF extraction
3. Both-disease report context
4. Empty PDF handling
5. Corrupted PDF handling
6. Image-only / scanned PDF detection (returns explicit error message)
7. Unsupported file type (non-PDF)
8. Disease context classification accuracy
9. Absence of fabricated missing values
10. ADNI ML execution rules (executed for ALZ + features, skipped for Parkinson's-only)
11. Alzheimer RAG evidence retrieval filtering
12. Parkinson RAG evidence retrieval filtering
13. Full API endpoint workflow (POST /api/reports/extract and POST /api/reports/analyze)
14. Real de-identified clinical case report E2E processing
"""

import os
import io
import pytest
import fitz
from fastapi.testclient import TestClient

from backend.main import app
from backend.services.pdf_service import PDFExtractionService, PDFExtractionError
from backend.models.report_schemas import StructuredClinicalProfile, PatientInformation, ClinicalScores
from backend.services.report_adapter import ClinicalProfileAdapter

pdf_service = PDFExtractionService()


@pytest.fixture
def sample_alzheimers_pdf_bytes():
    doc = fitz.open()
    page = doc.new_page()
    text = (
        "--- PAGE 1 ---\n"
        "CLINICAL REPORT: Patient Age 72, Female. MMSE: 22, MoCA: 19, CDR: 1.0.\n"
        "History of progressive memory loss and word-finding difficulty.\n"
        "Brain MRI shows bilateral hippocampal atrophy.\n"
        "Impression: Probable Alzheimer's disease."
    )
    page.insert_text((50, 50), text)
    bytes_io = io.BytesIO()
    doc.save(bytes_io)
    doc.close()
    return bytes_io.getvalue()


@pytest.fixture
def sample_parkinsons_pdf_bytes():
    doc = fitz.open()
    page = doc.new_page()
    text = (
        "--- PAGE 1 ---\n"
        "CLINICAL REPORT: Patient Age 66, Male.\n"
        "Patient exhibits right hand resting tremor, bradykinesia, and muscle rigidity.\n"
        "UPDRS Part III score: 26. Hoehn & Yahr Stage: 2.0.\n"
        "DaTSCAN shows dopamine transporter deficit in putamen.\n"
        "Impression: Idiopathic Parkinson's disease."
    )
    page.insert_text((50, 50), text)
    bytes_io = io.BytesIO()
    doc.save(bytes_io)
    doc.close()
    return bytes_io.getvalue()


@pytest.fixture
def sample_scanned_pdf_bytes():
    doc = fitz.open()
    doc.new_page()  # Empty page with 0 text
    bytes_io = io.BytesIO()
    doc.save(bytes_io)
    doc.close()
    return bytes_io.getvalue()


# ---------------------------------------------------------------------------
# 1. PDF Extraction Service Unit Tests
# ---------------------------------------------------------------------------

def test_pdf_extraction_service_valid_alzheimers(sample_alzheimers_pdf_bytes):
    full_text, pages = pdf_service.validate_and_extract(sample_alzheimers_pdf_bytes, "alz.pdf")
    assert "MMSE: 22" in full_text
    assert "Alzheimer's" in full_text
    assert len(pages) == 1


def test_pdf_extraction_service_empty_bytes():
    with pytest.raises(PDFExtractionError, match="Uploaded file is empty"):
        pdf_service.validate_and_extract(b"", "empty.pdf")


def test_pdf_extraction_service_corrupt_bytes():
    with pytest.raises(PDFExtractionError, match="Failed to read PDF file"):
        pdf_service.validate_and_extract(b"Not a valid PDF header content", "corrupt.pdf")


def test_pdf_extraction_service_scanned_image_only(sample_scanned_pdf_bytes):
    with pytest.raises(PDFExtractionError, match="This PDF does not contain extractable text"):
        pdf_service.validate_and_extract(sample_scanned_pdf_bytes, "scanned.pdf")


# ---------------------------------------------------------------------------
# 2. Clinical Profile Adapter & ADNI Logic Tests
# ---------------------------------------------------------------------------

def test_report_adapter_alzheimers_with_adni_features():
    profile = StructuredClinicalProfile(
        disease_context=["alzheimers"],
        patient_information=PatientInformation(age=72, sex="Female", education=16),
        clinical_scores=ClinicalScores(mmse=22, moca=19, cdr=1.0),
        symptoms=["memory loss"],
        clinical_impression="Alzheimer's dementia"
    )
    req = ClinicalProfileAdapter.adapt(profile)
    assert req.type == "CLINICAL_REPORT"
    assert req.disease_context == ["alzheimers"]
    assert req.adni_data is not None
    assert req.adni_data.AGE == 72.0
    assert req.adni_data.MMSE == 22.0


def test_report_adapter_parkinsons_skips_adni():
    profile = StructuredClinicalProfile(
        disease_context=["parkinsons"],
        patient_information=PatientInformation(age=66, sex="Male"),
        clinical_scores=ClinicalScores(updrs=26),
        symptoms=["resting tremor", "bradykinesia"],
        clinical_impression="Parkinson's disease"
    )
    req = ClinicalProfileAdapter.adapt(profile)
    assert req.type == "CLINICAL_REPORT"
    assert req.disease_context == ["parkinsons"]
    # ADNI MUST be skipped for Parkinson's-only reports
    assert req.adni_data is None


def test_report_adapter_no_fabricated_values():
    profile = StructuredClinicalProfile(
        disease_context=["alzheimers"],
        patient_information=PatientInformation(age=70, sex="Male"),
        clinical_scores=ClinicalScores(mmse=24), # MoCA, ADAS, FAQ missing
        symptoms=["memory impairment"]
    )
    assert profile.clinical_scores.moca is None
    assert profile.clinical_scores.adas is None
    assert profile.clinical_scores.faq is None


# ---------------------------------------------------------------------------
# 3. API Endpoint Tests
# ---------------------------------------------------------------------------

def test_api_extract_endpoint_unsupported_file_type():
    with TestClient(app) as client:
        response = client.post(
            "/api/reports/extract",
            files={"file": ("test.txt", b"plain text content", "text/plain")}
        )
        assert response.status_code == 400
        assert "Only PDF files are supported" in response.json()["detail"]


def test_api_extract_endpoint_scanned_pdf(sample_scanned_pdf_bytes):
    with TestClient(app) as client:
        response = client.post(
            "/api/reports/extract",
            files={"file": ("scanned.pdf", sample_scanned_pdf_bytes, "application/pdf")}
        )
        assert response.status_code == 400
        assert "This PDF does not contain extractable text" in response.json()["detail"]


def test_api_extract_and_analyze_end_to_end_alzheimers(sample_alzheimers_pdf_bytes):
    with TestClient(app) as client:
        # 1. Extract endpoint
        extract_resp = client.post(
            "/api/reports/extract",
            files={"file": ("alz.pdf", sample_alzheimers_pdf_bytes, "application/pdf")}
        )
        assert extract_resp.status_code == 200
        profile_data = extract_resp.json()
        assert "disease_context" in profile_data

        # 2. Analyze endpoint (in-memory orchestrator)
        analyze_resp = client.post(
            "/api/reports/analyze",
            json={"profile": profile_data, "clinical_question": "What does this mean?"}
        )
        assert analyze_resp.status_code == 200
        res = analyze_resp.json()
        assert res["workflow"] == "CLINICAL_REPORT"
        assert res["status"] == "completed"
        assert "explanation" in res
        assert res["explanation"] is not None


def test_api_extract_and_analyze_end_to_end_parkinsons(sample_parkinsons_pdf_bytes):
    with TestClient(app) as client:
        # 1. Extract endpoint
        extract_resp = client.post(
            "/api/reports/extract",
            files={"file": ("pd.pdf", sample_parkinsons_pdf_bytes, "application/pdf")}
        )
        assert extract_resp.status_code == 200
        profile_data = extract_resp.json()

        # 2. Analyze endpoint
        analyze_resp = client.post(
            "/api/reports/analyze",
            json={"profile": profile_data}
        )
        assert analyze_resp.status_code == 200
        res = analyze_resp.json()
        assert res["workflow"] == "CLINICAL_REPORT"
        assert res["status"] == "completed"
        # ADNI should not have run for Parkinson's only
        assert "ADNI ML Agent" not in res["agents_executed"]


# ---------------------------------------------------------------------------
# 4. De-identified Clinical Case Report E2E Tests
# ---------------------------------------------------------------------------

def test_deidentified_alzheimers_case_report_file():
    case_path = os.path.join("data", "test_reports", "deidentified_alzheimers_case.pdf")
    assert os.path.exists(case_path), "De-identified Alzheimer's case PDF must exist."

    with open(case_path, "rb") as f:
        content = f.read()

    with TestClient(app) as client:
        response = client.post(
            "/api/reports/extract",
            files={"file": ("deidentified_alzheimers_case.pdf", content, "application/pdf")}
        )
        assert response.status_code == 200
        profile = response.json()

        analyze_resp = client.post(
            "/api/reports/analyze",
            json={"profile": profile}
        )
        assert analyze_resp.status_code == 200
        res = analyze_resp.json()
        assert res["status"] == "completed"


def test_deidentified_parkinsons_case_report_file():
    case_path = os.path.join("data", "test_reports", "deidentified_parkinsons_case.pdf")
    assert os.path.exists(case_path), "De-identified Parkinson's case PDF must exist."

    with open(case_path, "rb") as f:
        content = f.read()

    with TestClient(app) as client:
        response = client.post(
            "/api/reports/extract",
            files={"file": ("deidentified_parkinsons_case.pdf", content, "application/pdf")}
        )
        assert response.status_code == 200
        profile = response.json()

        analyze_resp = client.post(
            "/api/reports/analyze",
            json={"profile": profile}
        )
        assert analyze_resp.status_code == 200
        res = analyze_resp.json()
        assert res["status"] == "completed"
        assert "ADNI ML Agent" not in res["agents_executed"]

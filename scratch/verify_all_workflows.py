"""
Comprehensive verification script testing all 9 workflow scenarios:
1. Alzheimer questionnaire workflow
2. Parkinson questionnaire workflow
3. Both questionnaire workflow
4. Alzheimer PDF workflow
5. Parkinson PDF workflow
6. Invalid PDF workflow
7. Scanned/image-only PDF workflow
8. Missing clinical values PDF workflow
9. Unknown disease context PDF workflow
"""

import os
import io
import fitz
from fastapi.testclient import TestClient
from backend.main import app

def run_verifications():
    print("\n==================================================")
    print("HEALTHSENSE AI — END-TO-END WORKFLOW VERIFICATION")
    print("==================================================\n")

    with TestClient(app) as client:

        # ----------------------------------------------------
        # TEST 1: Alzheimer Questionnaire Workflow
        # ----------------------------------------------------
        q_alz = client.get("/api/questionnaire/alzheimers").json()
        alz_answers = [{"question_id": q["id"], "answer": "Often"} for q in q_alz["questions"]]
        resp1 = client.post("/api/agents/analyze", json={
            "type": "QUESTIONNAIRE",
            "questionnaire_data": {
                "questionnaire_id": q_alz["questionnaire_id"],
                "version": q_alz["version"],
                "responses": alz_answers
            }
        })
        d1 = resp1.json()
        print(f"TEST 1 [Alzheimer Questionnaire]: Status HTTP {resp1.status_code} | Workflow={d1.get('workflow')} | Context={d1.get('disease_context')} | AgentsExecuted={d1.get('agents_executed')}")
        assert resp1.status_code == 200 and d1["status"] == "completed"

        # ----------------------------------------------------
        # TEST 2: Parkinson Questionnaire Workflow
        # ----------------------------------------------------
        q_pd = client.get("/api/questionnaire/parkinsons").json()
        pd_answers = [{"question_id": q["id"], "answer": "Sometimes"} for q in q_pd["questions"]]
        resp2 = client.post("/api/agents/analyze", json={
            "type": "QUESTIONNAIRE",
            "questionnaire_data": {
                "questionnaire_id": q_pd["questionnaire_id"],
                "version": q_pd["version"],
                "responses": pd_answers
            }
        })
        d2 = resp2.json()
        print(f"TEST 2 [Parkinson Questionnaire]: Status HTTP {resp2.status_code} | Workflow={d2.get('workflow')} | Context={d2.get('disease_context')} | AgentsExecuted={d2.get('agents_executed')}")
        assert resp2.status_code == 200 and d2["status"] == "completed"

        # ----------------------------------------------------
        # TEST 3: Both Questionnaire Workflow
        # ----------------------------------------------------
        q_both = client.get("/api/questionnaire/both").json()
        both_answers = (
            [{"question_id": q["id"], "answer": "Often"} for q in q_both["alzheimers_questions"]] +
            [{"question_id": q["id"], "answer": "Sometimes"} for q in q_both["parkinsons_questions"]]
        )
        resp3 = client.post("/api/agents/analyze", json={
            "type": "QUESTIONNAIRE",
            "questionnaire_data": {
                "questionnaire_id": q_both["questionnaire_id"],
                "version": q_both["version"],
                "responses": both_answers
            }
        })
        d3 = resp3.json()
        print(f"TEST 3 [Both Questionnaire]:      Status HTTP {resp3.status_code} | Workflow={d3.get('workflow')} | Context={d3.get('disease_context')} | AgentsExecuted={d3.get('agents_executed')}")
        assert resp3.status_code == 200 and d3["status"] == "completed"

        # ----------------------------------------------------
        # TEST 4: Alzheimer PDF Report Workflow
        # ----------------------------------------------------
        alz_pdf_path = os.path.join("data", "test_reports", "deidentified_alzheimers_case.pdf")
        with open(alz_pdf_path, "rb") as f:
            ext_alz = client.post("/api/reports/extract", files={"file": ("alz.pdf", f.read(), "application/pdf")})
        prof_alz = ext_alz.json()
        ana_alz = client.post("/api/reports/analyze", json={"profile": prof_alz})
        d4 = ana_alz.json()
        print(f"TEST 4 [Alzheimer PDF Report]:    Status HTTP {ana_alz.status_code} | Context={prof_alz.get('disease_context')} | ADNI Ran={'ADNI ML Agent' in d4.get('agents_executed', [])} | Status={d4.get('status')}")
        assert ana_alz.status_code == 200 and d4["status"] == "completed" and "alzheimers" in d4["disease_context"]

        # ----------------------------------------------------
        # TEST 5: Parkinson PDF Report Workflow
        # ----------------------------------------------------
        pd_pdf_path = os.path.join("data", "test_reports", "deidentified_parkinsons_case.pdf")
        with open(pd_pdf_path, "rb") as f:
            ext_pd = client.post("/api/reports/extract", files={"file": ("pd.pdf", f.read(), "application/pdf")})
        prof_pd = ext_pd.json()
        ana_pd = client.post("/api/reports/analyze", json={"profile": prof_pd})
        d5 = ana_pd.json()
        print(f"TEST 5 [Parkinson PDF Report]:    Status HTTP {ana_pd.status_code} | Context={prof_pd.get('disease_context')} | ADNI Skipped={'ADNI ML Agent' not in d5.get('agents_executed', [])} | Status={d5.get('status')}")
        assert ana_pd.status_code == 200 and d5["status"] == "completed" and "ADNI ML Agent" not in d5["agents_executed"]

        # ----------------------------------------------------
        # TEST 6: Invalid PDF File
        # ----------------------------------------------------
        resp6 = client.post("/api/reports/extract", files={"file": ("invalid.txt", b"plain text", "text/plain")})
        print(f"TEST 6 [Invalid PDF File]:        Status HTTP {resp6.status_code} | ErrorDetail='{resp6.json().get('detail')}'")
        assert resp6.status_code == 400

        # ----------------------------------------------------
        # TEST 7: Scanned / Image-Only PDF File
        # ----------------------------------------------------
        doc_scanned = fitz.open()
        doc_scanned.new_page()
        bytes_scanned = doc_scanned.tobytes()
        doc_scanned.close()
        resp7 = client.post("/api/reports/extract", files={"file": ("scanned.pdf", bytes_scanned, "application/pdf")})
        print(f"TEST 7 [Scanned PDF File]:        Status HTTP {resp7.status_code} | ErrorDetail='{resp7.json().get('detail')}'")
        assert resp7.status_code == 400 and "does not contain extractable text" in resp7.json()["detail"]

        # ----------------------------------------------------
        # TEST 8: Missing Clinical Values PDF
        # ----------------------------------------------------
        doc_missing = fitz.open()
        p_miss = doc_missing.new_page()
        p_miss.insert_text((50, 50), "--- PAGE 1 ---\nPatient reports memory lapses. No objective scores performed.")
        bytes_miss = doc_missing.tobytes()
        doc_missing.close()
        ext_miss = client.post("/api/reports/extract", files={"file": ("missing.pdf", bytes_miss, "application/pdf")})
        prof_miss = ext_miss.json()
        ana_miss = client.post("/api/reports/analyze", json={"profile": prof_miss})
        d8 = ana_miss.json()
        print(f"TEST 8 [Missing Values PDF]:      Status HTTP {ana_miss.status_code} | MoCA={prof_miss.get('clinical_scores', {}).get('moca')} | MMSE={prof_miss.get('clinical_scores', {}).get('mmse')} | Status={d8.get('status')}")
        assert prof_miss.get("clinical_scores", {}).get("moca") is None and prof_miss.get("clinical_scores", {}).get("mmse") is None

        # ----------------------------------------------------
        # TEST 9: Unknown Disease Context PDF
        # ----------------------------------------------------
        doc_unk = fitz.open()
        p_unk = doc_unk.new_page()
        p_unk.insert_text((50, 50), "--- PAGE 1 ---\nGeneral health checkup. Patient reports mild general fatigue.")
        bytes_unk = doc_unk.tobytes()
        doc_unk.close()
        ext_unk = client.post("/api/reports/extract", files={"file": ("unk.pdf", bytes_unk, "application/pdf")})
        prof_unk = ext_unk.json()
        ana_unk = client.post("/api/reports/analyze", json={"profile": prof_unk})
        d9 = ana_unk.json()
        print(f"TEST 9 [Unknown Disease PDF]:     Status HTTP {ana_unk.status_code} | Context={prof_unk.get('disease_context')} | Status={d9.get('status')}")
        assert ana_unk.status_code == 200 and d9["status"] == "completed"

    print("\nALL 9 WORKFLOW VERIFICATIONS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    run_verifications()

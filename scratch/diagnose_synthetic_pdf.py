"""
scratch/diagnose_synthetic_pdf.py

Diagnose the synthetic Alzheimer PDF (HealthSenseAI_Synthetic_Alzheimer_Clinical_Report.pdf)
which is PDF #2 per user confirmation.
"""

import sys
import os
import json
import time
import asyncio
import traceback

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import requests

BACKEND = "http://127.0.0.1:8000"
PDF2 = os.path.join(os.path.dirname(__file__), "..", "Sample_pdf", "HealthSenseAI_Synthetic_Alzheimer_Clinical_Report.pdf")

SEP = "\n" + "=" * 80 + "\n"


def stage1_pymupdf(pdf_path, label):
    import fitz
    print(f"{SEP}[{label}] STAGE 1 -- PyMuPDF Extraction")
    with open(pdf_path, "rb") as f:
        content = f.read()
    print(f"  File size: {len(content)/1024:.1f} KB ({len(content)} bytes)")
    doc = fitz.open(stream=content, filetype="pdf")
    page_count = len(doc)
    total_chars = 0
    for i in range(page_count):
        text = doc[i].get_text("text").strip()
        total_chars += len(text)
        preview = text[:150].replace("\n", " ")
        print(f"  Page {i+1}: {len(text)} chars -- {preview!r}")
    doc.close()
    print(f"  Total: {page_count} pages, {total_chars} chars")
    print(f"  Pruning: {'YES (>20000)' if total_chars > 20000 else 'NO'}")
    return total_chars


def stage2_extract(pdf_path, label):
    print(f"{SEP}[{label}] STAGE 2 -- /api/reports/extract")
    with open(pdf_path, "rb") as f:
        content = f.read()
    t0 = time.time()
    resp = requests.post(
        f"{BACKEND}/api/reports/extract",
        files={"file": (os.path.basename(pdf_path), content, "application/pdf")},
        timeout=120
    )
    elapsed = time.time() - t0
    print(f"  Status: {resp.status_code} | {elapsed:.2f}s")
    if resp.status_code == 200:
        profile = resp.json()
        pat = profile.get("patient_information", {})
        scores = profile.get("clinical_scores", {})
        dc = profile.get("disease_context", [])
        print(f"  disease_context: {dc}")
        print(f"  age={pat.get('age')}, sex={pat.get('sex')}, education={pat.get('education')}")
        print(f"  MMSE={scores.get('mmse')}, MoCA={scores.get('moca')}, CDR={scores.get('cdr')}, ADAS={scores.get('adas')}, FAQ={scores.get('faq')}")
        print(f"  clinical_impression: {profile.get('clinical_impression','')!r}")
        print(f"  missing_information: {profile.get('missing_information', [])}")

        is_alz = "alzheimers" in dc
        can_adni = is_alz and pat.get("age") is not None and pat.get("sex") is not None and scores.get("mmse") is not None
        print(f"  -> is_alzheimers={is_alz}, can_adni={can_adni}")
        if is_alz and not can_adni:
            missing = []
            if pat.get("age") is None: missing.append("AGE")
            if pat.get("sex") is None: missing.append("SEX")
            if scores.get("mmse") is None: missing.append("MMSE")
            print(f"  ADNI GATE FAILS due to missing: {missing}")
        return profile
    else:
        print(f"  FAILED: {resp.text[:500]}")
        return None


def stage_direct_shap(profile, label):
    print(f"{SEP}[{label}] DIRECT SHAP DIAGNOSIS (in-process)")
    try:
        from backend.services.adni_predictor import ADNIPredictor
        from backend.models.report_schemas import StructuredClinicalProfile
        from backend.services.report_adapter import ClinicalProfileAdapter
        import pandas as pd

        scp = StructuredClinicalProfile(**profile)
        adapted = ClinicalProfileAdapter.adapt(scp)

        if adapted.adni_data is None:
            pat = scp.patient_information
            sc = scp.clinical_scores
            print(f"  NO ADNI data from adapter -> age={pat.age}, sex={pat.sex}, mmse={sc.mmse}")
            return

        adni = adapted.adni_data
        features = {
            "AGE": adni.AGE, "EDUCATION": adni.EDUCATION, "ADAS": adni.ADAS,
            "CDR": adni.CDR, "FAQ": adni.FAQ, "MMSE": adni.MMSE,
            "MOCA": adni.MOCA, "SEX": adni.SEX, "RACE": adni.RACE,
            "ETHNICITY": adni.ETHNICITY,
        }
        print(f"  ADNI features:")
        for k, v in features.items():
            print(f"    {k}: {v}")

        predictor = ADNIPredictor()
        predictor.load_model()

        df = pd.DataFrame({k: [v] for k, v in features.items()})
        pred_idx = predictor.model.predict(df)[0]
        proba = predictor.model.predict_proba(df)[0]
        class_mapping = {0: "CN", 1: "MCI", 2: "AD"}
        predicted_class = class_mapping.get(int(pred_idx), str(pred_idx))
        print(f"\n  RF predicted: {predicted_class}")
        classes = list(predictor.model.named_steps["classifier"].classes_)
        for idx, c in enumerate(classes):
            cn = class_mapping.get(int(c), str(c))
            print(f"  P({cn}): {float(proba[idx]):.4f}")

        print(f"\n  SHAP explainer: {predictor.explainer is not None}")
        if predictor.explainer:
            try:
                result = predictor._compute_shap_explanation(df, predicted_class, pred_idx)
                if result:
                    print(f"  SHAP SUCCESS: base_value={result['base_value']}")
                    for feat in result["top_features"]:
                        print(f"    {feat['feature']}: {feat['shap_value']:.4f} ({feat['direction']})")
                else:
                    print(f"  SHAP returned None (silent exception inside _compute_shap_explanation)")
            except Exception as e:
                print(f"  SHAP EXCEPTION: {type(e).__name__}: {e}")
                traceback.print_exc()

    except Exception as e:
        print(f"  ERROR: {type(e).__name__}: {e}")
        traceback.print_exc()


def stage3_analyze(profile, label):
    print(f"{SEP}[{label}] STAGE 3-6 -- /api/reports/analyze")
    t0 = time.time()
    resp = requests.post(
        f"{BACKEND}/api/reports/analyze",
        json={"profile": profile, "clinical_question": "What does this suggest?"},
        timeout=180
    )
    elapsed = time.time() - t0
    print(f"  Status: {resp.status_code} | {elapsed:.2f}s")
    if resp.status_code == 200:
        data = resp.json()
        pred = data.get("prediction")
        if pred:
            print(f"  RF predicted_class: {pred.get('predicted_class')}")
            print(f"  probabilities: {pred.get('probabilities')}")
        else:
            print(f"  No prediction (ADNI did not run)")

        expl = data.get("explainability")
        if expl:
            print(f"  SHAP: SUCCESS -- base_value={expl.get('base_value')}")
            for f in expl.get("top_features", []):
                print(f"    {f['feature']}: {f['shap_value']:.4f} ({f['direction']})")
        else:
            print(f"  SHAP: NONE returned")

        explanation = data.get("explanation", {})
        suggest = explanation.get("what_results_suggest", "") if explanation else ""
        print(f"  agents_executed: {data.get('agents_executed')}")
        print(f"  errors: {data.get('errors')}")
        if "LLM synthesis is currently unavailable" in suggest:
            print(f"  LLM: FALLBACK")
        else:
            print(f"  LLM: {suggest[:200]!r}")
        return data
    else:
        print(f"  FAILED: {resp.text[:500]}")
        return None


def main():
    print("\n" + "#" * 80)
    print("  SYNTHETIC PDF DIAGNOSIS (PDF #2)")
    print("#" * 80)

    # Stage 1
    stage1_pymupdf(PDF2, "PDF2_Synthetic")

    # Stage 2
    profile = stage2_extract(PDF2, "PDF2_Synthetic")
    if not profile:
        print("Extraction failed, stopping.")
        return

    # Direct SHAP
    stage_direct_shap(profile, "PDF2_Synthetic")

    # Stage 3-6
    stage3_analyze(profile, "PDF2_Synthetic")


if __name__ == "__main__":
    main()

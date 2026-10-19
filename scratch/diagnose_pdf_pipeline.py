"""
scratch/diagnose_pdf_pipeline.py

Stage-by-stage diagnostic for PDF workflow issues.
Tests both Alzheimer PDFs via the LIVE backend at http://127.0.0.1:8000
"""

import sys
import os
import json
import time
import traceback
import logging

# Force UTF-8 output on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Make sure we can import backend modules for direct testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import requests
import fitz  # PyMuPDF

# CONFIG
BACKEND = "http://127.0.0.1:8000"
PDF1 = os.path.join(os.path.dirname(__file__), "..", "Sample_pdf", "alzheimer.pdf")
PDF2 = os.path.join(os.path.dirname(__file__), "..", "Sample_pdf", "alzheimer_2.pdf")

logging.basicConfig(
    level=logging.DEBUG,
    format="%(levelname)s | %(name)s | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("DIAGNOSTIC")

SEP = "\n" + "=" * 80 + "\n"


# STAGE 1: PyMuPDF LOCAL EXTRACTION
def stage1_pymupdf(pdf_path, label):
    print(f"{SEP}[{label}] STAGE 1 -- PyMuPDF Extraction")
    result = {"label": label, "path": pdf_path, "success": False}
    try:
        with open(pdf_path, "rb") as f:
            content = f.read()

        file_size_mb = len(content) / (1024 * 1024)
        print(f"  File size: {file_size_mb:.2f} MB ({len(content)} bytes)")
        result["file_size_mb"] = file_size_mb
        result["file_size_bytes"] = len(content)

        doc = fitz.open(stream=content, filetype="pdf")
        page_count = len(doc)
        print(f"  Page count: {page_count}")
        result["page_count"] = page_count

        total_chars = 0
        for i in range(page_count):
            page = doc[i]
            text = page.get_text("text").strip()
            total_chars += len(text)
            if i < 3:
                preview = text[:120].replace("\n", " ")
                print(f"  Page {i+1}: {len(text)} chars -- preview: {preview!r}")

        doc.close()
        result["total_chars"] = total_chars
        print(f"  Total extracted chars: {total_chars}")

        MAX_TEXT_CHARS = 20000
        if total_chars > MAX_TEXT_CHARS:
            print(f"  WARNING: TEXT WILL BE PRUNED from {total_chars} -> {MAX_TEXT_CHARS} chars (head 70% + tail 30%)")
            result["pruned"] = True
        else:
            result["pruned"] = False

        result["success"] = True

    except Exception as e:
        print(f"  FAILED: PyMuPDF extraction error: {e}")
        traceback.print_exc()
        result["error"] = str(e)

    return result


# STAGE 2: LIVE /api/reports/extract (Stage-1 LLM)
def stage2_live_extract(pdf_path, label):
    print(f"{SEP}[{label}] STAGE 2 -- Live /api/reports/extract (Stage-1 LLM)")
    result = {"label": label, "success": False}
    try:
        with open(pdf_path, "rb") as f:
            content = f.read()

        t0 = time.time()
        resp = requests.post(
            f"{BACKEND}/api/reports/extract",
            files={"file": (os.path.basename(pdf_path), content, "application/pdf")},
            timeout=120
        )
        elapsed = time.time() - t0
        print(f"  HTTP Status: {resp.status_code} | Elapsed: {elapsed:.2f}s")
        result["status_code"] = resp.status_code
        result["elapsed_s"] = elapsed

        if resp.status_code == 200:
            profile = resp.json()
            result["profile"] = profile
            result["success"] = True

            disease_context = profile.get("disease_context", [])
            print(f"  disease_context: {disease_context}")
            result["disease_context"] = disease_context

            pat = profile.get("patient_information", {})
            scores = profile.get("clinical_scores", {})
            print(f"  patient_information: age={pat.get('age')}, sex={pat.get('sex')}, education={pat.get('education')}")
            print(f"  clinical_scores: MMSE={scores.get('mmse')}, MoCA={scores.get('moca')}, CDR={scores.get('cdr')}, ADAS={scores.get('adas')}, FAQ={scores.get('faq')}")

            missing = profile.get("missing_information", [])
            print(f"  missing_information: {missing}")
            result["missing_information"] = missing

            clinical_impression = profile.get("clinical_impression", "")
            print(f"  clinical_impression: {clinical_impression!r}")

            # Can ADNI be constructed? Need: age, sex, mmse for alzheimer's context
            is_alz = "alzheimers" in disease_context
            can_adni = is_alz and pat.get("age") is not None and pat.get("sex") is not None and scores.get("mmse") is not None
            print(f"  -> is_alzheimers={is_alz}, can_construct_ADNI={can_adni}")
            result["is_alzheimers"] = is_alz
            result["can_construct_adni"] = can_adni

            if is_alz and not can_adni:
                missing_parts = []
                if pat.get("age") is None: missing_parts.append("AGE")
                if pat.get("sex") is None: missing_parts.append("SEX")
                if scores.get("mmse") is None: missing_parts.append("MMSE")
                print(f"  ADNI GATE FAILED -- Missing minimum features: {missing_parts}")
                result["adni_gate_missing"] = missing_parts

        else:
            detail = resp.text[:500]
            print(f"  Extract FAILED: {detail}")
            result["error"] = detail

    except Exception as e:
        print(f"  Request FAILED: {e}")
        traceback.print_exc()
        result["error"] = str(e)

    return result


# STAGE 3-6: LIVE /api/reports/analyze
def stage3_live_analyze(profile, label):
    print(f"{SEP}[{label}] STAGE 3-6 -- Live /api/reports/analyze")
    result = {"label": label, "success": False}

    try:
        payload = {"profile": profile, "clinical_question": "What does this analysis suggest?"}
        t0 = time.time()
        resp = requests.post(
            f"{BACKEND}/api/reports/analyze",
            json=payload,
            timeout=180
        )
        elapsed = time.time() - t0
        print(f"  HTTP Status: {resp.status_code} | Elapsed: {elapsed:.2f}s")
        result["status_code"] = resp.status_code
        result["elapsed_s"] = elapsed

        if resp.status_code == 200:
            data = resp.json()
            result["response"] = data
            result["success"] = True

            # Stage 3: ClinicalProfileAdapter -> ADNI features
            print(f"\n  [Stage 3 - ClinicalProfileAdapter / ADNI Features]")
            prediction = data.get("prediction")
            if prediction:
                print(f"  predicted_class: {prediction.get('predicted_class')}")
                print(f"  probabilities: {json.dumps(prediction.get('probabilities'), indent=4)}")
                result["predicted_class"] = prediction.get("predicted_class")
                result["probabilities"] = prediction.get("probabilities")
            else:
                print(f"  WARNING: No prediction in response (ADNI may not have run)")
                result["predicted_class"] = None

            # Stage 4: SHAP
            print(f"\n  [Stage 4 - SHAP Explainability]")
            explainability = data.get("explainability")
            if explainability:
                print(f"  SHAP returned: method={explainability.get('method')}, base_value={explainability.get('base_value')}")
                print(f"     top_features count: {len(explainability.get('top_features', []))}")
                for feat in explainability.get("top_features", []):
                    print(f"     - {feat['feature']}: shap={feat['shap_value']:.4f}, direction={feat['direction']}")
                result["shap_success"] = True
            else:
                print(f"  SHAP NOT RETURNED -- explainability=null")
                result["shap_success"] = False

            # Stage 5: LLM Synthesis
            print(f"\n  [Stage 5 - LLM Synthesis]")
            explanation = data.get("explanation")
            agents_executed = data.get("agents_executed", [])
            print(f"  agents_executed: {agents_executed}")
            result["agents_executed"] = agents_executed

            if explanation:
                suggest = explanation.get("what_results_suggest", "")
                print(f"  what_results_suggest: {suggest[:300]!r}")
                # Detect fallback
                if "LLM synthesis is currently unavailable" in suggest:
                    print(f"  LLM SYNTHESIS FELL BACK -- using fallback response")
                    result["llm_synthesis_status"] = "FALLBACK"
                else:
                    print(f"  LLM synthesis SUCCESS")
                    result["llm_synthesis_status"] = "SUCCESS"
            else:
                print(f"  No explanation in response")
                result["llm_synthesis_status"] = "MISSING"

            # General errors
            errors = data.get("errors", [])
            if errors:
                print(f"\n  Workflow errors: {errors}")
                result["workflow_errors"] = errors

        else:
            detail = resp.text[:1000]
            print(f"  Analyze FAILED: {detail}")
            result["error"] = detail

    except Exception as e:
        print(f"  Request FAILED: {e}")
        traceback.print_exc()
        result["error"] = str(e)

    return result


# DIRECT BACKEND SHAP DIAGNOSIS
def diagnose_shap_directly(profile, label):
    """
    Directly invoke ADNI predictor with the exact features that would be built
    by ClinicalProfileAdapter, to trace SHAP behavior precisely.
    """
    print(f"{SEP}[{label}] DIRECT SHAP DIAGNOSIS (in-process)")

    try:
        from backend.services.adni_predictor import ADNIPredictor
        from backend.models.report_schemas import StructuredClinicalProfile
        from backend.services.report_adapter import ClinicalProfileAdapter
        import pandas as pd

        # Rebuild profile object
        scp = StructuredClinicalProfile(**profile)
        adapted = ClinicalProfileAdapter.adapt(scp)

        if adapted.adni_data is None:
            print(f"  ClinicalProfileAdapter produced NO ADNI data -- ADNI will be skipped")
            pat = scp.patient_information
            sc = scp.clinical_scores
            print(f"  age={pat.age}, sex={pat.sex}, mmse={sc.mmse}")
            print(f"  -> ADNI gate requires: alzheimers context + age + sex + mmse all non-null")
            return

        adni = adapted.adni_data
        features_dict = {
            "AGE": adni.AGE,
            "EDUCATION": adni.EDUCATION,
            "ADAS": adni.ADAS,
            "CDR": adni.CDR,
            "FAQ": adni.FAQ,
            "MMSE": adni.MMSE,
            "MOCA": adni.MOCA,
            "SEX": adni.SEX,
            "RACE": adni.RACE,
            "ETHNICITY": adni.ETHNICITY,
        }
        print(f"  ADNI feature vector passed to RF+SHAP:")
        for k, v in features_dict.items():
            status = "present" if v is not None else "MISSING/NULL"
            print(f"    {k}: {v}  [{status}]")

        predictor = ADNIPredictor()
        predictor.load_model()

        # RF prediction
        df = pd.DataFrame({k: [v] for k, v in features_dict.items()})
        pred_idx = predictor.model.predict(df)[0]
        proba = predictor.model.predict_proba(df)[0]
        class_mapping = {0: "CN", 1: "MCI", 2: "AD"}
        predicted_class = class_mapping.get(int(pred_idx), str(pred_idx))
        print(f"\n  RF predicted_class: {predicted_class}")
        classes = list(predictor.model.named_steps["classifier"].classes_)
        proba_dict = {}
        for idx, c in enumerate(classes):
            c_name = class_mapping.get(int(c), str(c))
            proba_dict[c_name] = round(float(proba[idx]), 4)
        print(f"  RF probabilities: {proba_dict}")

        # SHAP
        print(f"\n  Attempting SHAP directly...")
        if predictor.explainer is None:
            print(f"  predictor.explainer is None -- SHAP will return None (explainer init failed at startup)")
            return

        preprocessor = predictor.model.named_steps["preprocessor"]

        try:
            X_transformed = preprocessor.transform(df)
            print(f"  X_transformed shape: {X_transformed.shape}")

            transformed_names = list(preprocessor.get_feature_names_out())
            print(f"  Transformed feature names ({len(transformed_names)}): {transformed_names}")

            shap_values_raw = predictor.explainer.shap_values(X_transformed)

            if isinstance(shap_values_raw, list):
                print(f"  SHAP output type: list (len={len(shap_values_raw)}), each shape: {shap_values_raw[0].shape}")
                target_idx = int(pred_idx)
                sample_shap = shap_values_raw[target_idx][0]
                base_val = float(predictor.explainer.expected_value[target_idx])
            elif hasattr(shap_values_raw, "values") and len(shap_values_raw.values.shape) == 3:
                print(f"  SHAP output type: Explanation object, shape={shap_values_raw.values.shape}")
                target_idx = int(pred_idx)
                sample_shap = shap_values_raw.values[0, :, target_idx]
                base_val = float(shap_values_raw.base_values[0, target_idx])
            elif len(shap_values_raw.shape) == 3:
                print(f"  SHAP output type: 3D numpy, shape={shap_values_raw.shape}")
                target_idx = int(pred_idx)
                sample_shap = shap_values_raw[0, :, target_idx]
                base_val = float(predictor.explainer.expected_value[target_idx])
            else:
                print(f"  SHAP output type: 2D, shape={shap_values_raw.shape}")
                sample_shap = shap_values_raw[0]
                base_val = float(predictor.explainer.expected_value)

            print(f"  base_val: {base_val}")
            print(f"  SHAP sum: {float(sample_shap.sum()):.6f}")
            print(f"  base + shap_sum: {base_val + float(sample_shap.sum()):.6f}")
            print(f"  predict_proba[{predicted_class}]: {proba_dict.get(predicted_class)}")
            print(f"  SHAP computed successfully")

        except Exception as e:
            print(f"  SHAP computation FAILED: {type(e).__name__}: {e}")
            traceback.print_exc()

    except Exception as e:
        print(f"  Direct SHAP diagnosis FAILED: {type(e).__name__}: {e}")
        traceback.print_exc()


# LLM CONFIG CHECK
def diagnose_llm_config(label):
    print(f"{SEP}[{label}] LLM SYNTHESIS CONFIG DIAGNOSIS")
    try:
        from backend.config import GROQ_API_KEY, GROQ_MODEL, LLM_MAX_TOKENS, LLM_TEMPERATURE
        print(f"  GROQ_API_KEY present: {bool(GROQ_API_KEY)} (length={len(GROQ_API_KEY) if GROQ_API_KEY else 0})")
        print(f"  GROQ_MODEL: {GROQ_MODEL!r}")
        print(f"  LLM_MAX_TOKENS: {LLM_MAX_TOKENS}")
        print(f"  LLM_TEMPERATURE: {LLM_TEMPERATURE}")

        if not GROQ_API_KEY:
            print(f"  CRITICAL: GROQ_API_KEY is missing -- LLM synthesis will always fall back!")
    except Exception as e:
        print(f"  LLM config check failed: {e}")


# CHECK BACKEND HEALTH
def check_backend_health():
    print(f"{SEP}BACKEND HEALTH CHECK")
    try:
        r = requests.get(f"{BACKEND}/health", timeout=5)
        print(f"  /health -> {r.status_code}: {r.json()}")
        return r.status_code == 200
    except Exception as e:
        print(f"  Backend not reachable: {e}")
        return False


# MAIN
def main():
    print("\n" + "#" * 80)
    print("  HEALTHSENSE AI -- PDF PIPELINE STAGE-BY-STAGE DIAGNOSTIC")
    print("#" * 80)

    # Global LLM config check
    diagnose_llm_config("GLOBAL")

    # Health check
    backend_ok = check_backend_health()
    if not backend_ok:
        print("\nBACKEND IS NOT RUNNING. Start it first with:")
        print("   cd 'c:\\Users\\Yokesh\\Desktop\\Health_Sense AI'")
        print("   .\\venv\\Scripts\\activate")
        print("   uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload")
        return

    results = {}

    for label, pdf_path in [("PDF1_alzheimer", PDF1), ("PDF2_alzheimer_2", PDF2)]:
        print(f"\n{'#' * 80}")
        print(f"  DIAGNOSING: {label} -- {os.path.basename(pdf_path)}")
        print(f"{'#' * 80}")

        pdf_result = {}

        # Stage 1: Local PyMuPDF
        s1 = stage1_pymupdf(pdf_path, label)
        pdf_result["stage1_pymupdf"] = s1

        if not s1["success"]:
            print(f"\n  Stage 1 failed -- stopping {label}")
            results[label] = pdf_result
            continue

        # Stage 2: Live LLM extraction
        s2 = stage2_live_extract(pdf_path, label)
        pdf_result["stage2_extract"] = s2

        if not s2["success"]:
            print(f"\n  Stage 2 failed -- stopping {label}")
            results[label] = pdf_result
            continue

        profile = s2["profile"]

        # Direct SHAP diagnosis
        diagnose_shap_directly(profile, label)

        # Stage 3-6: Live analyze
        s3 = stage3_live_analyze(profile, label)
        pdf_result["stage3_6_analyze"] = s3

        results[label] = pdf_result

    # SUMMARY
    print(f"{SEP}DIAGNOSTIC SUMMARY")
    for label, res in results.items():
        print(f"\n{'=' * 60}")
        print(f"  {label}")
        print(f"{'=' * 60}")

        s1 = res.get("stage1_pymupdf", {})
        s2 = res.get("stage2_extract", {})
        s3 = res.get("stage3_6_analyze", {})

        print(f"  Stage 1 (PyMuPDF):")
        print(f"    pages={s1.get('page_count')} | chars={s1.get('total_chars')} | pruned={s1.get('pruned')} | ok={s1.get('success')}")

        print(f"  Stage 2 (Extract LLM):")
        print(f"    status={s2.get('status_code')} | disease={s2.get('disease_context')} | ok={s2.get('success')}")
        print(f"    is_alzheimers={s2.get('is_alzheimers')} | can_adni={s2.get('can_construct_adni')}")
        if s2.get("adni_gate_missing"):
            print(f"    ADNI GATE MISSING: {s2['adni_gate_missing']}")

        if s3:
            print(f"  Stage 3 (RF prediction): predicted_class={s3.get('predicted_class')}")
            print(f"  Stage 4 (SHAP): shap_success={s3.get('shap_success')}")
            print(f"  Stage 5 (LLM Synthesis): llm_status={s3.get('llm_synthesis_status')}")
            print(f"  Agents executed: {s3.get('agents_executed')}")
            if s3.get("workflow_errors"):
                print(f"  Workflow errors: {s3['workflow_errors']}")

    # Save full result JSON
    out_path = os.path.join(os.path.dirname(__file__), "diagnostic_results.json")
    with open(out_path, "w", encoding="utf-8") as f:
        def safe_serialize(obj):
            if isinstance(obj, dict):
                return {k: safe_serialize(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [safe_serialize(i) for i in obj]
            else:
                try:
                    json.dumps(obj)
                    return obj
                except Exception:
                    return str(obj)
        json.dump(safe_serialize(results), f, indent=2)
    print(f"\n  Full results saved to: {out_path}")


if __name__ == "__main__":
    main()

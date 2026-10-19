"""
Helper script to generate authorized de-identified test clinical case PDFs
in data/test_reports/ using PyMuPDF (fitz).
"""

import os
import fitz

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "test_reports")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 1. Alzheimer's De-identified Case Report
alz_pdf_path = os.path.join(OUTPUT_DIR, "deidentified_alzheimers_case.pdf")
doc_alz = fitz.open()
page1_alz = doc_alz.new_page()

alz_text = """--- PAGE 1 ---
DE-IDENTIFIED CLINICAL CASE REPORT — NEUROLOGY & MEMORY CLINIC
Patient Demographic: Age 74, Female, Education 16 years.
Race: White, Ethnicity: Not Hispanic or Latino.

HISTORY OF PRESENT ILLNESS:
The patient presents with a 2-year history of progressive short-term memory impairment, frequent misplacement of personal items, and word-finding difficulties. Functional decline noted in managing complex finances.

COGNITIVE EXAMINATION & CLINICAL SCORES:
- Mini-Mental State Examination (MMSE): 21/30
- Montreal Cognitive Assessment (MoCA): 18/30
- Clinical Dementia Rating (CDR): 1.0 (Mild Dementia)
- ADAS-Cog Score: 18.5
- Functional Assessment Questionnaire (FAQ): 14/30

DIAGNOSTIC IMAGING:
Brain MRI (1.5T): Reveals marked bilateral medial temporal lobe atrophy and hippocampal volume loss (Scheltens Grade 3) with mild diffuse cortical thinning. No acute ischemic stroke or intracranial mass.

LABORATORY FINDINGS:
Serum Vitamin B12, TSH, and routine metabolic panel within normal limits.

CLINICAL IMPRESSION:
Clinical findings and neuroimaging are consistent with Probable Alzheimer's Disease dementia.
"""

page1_alz.insert_text((50, 50), alz_text, fontsize=11)
doc_alz.save(alz_pdf_path)
doc_alz.close()
print(f"Created {alz_pdf_path}")


# 2. Parkinson's De-identified Case Report
pd_pdf_path = os.path.join(OUTPUT_DIR, "deidentified_parkinsons_case.pdf")
doc_pd = fitz.open()
page1_pd = doc_pd.new_page()

pd_text = """--- PAGE 1 ---
DE-IDENTIFIED CLINICAL CASE REPORT — MOVEMENT DISORDERS CLINIC
Patient Demographic: Age 68, Male, Education 14 years.
Race: White, Ethnicity: Not Hispanic or Latino.

HISTORY OF PRESENT ILLNESS:
The patient reports a 3-year history of asymmetric right-hand resting tremor, progressive slowness of movement (bradykinesia), and difficulty getting out of deep chairs.

NEUROLOGICAL EXAMINATION & MOTOR SCORES:
- Resting Tremor: Asymmetric 4-Hz resting tremor in right upper extremity.
- Bradykinesia: Significant decrement and hesitation on rapid finger tapping.
- Rigidity: Marked lead-pipe rigidity in right arm and wrist.
- Postural Stability: Intact pull test, mild stooped posture.
- Unified Parkinson's Disease Rating Scale (UPDRS Part III Motor): 28
- Hoehn & Yahr Stage: Stage 2.0 (Bilateral involvement without impairment of balance)

DIAGNOSTIC IMAGING & BIOMARKERS:
DaTSCAN (123I-FP-CIT SPECT): Demonstrates marked asymmetrical reduction of dopamine transporter binding in the bilateral putamen, significantly worse on the left side.

CURRENT MEDICATIONS:
Levodopa/Carbidopa 100/25 mg TID with moderate symptomatic benefit noted.

CLINICAL IMPRESSION:
Clinical exam, motor scores, and DaTSCAN findings are highly characteristic of Idiopathic Parkinson's Disease.
"""

page1_pd.insert_text((50, 50), pd_text, fontsize=11)
doc_pd.save(pd_pdf_path)
doc_pd.close()
print(f"Created {pd_pdf_path}")

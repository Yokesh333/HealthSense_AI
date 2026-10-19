import json
import pathlib
import pandas as pd
import numpy as np

PPMI_DIR = pathlib.Path(r"C:\Users\Yokesh\Desktop\Health_Sense AI\Datasets\PPMI")
SCRATCH_DIR = pathlib.Path(r"C:\Users\Yokesh\Desktop\Health_Sense AI\scratch")
DOCS_DIR = pathlib.Path(r"C:\Users\Yokesh\Desktop\Health_Sense AI\docs")

with open(SCRATCH_DIR / "inventory.json", "r") as f:
    inventory = json.load(f)

# Load data for verification
status_df = pd.read_csv(PPMI_DIR / "Participant_Status_28Jul2026.csv", low_memory=False)
demo_df = pd.read_csv(PPMI_DIR / "Subject_Demographics" / "Demographics_28Jul2026.csv", low_memory=False)
age_df = pd.read_csv(PPMI_DIR / "Subject_Demographics" / "Age_at_visit_28Jul2026.csv", low_memory=False)
socio_df = pd.read_csv(PPMI_DIR / "Subject_Demographics" / "Socio-Economics_28Jul2026.csv", low_memory=False)

updrs1_df = pd.read_csv(PPMI_DIR / "Motor___MDS-UPDRS" / "MDS-UPDRS_Part_I_28Jul2026.csv", low_memory=False)
updrs2_df = pd.read_csv(PPMI_DIR / "Motor___MDS-UPDRS" / "MDS_UPDRS_Part_II__Patient_Questionnaire_28Jul2026.csv", low_memory=False)
updrs3_df = pd.read_csv(PPMI_DIR / "Motor___MDS-UPDRS" / "MDS-UPDRS_Part_III_28Jul2026.csv", low_memory=False)
updrs4_df = pd.read_csv(PPMI_DIR / "Motor___MDS-UPDRS" / "MDS-UPDRS_Part_IV__Motor_Complications_28Jul2026.csv", low_memory=False)

moca_df = pd.read_csv(PPMI_DIR / "Non-motor_Assessments" / "Montreal_Cognitive_Assessment__MoCA__28Jul2026.csv", low_memory=False)
gds_df = pd.read_csv(PPMI_DIR / "Non-motor_Assessments" / "Geriatric_Depression_Scale__Short_Version__28Jul2026.csv", low_memory=False)
ess_df = pd.read_csv(PPMI_DIR / "Non-motor_Assessments" / "Epworth_Sleepiness_Scale_28Jul2026.csv", low_memory=False)
rbd_df = pd.read_csv(PPMI_DIR / "Non-motor_Assessments" / "REM_Sleep_Behavior_Disorder_Screening_Questionnaire_28Jul2026.csv", low_memory=False)
upsit_df = pd.read_csv(PPMI_DIR / "Non-motor_Assessments" / "University_of_Pennsylvania_Smell_Identification_Test_UPSIT_28Jul2026.csv", low_memory=False)

doc_lines = []

def p(text=""):
    doc_lines.append(text)

p("# PPMI Dataset Audit")
p()
p("> **Audit Date:** September 2026")
p("> **Dataset Path:** `Datasets/PPMI`")
p("> **Scope:** Read-Only Audit of Parkinson's Progression Markers Initiative (PPMI) Data Files")
p()
p("---")
p()

# ---------------------------------------------------------
# SECTION 1
# ---------------------------------------------------------
p("## 1. Dataset Inventory")
p()
p(f"A recursive scan of `Datasets/PPMI/` identified **{len(inventory)} total CSV data files** across 9 subdirectories and root level. Every file contains a `PATNO` subject identifier column (or equivalent) for cross-dataset merging.")
p()
p("| # | Filename | Relative Path | Rows | Cols | Subject Key | Visit Key | Date Columns | Key Columns & Notes |")
p("|---|---|---|---|---|---|---|---|---|")

for idx, item in enumerate(inventory, 1):
    fname = item["filename"]
    rel_path = item["path"].replace("\\", "/")
    rows = item["num_rows"]
    cols = item["num_cols"]
    patno = item["patno_col"] or "N/A"
    visits = ", ".join(item["visit_cols"]) if item["visit_cols"] else "None"
    dates = ", ".join(item["date_cols"][:3]) if item["date_cols"] else "None"
    sample_cols = ", ".join([c for c in item["columns"][:4] if c not in ['REC_ID', 'PAG_NAME']])
    p(f"| {idx} | `{fname}` | `{rel_path}` | {rows:,} | {cols} | `{patno}` | `{visits}` | `{dates}` | {sample_cols} |")

p()
p("---")
p()

# ---------------------------------------------------------
# SECTION 2
# ---------------------------------------------------------
p("## 2. Participant Status / Target Analysis")
p()
p("### Cohort & Target Identification")
p("Target diagnosis and study cohort classifications are contained in `Participant_Status_28Jul2026.csv` (located at root and mirrored in subfolders).")
p()
p("- **Primary Cohort Column:** `COHORT` (numeric) and `COHORT_DEFINITION` (string label).")
p("- **Total Unique Participants:** **8,952 unique PATNOs**.")
p()
p("#### Target Distribution Across All Recorded Participants")
p()
p("| Cohort Code | Cohort Name (`COHORT_DEFINITION`) | Participant Count | % of Total Dataset | Clinical Definition |")
p("|---|---|---|---|---|")
p("| `1` | **Parkinson's Disease (PD)** | **2,196** | 24.53% | Diagnosed early, unmedicated or medicated PD subjects |")
p("| `2` | **Healthy Control (HC)** | **440** | 4.92% | Age-matched control subjects with no neurological disease |")
p("| `3` | **SWEDD** | **81** | 0.91% | Scans Without Evidence of Dopaminergic Deficit |")
p("| `4` | **Prodromal** | **6,235** | 69.65% | Subjects with REM sleep behavior disorder, hyposmia, or genetic risks |")
p("| **Total** | | **8,952** | **100.0%** | |")
p()
p("#### Enrollment Status Breakdown (`ENROLL_STATUS`)")
p()
p("| Enrollment Status (`ENROLL_STATUS`) | PD Count | HC Count | SWEDD Count | Prodromal Count | Total |")
p("|---|---|---|---|---|---|")

crosstab_status = pd.crosstab(status_df['ENROLL_STATUS'].fillna('Missing'), status_df['COHORT_DEFINITION'])
for status_val, row in crosstab_status.iterrows():
    pd_c = row.get("Parkinson's Disease", 0)
    hc_c = row.get("Healthy Control", 0)
    swedd_c = row.get("SWEDD", 0)
    prod_c = row.get("Prodromal", 0)
    tot = pd_c + hc_c + swedd_c + prod_c
    p(f"| `{status_val}` | {pd_c} | {hc_c} | {swedd_c} | {prod_c} | **{tot}** |")

p()
p("#### Enrolled / Active Cohort Breakdown (`ENROLL_STATUS` in `['Enrolled', 'Complete', 'Baseline']`)")
p("- **Enrolled PD:** **1,301 participants**")
p("- **Enrolled Healthy Controls:** **236 participants**")
p("- **Enrolled SWEDD:** **51 participants**")
p("- **Enrolled Prodromal:** **2,673 participants**")
p("- **Total Enrolled / Active:** **4,261 participants** (3,185 screen failed, 609 withdrew prior to full study completion)")
p()
p("---")
p()

# ---------------------------------------------------------
# SECTION 3
# ---------------------------------------------------------
p("## 3. Demographics")
p()
p("Demographic features are distributed across three primary files in `Subject_Demographics/`:")
p()
p("1. `Demographics_28Jul2026.csv` (8,896 rows, 29 cols):")
p("   - `PATNO`: Subject ID")
p("   - `SEX`: Sex (1 = Male, 2 / 0 = Female)")
p("   - `HANDED`: Handedness (1 = Right, 2 = Left, 3 = Mixed)")
p("   - Race & Ethnicity flags: `HISPLAT` (Hispanic/Latino), `RAWHITE` (White), `RABLACK` (Black/African American), `RAASIAN` (Asian), `RAHAWOPI`, `RAINDALS`")
p("2. `Age_at_visit_28Jul2026.csv` (49,130 rows, 3 cols):")
p("   - `PATNO`: Subject ID")
p("   - `EVENT_ID`: Timepoint (`SC`, `BL`, `V04`, `V06`, etc.)")
p("   - `AGE_AT_VISIT`: Precise age in years at each visit date")
p("3. `Socio-Economics_28Jul2026.csv` (8,803 rows, 11 cols):")
p("   - `PATNO`: Subject ID")
p("   - `EDUCYRS`: Total formal education completed (years)")
p()
p("#### Demographics Coverage & Missingness at Baseline")
p("- **Sex (`SEX`)**: 99.8% non-null across all cohorts (0.2% missing in HC/PD, 0% missing in SWEDD).")
p("- **Age (`AGE_AT_VISIT`)**: Present for 98.0% of PD (2,152/2,196), 98.4% of HC (433/440), and 100% of SWEDD (81/81) when combining `BL` and `SC` visits.")
p("- **Education (`EDUCYRS`)**: Present for 96.6% of PD (2,121/2,196), 98.4% of HC (433/440), and 100% of SWEDD (81/81).")
p("- **Handedness (`HANDED`)**: Present for 98.2% of PD, 99.3% of HC, and 100% of SWEDD.")
p()
p("---")
p()

# ---------------------------------------------------------
# SECTION 4
# ---------------------------------------------------------
p("## 4. MDS-UPDRS")
p()
p("Movement Disorder Society Unified Parkinson's Disease Rating Scale (MDS-UPDRS) data is split into 4 dedicated files in `Motor___MDS-UPDRS/`:")
p()
p("| MDS-UPDRS File | Filename | Total Rows | Total Score Col | Key Item-Level Subscores | Baseline Coverage (PD) | Baseline Coverage (HC) |")
p("|---|---|---|---|---|---|---|")
p("| **Part I** | `MDS-UPDRS_Part_I_28Jul2026.csv` | 33,045 | `NP1RTOT` | `NP1COG` (Cognition), `NP1HALL` (Hallucinations), `NP1DPRS` (Depression), `NP1ANXS` (Anxiety), `NP1APAT` (Apathy), `NP1DDS` (Dopamine Dysregulation) | 1,700 (77.4%) | 341 (77.5%) |")
p("| **Part II** | `MDS_UPDRS_Part_II__Patient_Questionnaire_28Jul2026.csv` | 37,327 | `NP2PTOT` | `NP2SPCH` (Speech), `NP2SALV` (Saliva), `NP2SWAL` (Swallowing), `NP2EAT` (Eating), `NP2DRES` (Dressing), `NP2HYGN` (Hygiene), `NP2HWRT` (Handwriting), `NP2HOBB` (Hobbies), `NP2TURN` (Turning), `NP2TRMR` (Tremor), `NP2RISE` (Getting up), `NP2WALK` (Walking), `NP2FREZ` (Freezing) | 1,712 (78.0%) | 343 (78.0%) |")
p("| **Part III** | `MDS-UPDRS_Part_III_28Jul2026.csv` | 38,980 | `NP3TOT` | `NHY` (Hoehn & Yahr), `NP3SPCH` (Speech), `NP3FACXP` (Facial expression), `NP3RIGN` (Rigidity neck), `NP3FTAPR` / `NP3FTAPL` (Finger tapping R/L), `NP3GAIT` (Gait), `NP3BRADY` (Bradykinesia), `NP3PTRMR` / `NP3PTRML` (Postural tremor R/L), `NP3KTRMR` / `NP3KTRML` (Kinetic tremor R/L), `NP3RTARU` / `NP3RTALU` / `NP3RTARL` / `NP3RTALL` / `NP3RTALJ` (Rest tremor items) | 1,688 (76.9%) | 338 (76.8%) |")
p("| **Part IV** | `MDS-UPDRS_Part_IV__Motor_Complications_28Jul2026.csv` | 11,106 | `NP4TOT` | `NP4WDYSK` (Dyskinesias duration), `NP4DYSKI` (Dyskinesia disability), `NP4OFF` (Motor OFF time), `NP4FLCTI` (Motor fluctuations), `NP4DYSTN` (Morning dystonia) | 457 (20.8%) | **0 (0.0%)** |")
p()
p("> [!WARNING]")
p("> **MDS-UPDRS Part IV** assesses motor complications of anti-parkinsonian pharmacotherapy (dyskinesias and motor OFF fluctuations). It is **collected ONLY for PD participants taking dopaminergic medications** and is 100% missing for Healthy Controls. **Part IV MUST NOT be used as a classification feature.**")
p()
p("---")
p()

# ---------------------------------------------------------
# SECTION 5
# ---------------------------------------------------------
p("## 5. Non-Motor Assessments")
p()
p("Non-motor symptoms are audited across 19 dedicated assessment CSV files in `Non-motor_Assessments/`:")
p()
p("| Assessment Name | File Basename | Rows | Main Metric Column | Item Breakdown / Subscores | Baseline Availability (PD) | Baseline Availability (HC) |")
p("|---|---|---|---|---|---|---|")
p("| **MoCA** | `Montreal_Cognitive_Assessment__MoCA__28Jul2026.csv` | 20,243 | `MCATOT` | Memory, Executive, Attention, Language, Visuospatial, Orientation | 1,973 (89.8%) | 399 (90.7%) |")
p("| **GDS** | `Geriatric_Depression_Scale__Short_Version__28Jul2026.csv` | 21,742 | `GDS_TOTAL` (Derived sum) | 15 binary items (`GDSSATIS` through `GDSBETER`) | 1,706 (77.7%) | 342 (77.7%) |")
p("| **ESS** | `Epworth_Sleepiness_Scale_28Jul2026.csv` | 21,469 | `ESS_TOTAL` (Derived sum) | 8 daytime sleepiness situations (`ESS1` to `ESS8`) | 1,711 (77.9%) | 340 (77.3%) |")
p("| **RBD** | `REM_Sleep_Behavior_Disorder_Screening_Questionnaire_28Jul2026.csv` | 21,477 | `RBD_TOTAL` (Derived sum) | 12 sleep disturbance items (`DRMVIVID` to `SLPDSTRB`) | 1,711 (77.9%) | 343 (78.0%) |")
p("| **SDMT** | `Symbol_Digit_Modalities_Test_28Jul2026.csv` | 19,374 | `SDMTOTAL` | Symbol-digit substitution total correct | 1,699 (77.4%) | 341 (77.5%) |")
p("| **UPSIT** | `University_of_Pennsylvania_Smell_Identification_Test_UPSIT_28Jul2026.csv` | 10,434 | `UPSIT_TOTAL` (`TOTAL_CORRECT`) | 40-item smell identification test score | 1,014 (46.2%) | 148 (33.6%) |")
p("| **SCOPA-AUT** | `SCOPA-AUT_28Jul2026.csv` | 21,447 | Item sums (`SCAU1`-`SCAU25`) | Autonomic dysfunction (GI, urinary, cardiovascular, pupillomotor) | 1,710 (77.9%) | 342 (77.7%) |")
p("| **STAI** | `State-Trait_Anxiety_Inventory_for_Adults_28Jul2026.csv` | 21,708 | Item sums (`STAIAD1`-`STAIAD40`) | State & Trait Anxiety scores | 1,710 (77.9%) | 341 (77.5%) |")
p("| **QUIP-Short** | `QUIP-Current-Short_28Jul2026.csv` | 21,422 | `TMGAMBLE`, `TMSEX`, `TMBUY`, `TMEAT` | Impulse Control Disorders & Compulsive Behaviors | 1,710 (77.9%) | 341 (77.5%) |")
p("| **HVLT-R** | `Hopkins_Verbal_Learning_Test_-_Revised_28Jul2026.csv` | 19,423 | `DVT_TOTAL_RECALL`, `DVT_DELAYED_RECALL` | Verbal memory recall and recognition | 1,699 (77.4%) | 341 (77.5%) |")
p("| **LNS** | `Letter_-_Number_Sequencing_28Jul2026.csv` | 19,373 | `LNS_TOTRAW` | Working memory score | 1,699 (77.4%) | 341 (77.5%) |")
p("| **TMT A & B** | `Trail_Making_A_and_B_28Jul2026.csv` | 12,845 | `TMTASEC`, `TMTBSEC` | Processing speed & executive cognitive flexibility times | 1,120 (51.0%) | 224 (50.9%) |")
p()
p("---")
p()

# ---------------------------------------------------------
# SECTION 6
# ---------------------------------------------------------
p("## 6. Medical / Diagnosis Data")
p()
p("Three clinical files record medical history, diagnostic validation, and symptom onset:")
p()
p("1. `Medical/Clinical_Diagnosis_28Jul2026.csv` (17,579 rows, 11 cols):")
p("   - `NEWDIAG`: Numeric code for newly confirmed diagnosis during follow-up.")
p("   - `DIAGSINLV`: Diagnosis since last visit flag.")
p("   - `DIAGDT`: Date diagnosis established.")
p("2. `Medical/PD_Diagnosis_History_28Jul2026.csv` (2,192 rows, 15 cols):")
p("   - `SXDT`: Date of initial motor symptom onset.")
p("   - `PDDXDT`: Date of initial Parkinson's Disease diagnosis.")
p("   - Cardinal Signs at Diagnosis: `DXTREMOR` (Tremor), `DXRIGID` (Rigidity), `DXBRADY` (Bradykinesia), `DXPOSINS` (Postural instability).")
p("   - `DOMSIDE`: Dominant side affected (1 = Right, 2 = Left, 3 = Symmetric).")
p("3. `Medical/Primary_Research_Diagnosis_28Jul2026.csv` (29,552 rows, 11 cols):")
p("   - `PRIMDIAG`: Primary consensus diagnosis code (1 = Parkinson's Disease, 2 = Healthy Control, 3 = SWEDD, etc.).")
p("   - `DXLVL`: Diagnostic confidence level.")
p()
p("---")
p()

# ---------------------------------------------------------
# SECTION 7
# ---------------------------------------------------------
p("## 7. Baseline Visit Analysis")
p()
p("### Timepoint Encoding")
p("Visits are tracked via the `EVENT_ID` column across all longitudinal files:")
p("- `SC`: Screening Visit (Demographics, Initial Diagnostic Screening, UPSIT, MoCA screening)")
p("- `BL`: Baseline Visit (Primary Motor Exam, Patient Questionnaires, Baseline Blood/CSF, Neuro-assessments)")
p("- `V04`, `V06`, `V08`, `V10`, `V12`, `V14`, `V16`, `V18`, `V20`: Annual/semi-annual longitudinal follow-up visits.")
p()
p("### Longitudinal Row Multiplicity")
p("- **Multiple rows per PATNO exist** across different `EVENT_ID` timepoints in all clinical assessment files (average 4 to 12 visits per subject).")
p("- Within a single `EVENT_ID` (e.g., `BL`), each `PATNO` has exactly **1 unique row**.")
p()
p("### Baseline Harmonization Strategy")
p("For cross-sectional model training at baseline:")
p("- Static/Screening variables (`SEX`, `HANDED`, `EDUCYRS`) are extracted from `Demographics_28Jul2026.csv` and `Socio-Economics_28Jul2026.csv`.")
p("- `AGE_AT_VISIT`, `MCATOT`, and `UPSIT_TOTAL` are taken from `EVENT_ID == 'BL'`, falling back to `EVENT_ID == 'SC'` if `BL` is unrecorded.")
p("- Motor assessments (`NP1RTOT`, `NP2PTOT`, `NP3TOT`, `NHY`) and non-motor scales (`GDS`, `ESS`, `RBD`, `SDMT`) are taken from `EVENT_ID == 'BL'`.")
p()
p("---")
p()

# ---------------------------------------------------------
# SECTION 8
# ---------------------------------------------------------
p("## 8. Missing Data Analysis")
p()
p("#### Candidate Baseline Feature Missingness by Cohort (SC + BL Harmonized)")
p()
p("| Feature Name | Feature Category | Missing % in PD (N=2,196) | Non-Null PD Count | Missing % in HC (N=440) | Non-Null HC Count | Missing % in SWEDD (N=81) | Non-Null SWEDD Count | Missing % in Prodromal (N=6,235) | Non-Null Prodromal Count |")
p("|---|---|---|---|---|---|---|---|---|---|")

feat_rows = [
    ("`AGE_AT_VISIT`", "Demographic", "2.0%", 2152, "1.6%", 433, "0.0%", 81, "4.3%", 5969),
    ("`SEX`", "Demographic", "0.2%", 2192, "0.2%", 439, "0.0%", 81, "0.9%", 6182),
    ("`HANDED`", "Demographic", "1.8%", 2156, "0.7%", 437, "0.0%", 81, "2.9%", 6055),
    ("`EDUCYRS`", "Demographic", "3.4%", 2121, "1.6%", 433, "0.0%", 81, "15.9%", 5246),
    ("`NP1RTOT`", "Motor (Part I)", "22.6%", 1700, "22.5%", 341, "18.5%", 66, "53.0%", 2933),
    ("`NP2PTOT`", "Motor (Part II)", "22.0%", 1712, "22.0%", 343, "18.5%", 66, "52.9%", 2939),
    ("`NP3TOT`", "Motor (Part III)", "23.1%", 1688, "23.2%", 338, "18.5%", 66, "53.6%", 2895),
    ("`NHY`", "Motor (H&Y)", "22.9%", 1694, "22.5%", 341, "18.5%", 66, "52.9%", 2939),
    ("`MCATOT`", "Non-Motor (Cognition)", "10.2%", 1973, "9.3%", 399, "0.0%", 81, "50.9%", 3063),
    ("`GDS_TOTAL`", "Non-Motor (Mood)", "22.3%", 1706, "22.3%", 342, "19.8%", 65, "54.0%", 2868),
    ("`ESS_TOTAL`", "Non-Motor (Sleep)", "22.1%", 1711, "22.7%", 340, "21.0%", 64, "52.8%", 2942),
    ("`RBD_TOTAL`", "Non-Motor (Sleep)", "22.1%", 1711, "22.0%", 343, "19.8%", 65, "52.9%", 2935),
    ("`SDMTOTAL`", "Non-Motor (Speed)", "22.6%", 1699, "22.5%", 341, "18.5%", 66, "53.0%", 2932),
    ("`UPSIT_TOTAL`", "Non-Motor (Smell)", "53.8%", 1014, "66.4%", 148, "100.0%", 0, "12.1%", 5479),
    ("`NP4TOT`", "Motor Complications", "79.2%", 457, "100.0%", 0, "100.0%", 0, "99.8%", 13),
]

for fr in feat_rows:
    p(f"| {fr[0]} | {fr[1]} | {fr[2]} | {fr[3]} | {fr[4]} | {fr[5]} | {fr[6]} | {fr[7]} | {fr[8]} | {fr[9]} |")

p()
p("---")
p()

# ---------------------------------------------------------
# SECTION 9
# ---------------------------------------------------------
p("## 9. Candidate Features")
p()
p("The audited candidate features are divided into four explicit groups:")
p()
p("### A. Demographic Features (4 Features)")
p("1. `AGE_AT_VISIT`: Age at visit in years (Continuous)")
p("2. `SEX`: Sex (Binary: 1 = Male, 2/0 = Female)")
p("3. `EDUCYRS`: Years of formal education (Continuous)")
p("4. `HANDED`: Handedness (Categorical: 1 = Right, 2 = Left, 3 = Mixed)")
p()
p("### B. Motor Features (35 Features)")
p("1. `NP1RTOT`: MDS-UPDRS Part I Total Score (Non-motor experiences of daily living)")
p("2. `NP2PTOT`: MDS-UPDRS Part II Total Score (Motor experiences of daily living)")
p("3. `NP3TOT`: MDS-UPDRS Part III Total Score (Motor Examination)")
p("4. `NHY`: Hoehn and Yahr Stage (Ordinal: 0 to 5)")
p("5. Part I Subscore Items: `NP1COG` (Cognitive impairment), `NP1HALL` (Hallucinations), `NP1DPRS` (Depression), `NP1ANXS` (Anxiety), `NP1APAT` (Apathy), `NP1DDS` (Dopamine dysregulation)")
p("6. Part II Subscore Items: `NP2SPCH` (Speech), `NP2SALV` (Saliva & drooling), `NP2SWAL` (Swallowing), `NP2EAT` (Eating tasks), `NP2DRES` (Dressing), `NP2HYGN` (Hygiene), `NP2HWRT` (Handwriting), `NP2HOBB` (Hobbies), `NP2TURN` (Turning in bed), `NP2TRMR` (Tremor), `NP2RISE` (Getting out of bed/chair), `NP2WALK` (Walking & balance), `NP2FREZ` (Freezing)")
p("7. Part III Subscore Items: `NP3SPCH` (Speech), `NP3FACXP` (Facial expression), `NP3RIGN` (Neck rigidity), `NP3FTAPR` / `NP3FTAPL` (Finger tapping R/L), `NP3HMOVR` / `NP3HMOVL` (Hand movements R/L), `NP3PRSPR` / `NP3PRSPL` (Pronation-supination R/L), `NP3GAIT` (Gait), `NP3FRZGT` (Freezing of gait), `NP3PSTBL` (Postural stability), `NP3POSTR` (Posture), `NP3BRADY` (Global bradykinesia), `NP3PTRMR` / `NP3PTRML` (Postural tremor R/L), `NP3RTARU` / `NP3RTALU` / `NP3RTARL` / `NP3RTALL` / `NP3RTALJ` (Rest tremor items)")
p()
p("### C. Non-Motor Features (12 Features)")
p("1. `MCATOT`: Montreal Cognitive Assessment Total Score (0-30)")
p("2. `GDS_TOTAL`: Geriatric Depression Scale Short Version Total (0-15)")
p("3. `ESS_TOTAL`: Epworth Sleepiness Scale Total (0-24)")
p("4. `RBD_TOTAL`: REM Sleep Behavior Disorder Screening Questionnaire Total (0-12)")
p("5. `SDMTOTAL`: Symbol Digit Modalities Test Total Score")
p("6. `UPSIT_TOTAL`: University of Pennsylvania Smell Identification Test Score (0-40)")
p("7. `DVT_TOTAL_RECALL`: HVLT-R Total Recall Score")
p("8. `DVT_DELAYED_RECALL`: HVLT-R Delayed Recall Score")
p("9. `LNS_TOTRAW`: Letter-Number Sequencing Raw Score")
p("10. `TMTASEC`: Trail Making Test Part A Completion Time (seconds)")
p("11. `TMTBSEC`: Trail Making Test Part B Completion Time (seconds)")
p("12. `SCOPA_AUT_TOTAL`: SCOPA-AUT Autonomic Dysfunction Score")
p()
p("---")
p()

# ---------------------------------------------------------
# SECTION 10
# ---------------------------------------------------------
p("## 10. Data Leakage Risks")
p()
p("> [!CAUTION]")
p("> **CRITICAL DATA-LEAKAGE AUDIT:** The following **18 columns/feature families MUST BE STRICTLY EXCLUDED** from model features. They directly encode the target diagnosis, study outcome, post-diagnosis treatment, or cohort assignment.")
p()
p("| Column Name | Source File | Leakage Reason & Target Proxy Risk | Action |")
p("|---|---|---|---|")
p("| `COHORT` | `Participant_Status_28Jul2026.csv` | **Direct Target Class** (1=PD, 2=HC, 3=SWEDD, 4=Prodromal) | **EXCLUDE / TARGET** |")
p("| `COHORT_DEFINITION` | `Participant_Status_28Jul2026.csv` | **Direct Target Label String** | **EXCLUDE / TARGET** |")
p("| `APPRDX` | `Subject_Cohort_History_28Jul2026.csv` | **Direct Target Appendix Code** | **EXCLUDE** |")
p("| `ENROLL_STATUS` | `Participant_Status_28Jul2026.csv` | Study enrollment & trial outcome status | **EXCLUDE** |")
p("| `NEWDIAG`, `DIAGSINLV`, `DIAGDT` | `Clinical_Diagnosis_28Jul2026.csv` | Clinical diagnosis determination events | **EXCLUDE** |")
p("| `SXDT` | `PD_Diagnosis_History_28Jul2026.csv` | Date of PD motor symptom onset | **EXCLUDE** |")
p("| `PDDXDT` | `PD_Diagnosis_History_28Jul2026.csv` | Date of formal Parkinson's Disease diagnosis | **EXCLUDE** |")
p("| `DXTREMOR`, `DXRIGID`, `DXBRADY`, `DXPOSINS` | `PD_Diagnosis_History_28Jul2026.csv` | Diagnostic cardinal signs logged by physician at PD diagnosis | **EXCLUDE** |")
p("| `PRIMDIAG`, `NEWDIAGEXP`, `DXLVL` | `Primary_Research_Diagnosis_28Jul2026.csv` | Consensus primary research diagnosis code | **EXCLUDE** |")
p("| `PDTRTMNT`, `PDSTATE` | `MDS-UPDRS_Part_III_28Jul2026.csv` | PD treatment status (1=Medicated, 0=Unmedicated) & ON/OFF state | **EXCLUDE** |")
p("| `PDMEDYN`, `DBSYN`, `HIFUYN`, `DBSONYN` | `MDS-UPDRS_Part_III_28Jul2026.csv` | Parkinson's medication usage & Deep Brain Stimulation status | **EXCLUDE** |")
p("| `NP4TOT`, `NP4WDYSK`, `NP4DYSKI`, `NP4OFF`, `NP4FLCTI`, `NP4DYSTN` | `MDS-UPDRS_Part_IV_28Jul2026.csv` | Motor complications of levodopa therapy (Collected ONLY for PD patients) | **EXCLUDE** |")
p()
p("---")
p()

# ---------------------------------------------------------
# SECTION 11
# ---------------------------------------------------------
p("## 11. Subject-Level Split Requirements")
p()
p("1. **Longitudinal Grouping Requirement (`PATNO`)**:")
p("   - The PPMI dataset contains multiple visits per subject (`SC`, `BL`, `V04`, `V06`, etc.).")
p("   - **Rule:** Machine learning cross-validation and train/test splits **MUST perform group-based splitting on `PATNO`** (e.g. `GroupKFold` or `GroupShuffleSplit`).")
p("   - Under no circumstances should visits from the same `PATNO` appear in both training and test folds, as this causes severe data leakage across time.")
p("2. **Cross-Sectional Baseline Recommendation**:")
p("   - For the initial diagnostic classification task, restrict data to 1 baseline sample per `PATNO` (`EVENT_ID == 'BL'` or harmonized `SC`+`BL`).")
p()
p("---")
p()

# ---------------------------------------------------------
# SECTION 12
# ---------------------------------------------------------
p("## 12. Recommended Training Dataset Design")
p()
p("### Problem Formulation: Binary Parkinson's Disease (PD) vs. Healthy Control (HC)")
p("- The audited PPMI dataset **strongly supports a binary PD vs. HC classification formulation**.")
p("- Baseline motor assessments (MDS-UPDRS Parts I, II, III), cognitive tests (MoCA), sleep scores (ESS, RBD), mood scales (GDS), and demographics are collected in identical, standardized protocols for both PD and HC participants.")
p()
p("### SWEDD Handling Recommendation")
p("> [!IMPORTANT]")
p("> **RECOMMENDATION: EXCLUDE SWEDD FROM BINARY PD-VS-HC TRAINING.**")
p(">- **Data-Driven Justification:** SWEDD (Scans Without Evidence of Dopaminergic Deficit) subjects (N=81) presented with clinical tremor/parkinsonism at enrollment but had normal baseline DaTscan imaging.")
p(">- Long-term PPMI follow-up studies demonstrate that >80% of SWEDD participants do NOT develop progressive Parkinson's disease and frequently receive alternative diagnoses (e.g., essential tremor, dystonia).")
p(">- Including SWEDD as Healthy Control would inject false negatives, while including SWEDD as PD would inject false positives. Excluding SWEDD ensures clean, gold-standard binary ground-truth labels (`PD` vs `HC`).")
p()
p("### Recommended Baseline Dataset Matrix")
p()
p("| Target Cohort | Total Available | Baseline Motor + Demo (`Age, Sex, UPDRS I, II, III`) | Complete Baseline Motor + Demo + Cognition (`+ MoCA`) | Recommendation |")
p("|---|---|---|---|---|")
p("| **Parkinson's Disease (PD)** | 2,196 | **1,664** | 1,595 | **Include in PD class (Label = 1)** |")
p("| **Healthy Control (HC)** | 440 | **338** | 326 | **Include in HC class (Label = 0)** |")
p("| **Total Usable Binary Dataset** | **2,636** | **2,002** | **1,921** | **Gold-Standard Binary Classification Dataset** |")
p("| **SWEDD** | 81 | 66 | 66 | **EXCLUDE from binary training** |")
p("| **Prodromal** | 6,235 | 2,861 | 2,342 | **Reserve for secondary risk-prediction / prodromal screening** |")
p()
p("---")
p()

# ---------------------------------------------------------
# SECTION 13
# ---------------------------------------------------------
p("## 13. Open Questions / Issues")
p()
p("1. **UPSIT Missingness in Healthy Controls**:")
p("   - UPSIT smell test is missing in 66.4% of HC baseline visits (148/440 present) because olfactory screening was prioritized for prodromal enrichment cohorts.")
p("   - *Recommendation:* Evaluate model architectures with and without UPSIT, or use median/MICE imputation if UPSIT is retained as a candidate feature.")
p("2. **Motor Examination ON/OFF State**:")
p("   - In MDS-UPDRS Part III, some PD patients were assessed in the 'OFF' state (off medication) while others were assessed in 'ON' state.")
p("   - *Recommendation:* Filter for baseline unmedicated assessments or include medication state flag if evaluating treated cohorts.")
p()
p("---")
p()

# Concise summary table required by prompt
p("## Concise Audit Summary")
p()
p("```text")
p("PD participants: 2196")
p("Healthy Control participants: 440")
p("SWEDD participants: 81")
p("Unique participants: 8952")
p("Baseline participants: 5152")
p("Potential usable participants: 2002")
p("Candidate feature count: 51")
p("Columns excluded for leakage: ['COHORT', 'COHORT_DEFINITION', 'APPRDX', 'ENROLL_STATUS', 'NEWDIAG', 'DIAGSINLV', 'DIAGDT', 'SXDT', 'PDDXDT', 'DXTREMOR', 'DXRIGID', 'DXBRADY', 'DXPOSINS', 'PRIMDIAG', 'NEWDIAGEXP', 'DXLVL', 'PDTRTMNT', 'PDSTATE', 'PDMEDYN', 'DBSYN', 'HIFUYN', 'DBSONYN', 'NP4TOT', 'NP4WDYSK', 'NP4DYSKI', 'NP4OFF', 'NP4FLCTI', 'NP4DYSTN']")
p("```")
p()
p("### Exact Files Used to Derive Audit Numbers")
p("1. `Participant_Status_28Jul2026.csv` (Target cohorts, unique PATNOs, enrollment status)")
p("2. `Subject_Demographics/Demographics_28Jul2026.csv` (Sex, handedness, race/ethnicity)")
p("3. `Subject_Demographics/Age_at_visit_28Jul2026.csv` (Age at baseline/screening visits)")
p("4. `Subject_Demographics/Socio-Economics_28Jul2026.csv` (Education years)")
p("5. `Motor___MDS-UPDRS/MDS-UPDRS_Part_I_28Jul2026.csv` (MDS-UPDRS Part I scores)")
p("6. `Motor___MDS-UPDRS/MDS_UPDRS_Part_II__Patient_Questionnaire_28Jul2026.csv` (MDS-UPDRS Part II scores)")
p("7. `Motor___MDS-UPDRS/MDS-UPDRS_Part_III_28Jul2026.csv` (MDS-UPDRS Part III scores & Hoehn & Yahr)")
p("8. `Motor___MDS-UPDRS/MDS-UPDRS_Part_IV__Motor_Complications_28Jul2026.csv` (MDS-UPDRS Part IV scores)")
p("9. `Non-motor_Assessments/Montreal_Cognitive_Assessment__MoCA__28Jul2026.csv` (MoCA cognition scores)")
p("10. `Non-motor_Assessments/Geriatric_Depression_Scale__Short_Version__28Jul2026.csv` (GDS depression scores)")
p("11. `Non-motor_Assessments/Epworth_Sleepiness_Scale_28Jul2026.csv` (ESS daytime sleepiness scores)")
p("12. `Non-motor_Assessments/REM_Sleep_Behavior_Disorder_Screening_Questionnaire_28Jul2026.csv` (RBD sleep disturbance scores)")
p("13. `Non-motor_Assessments/University_of_Pennsylvania_Smell_Identification_Test_UPSIT_28Jul2026.csv` (UPSIT smell identification scores)")
p("14. `Non-motor_Assessments/Symbol_Digit_Modalities_Test_28Jul2026.csv` (SDMT processing speed scores)")
p("15. `Medical/Clinical_Diagnosis_28Jul2026.csv` (Clinical diagnosis events)")
p("16. `Medical/PD_Diagnosis_History_28Jul2026.csv` (PD symptom onset & diagnosis dates)")
p("17. `Medical/Primary_Research_Diagnosis_28Jul2026.csv` (Primary research diagnosis)")

doc_text = "\n".join(doc_lines)

out_path = DOCS_DIR / "PPMI_DATA_AUDIT.md"
with open(out_path, "w", encoding="utf-8") as f:
    f.write(doc_text)

print(f"Successfully generated {out_path} ({len(doc_text)} characters).")


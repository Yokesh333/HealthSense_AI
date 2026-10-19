# PPMI Dataset Audit

> **Audit Date:** September 2026
> **Dataset Path:** `Datasets/PPMI`
> **Scope:** Read-Only Audit of Parkinson's Progression Markers Initiative (PPMI) Data Files

---

## 1. Dataset Inventory

A recursive scan of `Datasets/PPMI/` identified **52 total CSV data files** across 9 subdirectories and root level. Every file contains a `PATNO` subject identifier column (or equivalent) for cross-dataset merging.

| # | Filename | Relative Path | Rows | Cols | Subject Key | Visit Key | Date Columns | Key Columns & Notes |
|---|---|---|---|---|---|---|---|---|
| 1 | `Family_History_28Jul2026.csv` | `Family_History_28Jul2026.csv` | 8,791 | 43 | `PATNO` | `EVENT_ID` | `INFODT, LAST_UPDATE` | PATNO, EVENT_ID |
| 2 | `FS7_APARC_CTH_28Jul2026.csv` | `FS7_APARC_CTH_28Jul2026.csv` | 1,716 | 72 | `PATNO` | `EVENT_ID` | `None` | PATNO, EVENT_ID, lh_bankssts, lh_caudalanteriorcingulate |
| 3 | `FS7_APARC_SA_28Jul2026.csv` | `FS7_APARC_SA_28Jul2026.csv` | 1,716 | 72 | `PATNO` | `EVENT_ID` | `None` | PATNO, EVENT_ID, lh_bankssts, lh_caudalanteriorcingulate |
| 4 | `FS7_ASEG_VOL_28Jul2026.csv` | `FS7_ASEG_VOL_28Jul2026.csv` | 1,713 | 66 | `PATNO` | `EVENT_ID` | `EstimatedTotalIntraCranialVol, Right_Caudate, Left_Caudate` | PATNO, EVENT_ID, Left_WM_hypointensities, Brain_Stem |
| 5 | `Grey_Matter_Volume_28Jul2026.csv` | `Grey_Matter_Volume_28Jul2026.csv` | 363 | 6 | `PATNO` | `EVENT_ID` | `MRIDATE, update_stamp` | PATNO, EVENT_ID, IMAGEID, MRIDATE |
| 6 | `FS7_APARC_CTH_28Jul2026.csv` | `Imaging/FS7_APARC_CTH_28Jul2026.csv` | 1,716 | 72 | `PATNO` | `EVENT_ID` | `None` | PATNO, EVENT_ID, lh_bankssts, lh_caudalanteriorcingulate |
| 7 | `FS7_APARC_SA_28Jul2026.csv` | `Imaging/FS7_APARC_SA_28Jul2026.csv` | 1,716 | 72 | `PATNO` | `EVENT_ID` | `None` | PATNO, EVENT_ID, lh_bankssts, lh_caudalanteriorcingulate |
| 8 | `FS7_ASEG_VOL_28Jul2026.csv` | `Imaging/FS7_ASEG_VOL_28Jul2026.csv` | 1,713 | 66 | `PATNO` | `EVENT_ID` | `EstimatedTotalIntraCranialVol, Right_Caudate, Left_Caudate` | PATNO, EVENT_ID, Left_WM_hypointensities, Brain_Stem |
| 9 | `Grey_Matter_Volume_28Jul2026.csv` | `Imaging/Grey_Matter_Volume_28Jul2026.csv` | 363 | 6 | `PATNO` | `EVENT_ID` | `MRIDATE, update_stamp` | PATNO, EVENT_ID, IMAGEID, MRIDATE |
| 10 | `Magnetic_Resonance_Imaging__MRI__28Jul2026.csv` | `Imaging/Magnetic_Resonance_Imaging__MRI__28Jul2026.csv` | 12,489 | 13 | `PATNO` | `EVENT_ID` | `INFODT, MRIWDTI, LAST_UPDATE` | PATNO, EVENT_ID |
| 11 | `MRIQC_28Jul2026.csv` | `Imaging/MRIQC_28Jul2026.csv` | 1,740 | 58 | `PATNO` | `EVENT_ID` | `None` | PATNO, EVENT_ID, cjv, cnr |
| 12 | `Xing_Core_Lab_-_MRI_acquisition_metadata_28Jul2026.csv` | `Imaging/Xing_Core_Lab_-_MRI_acquisition_metadata_28Jul2026.csv` | 8,195 | 10 | `PATNO` | `EVENT_ID` | `MRI_SCAN_DATE, MRI_SEQ_DTI` | PROTOCOL, PATNO, EVENT_ID, MRI_SCAN_DATE |
| 13 | `Magnetic_Resonance_Imaging__MRI__28Jul2026.csv` | `Magnetic_Resonance_Imaging__MRI__28Jul2026.csv` | 12,489 | 13 | `PATNO` | `EVENT_ID` | `INFODT, MRIWDTI, LAST_UPDATE` | PATNO, EVENT_ID |
| 14 | `Clinical_Diagnosis_28Jul2026.csv` | `Medical/Clinical_Diagnosis_28Jul2026.csv` | 17,579 | 11 | `PATNO` | `EVENT_ID` | `INFODT, DIAGDT, LAST_UPDATE` | PATNO, EVENT_ID |
| 15 | `PD_Diagnosis_History_28Jul2026.csv` | `Medical/PD_Diagnosis_History_28Jul2026.csv` | 2,192 | 15 | `PATNO` | `EVENT_ID` | `INFODT, SXDT, PDDXDT` | PATNO, EVENT_ID |
| 16 | `Primary_Research_Diagnosis_28Jul2026.csv` | `Medical/Primary_Research_Diagnosis_28Jul2026.csv` | 29,552 | 11 | `PATNO` | `EVENT_ID` | `INFODT, LAST_UPDATE` | PATNO, EVENT_ID |
| 17 | `MDS-UPDRS_Part_I_28Jul2026.csv` | `Motor___MDS-UPDRS/MDS-UPDRS_Part_I_28Jul2026.csv` | 33,045 | 15 | `PATNO` | `EVENT_ID` | `INFODT, LAST_UPDATE` | PATNO, EVENT_ID |
| 18 | `MDS-UPDRS_Part_III_28Jul2026.csv` | `Motor___MDS-UPDRS/MDS-UPDRS_Part_III_28Jul2026.csv` | 38,980 | 65 | `PATNO` | `EVENT_ID` | `INFODT, PDTRTMNT, PDMEDDT` | PATNO, EVENT_ID |
| 19 | `MDS-UPDRS_Part_IV__Motor_Complications_28Jul2026.csv` | `Motor___MDS-UPDRS/MDS-UPDRS_Part_IV__Motor_Complications_28Jul2026.csv` | 11,106 | 23 | `PATNO` | `EVENT_ID` | `INFODT, LAST_UPDATE` | PATNO, EVENT_ID |
| 20 | `MDS_UPDRS_Part_II__Patient_Questionnaire_28Jul2026.csv` | `Motor___MDS-UPDRS/MDS_UPDRS_Part_II__Patient_Questionnaire_28Jul2026.csv` | 37,327 | 22 | `PATNO` | `EVENT_ID` | `INFODT, LAST_UPDATE` | PATNO, EVENT_ID |
| 21 | `MRIQC_28Jul2026.csv` | `MRIQC_28Jul2026.csv` | 1,740 | 58 | `PATNO` | `EVENT_ID` | `None` | PATNO, EVENT_ID, cjv, cnr |
| 22 | `Clock_Drawing_28Jul2026.csv` | `Non-motor_Assessments/Clock_Drawing_28Jul2026.csv` | 13,230 | 18 | `PATNO` | `EVENT_ID` | `INFODT, LAST_UPDATE` | PATNO, EVENT_ID |
| 23 | `Cognitive_Change_28Jul2026.csv` | `Non-motor_Assessments/Cognitive_Change_28Jul2026.csv` | 14,842 | 8 | `PATNO` | `EVENT_ID` | `INFODT, LAST_UPDATE` | PATNO, EVENT_ID |
| 24 | `Epworth_Sleepiness_Scale_28Jul2026.csv` | `Non-motor_Assessments/Epworth_Sleepiness_Scale_28Jul2026.csv` | 21,469 | 16 | `PATNO` | `EVENT_ID` | `INFODT, LAST_UPDATE` | PATNO, EVENT_ID |
| 25 | `Geriatric_Depression_Scale__Short_Version__28Jul2026.csv` | `Non-motor_Assessments/Geriatric_Depression_Scale__Short_Version__28Jul2026.csv` | 21,742 | 22 | `PATNO` | `EVENT_ID` | `INFODT, LAST_UPDATE` | PATNO, EVENT_ID |
| 26 | `Hopkins_Verbal_Learning_Test_-_Revised_28Jul2026.csv` | `Non-motor_Assessments/Hopkins_Verbal_Learning_Test_-_Revised_28Jul2026.csv` | 19,423 | 20 | `PATNO` | `EVENT_ID` | `INFODT, LAST_UPDATE` | PATNO, EVENT_ID |
| 27 | `Letter_-_Number_Sequencing_28Jul2026.csv` | `Non-motor_Assessments/Letter_-_Number_Sequencing_28Jul2026.csv` | 19,373 | 31 | `PATNO` | `EVENT_ID` | `INFODT, LAST_UPDATE` | PATNO, EVENT_ID |
| 28 | `Lexical_Fluency_28Jul2026.csv` | `Non-motor_Assessments/Lexical_Fluency_28Jul2026.csv` | 12,897 | 13 | `PATNO` | `EVENT_ID` | `INFODT, LAST_UPDATE` | PATNO, EVENT_ID |
| 29 | `Modified_Boston_Naming_Test_28Jul2026.csv` | `Non-motor_Assessments/Modified_Boston_Naming_Test_28Jul2026.csv` | 12,626 | 13 | `PATNO` | `EVENT_ID` | `INFODT, LAST_UPDATE` | PATNO, EVENT_ID |
| 30 | `Modified_Semantic_Fluency_28Jul2026.csv` | `Non-motor_Assessments/Modified_Semantic_Fluency_28Jul2026.csv` | 19,427 | 13 | `PATNO` | `EVENT_ID` | `INFODT, LAST_UPDATE` | PATNO, EVENT_ID |
| 31 | `Montreal_Cognitive_Assessment__MoCA__28Jul2026.csv` | `Non-motor_Assessments/Montreal_Cognitive_Assessment__MoCA__28Jul2026.csv` | 20,243 | 35 | `PATNO` | `EVENT_ID` | `INFODT, MCADATE, MCAYR` | PATNO, EVENT_ID |
| 32 | `Neuro_QoL__Cognition_Function_-_Short_Form_28Jul2026.csv` | `Non-motor_Assessments/Neuro_QoL__Cognition_Function_-_Short_Form_28Jul2026.csv` | 13,646 | 11 | `PATNO` | `EVENT_ID` | `INFODT, LAST_UPDATE` | PATNO, EVENT_ID |
| 33 | `PDAQ-27_28Jul2026.csv` | `Non-motor_Assessments/PDAQ-27_28Jul2026.csv` | 5,247 | 34 | `PATNO` | `EVENT_ID` | `INFODT, LAST_UPDATE` | PATNO, EVENT_ID |
| 34 | `QUIP-Current-Short_28Jul2026.csv` | `Non-motor_Assessments/QUIP-Current-Short_28Jul2026.csv` | 21,422 | 21 | `PATNO` | `EVENT_ID` | `INFODT, LAST_UPDATE` | PATNO, EVENT_ID |
| 35 | `REM_Sleep_Behavior_Disorder_Screening_Questionnaire_28Jul2026.csv` | `Non-motor_Assessments/REM_Sleep_Behavior_Disorder_Screening_Questionnaire_28Jul2026.csv` | 21,477 | 29 | `PATNO` | `EVENT_ID` | `INFODT, LAST_UPDATE` | PATNO, EVENT_ID |
| 36 | `SCOPA-AUT_28Jul2026.csv` | `Non-motor_Assessments/SCOPA-AUT_28Jul2026.csv` | 21,447 | 43 | `PATNO` | `EVENT_ID` | `INFODT, SCAU26DT, LAST_UPDATE` | PATNO, EVENT_ID |
| 37 | `State-Trait_Anxiety_Inventory_for_Adults_28Jul2026.csv` | `Non-motor_Assessments/State-Trait_Anxiety_Inventory_for_Adults_28Jul2026.csv` | 21,708 | 47 | `PATNO` | `EVENT_ID` | `INFODT, LAST_UPDATE` | PATNO, EVENT_ID |
| 38 | `Symbol_Digit_Modalities_Test_28Jul2026.csv` | `Non-motor_Assessments/Symbol_Digit_Modalities_Test_28Jul2026.csv` | 19,374 | 12 | `PATNO` | `EVENT_ID` | `INFODT, LAST_UPDATE` | PATNO, EVENT_ID |
| 39 | `Trail_Making_A_and_B_28Jul2026.csv` | `Non-motor_Assessments/Trail_Making_A_and_B_28Jul2026.csv` | 12,845 | 16 | `PATNO` | `EVENT_ID` | `INFODT, LAST_UPDATE` | PATNO, EVENT_ID |
| 40 | `University_of_Pennsylvania_Smell_Identification_Test_UPSIT_28Jul2026.csv` | `Non-motor_Assessments/University_of_Pennsylvania_Smell_Identification_Test_UPSIT_28Jul2026.csv` | 10,434 | 95 | `PATNO` | `EVENT_ID` | `INFODT, LAST_UPDATE` | PATNO, EVENT_ID |
| 41 | `Participant_Status_28Jul2026.csv` | `Participant_Status_28Jul2026.csv` | 8,952 | 35 | `PATNO` | `None` | `ENROLL_DATE, STATUS_DATE, DATELIG` | PATNO, COHORT, COHORT_DEFINITION, ENROLL_DATE |
| 42 | `Baseline_Visit_Start_28Jul2026.csv` | `Study_Enrollment/Baseline_Visit_Start_28Jul2026.csv` | 2,854 | 7 | `PATNO` | `EVENT_ID` | `INFODT, LAST_UPDATE` | PATNO, EVENT_ID |
| 43 | `FOUND_Enrollment_Status_28Jul2026.csv` | `Study_Enrollment/FOUND_Enrollment_Status_28Jul2026.csv` | 3,542 | 12 | `PATNO` | `None` | `FOCONSENTDATE, FOVITALUPDATE, LAST_UPDATE` | PATNO, FOSTATUS, FOCONSENTDATE, FOFOLLOWST |
| 44 | `Visit_Type_28Jul2026.csv` | `Study_Enrollment/Visit_Type_28Jul2026.csv` | 15,330 | 9 | `PATNO` | `EVENT_ID, MODVISIT` | `INFODT, LAST_UPDATE` | PATNO, EVENT_ID |
| 45 | `Age_at_visit_28Jul2026.csv` | `Subject_Demographics/Age_at_visit_28Jul2026.csv` | 49,130 | 3 | `PATNO` | `EVENT_ID, AGE_AT_VISIT` | `None` | PATNO, EVENT_ID, AGE_AT_VISIT |
| 46 | `Cognitive_Activities_Testing_Participant_28Jul2026.csv` | `Subject_Demographics/Cognitive_Activities_Testing_Participant_28Jul2026.csv` | 1,189 | 5 | `PATNO` | `None` | `None` | PATNO, CLIENT, LOE, LANGUAGE |
| 47 | `Demographics_28Jul2026.csv` | `Subject_Demographics/Demographics_28Jul2026.csv` | 8,896 | 29 | `PATNO` | `EVENT_ID` | `INFODT, BIRTHDT, LAST_UPDATE` | PATNO, EVENT_ID |
| 48 | `Race_and_Ethnicity_Question_in_myPPMI_28Jul2026.csv` | `Subject_Demographics/Race_and_Ethnicity_Question_in_myPPMI_28Jul2026.csv` | 11,455 | 15 | `PATNO` | `EVENT_ID` | `None` | PATNO, EVENT_ID, MODIFIED_AT, CREATED_AT |
| 49 | `Socio-Economics_28Jul2026.csv` | `Subject_Demographics/Socio-Economics_28Jul2026.csv` | 8,803 | 11 | `PATNO` | `EVENT_ID` | `INFODT, EDUCYRS, EDUCYRS_EQUIV` | PATNO, EVENT_ID |
| 50 | `ST-Direct_Demographics_28Jul2026.csv` | `Subject_Demographics/ST-Direct_Demographics_28Jul2026.csv` | 11,536 | 13 | `PATNO` | `None` | `None` | PATNO, AFICBERB, ASHKJEW, BASQUE |
| 51 | `Subject_Cohort_History_28Jul2026.csv` | `Subject_Demographics/Subject_Cohort_History_28Jul2026.csv` | 935 | 3 | `PATNO` | `None` | `None` | PATNO, APPRDX, COHORT |
| 52 | `Xing_Core_Lab_-_MRI_acquisition_metadata_28Jul2026.csv` | `Xing_Core_Lab_-_MRI_acquisition_metadata_28Jul2026.csv` | 8,195 | 10 | `PATNO` | `EVENT_ID` | `MRI_SCAN_DATE, MRI_SEQ_DTI` | PROTOCOL, PATNO, EVENT_ID, MRI_SCAN_DATE |

---

## 2. Participant Status / Target Analysis

### Cohort & Target Identification
Target diagnosis and study cohort classifications are contained in `Participant_Status_28Jul2026.csv` (located at root and mirrored in subfolders).

- **Primary Cohort Column:** `COHORT` (numeric) and `COHORT_DEFINITION` (string label).
- **Total Unique Participants:** **8,952 unique PATNOs**.

#### Target Distribution Across All Recorded Participants

| Cohort Code | Cohort Name (`COHORT_DEFINITION`) | Participant Count | % of Total Dataset | Clinical Definition |
|---|---|---|---|---|
| `1` | **Parkinson's Disease (PD)** | **2,196** | 24.53% | Diagnosed early, unmedicated or medicated PD subjects |
| `2` | **Healthy Control (HC)** | **440** | 4.92% | Age-matched control subjects with no neurological disease |
| `3` | **SWEDD** | **81** | 0.91% | Scans Without Evidence of Dopaminergic Deficit |
| `4` | **Prodromal** | **6,235** | 69.65% | Subjects with REM sleep behavior disorder, hyposmia, or genetic risks |
| **Total** | | **8,952** | **100.0%** | |

#### Enrollment Status Breakdown (`ENROLL_STATUS`)

| Enrollment Status (`ENROLL_STATUS`) | PD Count | HC Count | SWEDD Count | Prodromal Count | Total |
|---|---|---|---|---|---|
| `Baseline` | 12 | 0 | 0 | 21 | **33** |
| `Baseline Withdraw` | 20 | 1 | 0 | 31 | **52** |
| `Complete` | 34 | 11 | 50 | 6 | **101** |
| `Declined` | 47 | 14 | 14 | 40 | **115** |
| `Enrolled` | 1255 | 225 | 1 | 2646 | **4127** |
| `Excluded` | 76 | 35 | 3 | 157 | **271** |
| `Missing` | 1 | 0 | 0 | 2 | **3** |
| `Pending` | 12 | 0 | 0 | 140 | **152** |
| `Screen Scheduled` | 0 | 0 | 0 | 42 | **42** |
| `Screen failed` | 374 | 55 | 0 | 2756 | **3185** |
| `Screened` | 1 | 0 | 0 | 175 | **176** |
| `Withdraw Deceased` | 57 | 6 | 0 | 23 | **86** |
| `Withdrew` | 307 | 93 | 13 | 196 | **609** |

#### Enrolled / Active Cohort Breakdown (`ENROLL_STATUS` in `['Enrolled', 'Complete', 'Baseline']`)
- **Enrolled PD:** **1,301 participants**
- **Enrolled Healthy Controls:** **236 participants**
- **Enrolled SWEDD:** **51 participants**
- **Enrolled Prodromal:** **2,673 participants**
- **Total Enrolled / Active:** **4,261 participants** (3,185 screen failed, 609 withdrew prior to full study completion)

---

## 3. Demographics

Demographic features are distributed across three primary files in `Subject_Demographics/`:

1. `Demographics_28Jul2026.csv` (8,896 rows, 29 cols):
   - `PATNO`: Subject ID
   - `SEX`: Sex (1 = Male, 2 / 0 = Female)
   - `HANDED`: Handedness (1 = Right, 2 = Left, 3 = Mixed)
   - Race & Ethnicity flags: `HISPLAT` (Hispanic/Latino), `RAWHITE` (White), `RABLACK` (Black/African American), `RAASIAN` (Asian), `RAHAWOPI`, `RAINDALS`
2. `Age_at_visit_28Jul2026.csv` (49,130 rows, 3 cols):
   - `PATNO`: Subject ID
   - `EVENT_ID`: Timepoint (`SC`, `BL`, `V04`, `V06`, etc.)
   - `AGE_AT_VISIT`: Precise age in years at each visit date
3. `Socio-Economics_28Jul2026.csv` (8,803 rows, 11 cols):
   - `PATNO`: Subject ID
   - `EDUCYRS`: Total formal education completed (years)

#### Demographics Coverage & Missingness at Baseline
- **Sex (`SEX`)**: 99.8% non-null across all cohorts (0.2% missing in HC/PD, 0% missing in SWEDD).
- **Age (`AGE_AT_VISIT`)**: Present for 98.0% of PD (2,152/2,196), 98.4% of HC (433/440), and 100% of SWEDD (81/81) when combining `BL` and `SC` visits.
- **Education (`EDUCYRS`)**: Present for 96.6% of PD (2,121/2,196), 98.4% of HC (433/440), and 100% of SWEDD (81/81).
- **Handedness (`HANDED`)**: Present for 98.2% of PD, 99.3% of HC, and 100% of SWEDD.

---

## 4. MDS-UPDRS

Movement Disorder Society Unified Parkinson's Disease Rating Scale (MDS-UPDRS) data is split into 4 dedicated files in `Motor___MDS-UPDRS/`:

| MDS-UPDRS File | Filename | Total Rows | Total Score Col | Key Item-Level Subscores | Baseline Coverage (PD) | Baseline Coverage (HC) |
|---|---|---|---|---|---|---|
| **Part I** | `MDS-UPDRS_Part_I_28Jul2026.csv` | 33,045 | `NP1RTOT` | `NP1COG` (Cognition), `NP1HALL` (Hallucinations), `NP1DPRS` (Depression), `NP1ANXS` (Anxiety), `NP1APAT` (Apathy), `NP1DDS` (Dopamine Dysregulation) | 1,700 (77.4%) | 341 (77.5%) |
| **Part II** | `MDS_UPDRS_Part_II__Patient_Questionnaire_28Jul2026.csv` | 37,327 | `NP2PTOT` | `NP2SPCH` (Speech), `NP2SALV` (Saliva), `NP2SWAL` (Swallowing), `NP2EAT` (Eating), `NP2DRES` (Dressing), `NP2HYGN` (Hygiene), `NP2HWRT` (Handwriting), `NP2HOBB` (Hobbies), `NP2TURN` (Turning), `NP2TRMR` (Tremor), `NP2RISE` (Getting up), `NP2WALK` (Walking), `NP2FREZ` (Freezing) | 1,712 (78.0%) | 343 (78.0%) |
| **Part III** | `MDS-UPDRS_Part_III_28Jul2026.csv` | 38,980 | `NP3TOT` | `NHY` (Hoehn & Yahr), `NP3SPCH` (Speech), `NP3FACXP` (Facial expression), `NP3RIGN` (Rigidity neck), `NP3FTAPR` / `NP3FTAPL` (Finger tapping R/L), `NP3GAIT` (Gait), `NP3BRADY` (Bradykinesia), `NP3PTRMR` / `NP3PTRML` (Postural tremor R/L), `NP3KTRMR` / `NP3KTRML` (Kinetic tremor R/L), `NP3RTARU` / `NP3RTALU` / `NP3RTARL` / `NP3RTALL` / `NP3RTALJ` (Rest tremor items) | 1,688 (76.9%) | 338 (76.8%) |
| **Part IV** | `MDS-UPDRS_Part_IV__Motor_Complications_28Jul2026.csv` | 11,106 | `NP4TOT` | `NP4WDYSK` (Dyskinesias duration), `NP4DYSKI` (Dyskinesia disability), `NP4OFF` (Motor OFF time), `NP4FLCTI` (Motor fluctuations), `NP4DYSTN` (Morning dystonia) | 457 (20.8%) | **0 (0.0%)** |

> [!WARNING]
> **MDS-UPDRS Part IV** assesses motor complications of anti-parkinsonian pharmacotherapy (dyskinesias and motor OFF fluctuations). It is **collected ONLY for PD participants taking dopaminergic medications** and is 100% missing for Healthy Controls. **Part IV MUST NOT be used as a classification feature.**

---

## 5. Non-Motor Assessments

Non-motor symptoms are audited across 19 dedicated assessment CSV files in `Non-motor_Assessments/`:

| Assessment Name | File Basename | Rows | Main Metric Column | Item Breakdown / Subscores | Baseline Availability (PD) | Baseline Availability (HC) |
|---|---|---|---|---|---|---|
| **MoCA** | `Montreal_Cognitive_Assessment__MoCA__28Jul2026.csv` | 20,243 | `MCATOT` | Memory, Executive, Attention, Language, Visuospatial, Orientation | 1,973 (89.8%) | 399 (90.7%) |
| **GDS** | `Geriatric_Depression_Scale__Short_Version__28Jul2026.csv` | 21,742 | `GDS_TOTAL` (Derived sum) | 15 binary items (`GDSSATIS` through `GDSBETER`) | 1,706 (77.7%) | 342 (77.7%) |
| **ESS** | `Epworth_Sleepiness_Scale_28Jul2026.csv` | 21,469 | `ESS_TOTAL` (Derived sum) | 8 daytime sleepiness situations (`ESS1` to `ESS8`) | 1,711 (77.9%) | 340 (77.3%) |
| **RBD** | `REM_Sleep_Behavior_Disorder_Screening_Questionnaire_28Jul2026.csv` | 21,477 | `RBD_TOTAL` (Derived sum) | 12 sleep disturbance items (`DRMVIVID` to `SLPDSTRB`) | 1,711 (77.9%) | 343 (78.0%) |
| **SDMT** | `Symbol_Digit_Modalities_Test_28Jul2026.csv` | 19,374 | `SDMTOTAL` | Symbol-digit substitution total correct | 1,699 (77.4%) | 341 (77.5%) |
| **UPSIT** | `University_of_Pennsylvania_Smell_Identification_Test_UPSIT_28Jul2026.csv` | 10,434 | `UPSIT_TOTAL` (`TOTAL_CORRECT`) | 40-item smell identification test score | 1,014 (46.2%) | 148 (33.6%) |
| **SCOPA-AUT** | `SCOPA-AUT_28Jul2026.csv` | 21,447 | Item sums (`SCAU1`-`SCAU25`) | Autonomic dysfunction (GI, urinary, cardiovascular, pupillomotor) | 1,710 (77.9%) | 342 (77.7%) |
| **STAI** | `State-Trait_Anxiety_Inventory_for_Adults_28Jul2026.csv` | 21,708 | Item sums (`STAIAD1`-`STAIAD40`) | State & Trait Anxiety scores | 1,710 (77.9%) | 341 (77.5%) |
| **QUIP-Short** | `QUIP-Current-Short_28Jul2026.csv` | 21,422 | `TMGAMBLE`, `TMSEX`, `TMBUY`, `TMEAT` | Impulse Control Disorders & Compulsive Behaviors | 1,710 (77.9%) | 341 (77.5%) |
| **HVLT-R** | `Hopkins_Verbal_Learning_Test_-_Revised_28Jul2026.csv` | 19,423 | `DVT_TOTAL_RECALL`, `DVT_DELAYED_RECALL` | Verbal memory recall and recognition | 1,699 (77.4%) | 341 (77.5%) |
| **LNS** | `Letter_-_Number_Sequencing_28Jul2026.csv` | 19,373 | `LNS_TOTRAW` | Working memory score | 1,699 (77.4%) | 341 (77.5%) |
| **TMT A & B** | `Trail_Making_A_and_B_28Jul2026.csv` | 12,845 | `TMTASEC`, `TMTBSEC` | Processing speed & executive cognitive flexibility times | 1,120 (51.0%) | 224 (50.9%) |

---

## 6. Medical / Diagnosis Data

Three clinical files record medical history, diagnostic validation, and symptom onset:

1. `Medical/Clinical_Diagnosis_28Jul2026.csv` (17,579 rows, 11 cols):
   - `NEWDIAG`: Numeric code for newly confirmed diagnosis during follow-up.
   - `DIAGSINLV`: Diagnosis since last visit flag.
   - `DIAGDT`: Date diagnosis established.
2. `Medical/PD_Diagnosis_History_28Jul2026.csv` (2,192 rows, 15 cols):
   - `SXDT`: Date of initial motor symptom onset.
   - `PDDXDT`: Date of initial Parkinson's Disease diagnosis.
   - Cardinal Signs at Diagnosis: `DXTREMOR` (Tremor), `DXRIGID` (Rigidity), `DXBRADY` (Bradykinesia), `DXPOSINS` (Postural instability).
   - `DOMSIDE`: Dominant side affected (1 = Right, 2 = Left, 3 = Symmetric).
3. `Medical/Primary_Research_Diagnosis_28Jul2026.csv` (29,552 rows, 11 cols):
   - `PRIMDIAG`: Primary consensus diagnosis code (1 = Parkinson's Disease, 2 = Healthy Control, 3 = SWEDD, etc.).
   - `DXLVL`: Diagnostic confidence level.

---

## 7. Baseline Visit Analysis

### Timepoint Encoding
Visits are tracked via the `EVENT_ID` column across all longitudinal files:
- `SC`: Screening Visit (Demographics, Initial Diagnostic Screening, UPSIT, MoCA screening)
- `BL`: Baseline Visit (Primary Motor Exam, Patient Questionnaires, Baseline Blood/CSF, Neuro-assessments)
- `V04`, `V06`, `V08`, `V10`, `V12`, `V14`, `V16`, `V18`, `V20`: Annual/semi-annual longitudinal follow-up visits.

### Longitudinal Row Multiplicity
- **Multiple rows per PATNO exist** across different `EVENT_ID` timepoints in all clinical assessment files (average 4 to 12 visits per subject).
- Within a single `EVENT_ID` (e.g., `BL`), each `PATNO` has exactly **1 unique row**.

### Baseline Harmonization Strategy
For cross-sectional model training at baseline:
- Static/Screening variables (`SEX`, `HANDED`, `EDUCYRS`) are extracted from `Demographics_28Jul2026.csv` and `Socio-Economics_28Jul2026.csv`.
- `AGE_AT_VISIT`, `MCATOT`, and `UPSIT_TOTAL` are taken from `EVENT_ID == 'BL'`, falling back to `EVENT_ID == 'SC'` if `BL` is unrecorded.
- Motor assessments (`NP1RTOT`, `NP2PTOT`, `NP3TOT`, `NHY`) and non-motor scales (`GDS`, `ESS`, `RBD`, `SDMT`) are taken from `EVENT_ID == 'BL'`.

---

## 8. Missing Data Analysis

#### Candidate Baseline Feature Missingness by Cohort (SC + BL Harmonized)

| Feature Name | Feature Category | Missing % in PD (N=2,196) | Non-Null PD Count | Missing % in HC (N=440) | Non-Null HC Count | Missing % in SWEDD (N=81) | Non-Null SWEDD Count | Missing % in Prodromal (N=6,235) | Non-Null Prodromal Count |
|---|---|---|---|---|---|---|---|---|---|
| `AGE_AT_VISIT` | Demographic | 2.0% | 2152 | 1.6% | 433 | 0.0% | 81 | 4.3% | 5969 |
| `SEX` | Demographic | 0.2% | 2192 | 0.2% | 439 | 0.0% | 81 | 0.9% | 6182 |
| `HANDED` | Demographic | 1.8% | 2156 | 0.7% | 437 | 0.0% | 81 | 2.9% | 6055 |
| `EDUCYRS` | Demographic | 3.4% | 2121 | 1.6% | 433 | 0.0% | 81 | 15.9% | 5246 |
| `NP1RTOT` | Motor (Part I) | 22.6% | 1700 | 22.5% | 341 | 18.5% | 66 | 53.0% | 2933 |
| `NP2PTOT` | Motor (Part II) | 22.0% | 1712 | 22.0% | 343 | 18.5% | 66 | 52.9% | 2939 |
| `NP3TOT` | Motor (Part III) | 23.1% | 1688 | 23.2% | 338 | 18.5% | 66 | 53.6% | 2895 |
| `NHY` | Motor (H&Y) | 22.9% | 1694 | 22.5% | 341 | 18.5% | 66 | 52.9% | 2939 |
| `MCATOT` | Non-Motor (Cognition) | 10.2% | 1973 | 9.3% | 399 | 0.0% | 81 | 50.9% | 3063 |
| `GDS_TOTAL` | Non-Motor (Mood) | 22.3% | 1706 | 22.3% | 342 | 19.8% | 65 | 54.0% | 2868 |
| `ESS_TOTAL` | Non-Motor (Sleep) | 22.1% | 1711 | 22.7% | 340 | 21.0% | 64 | 52.8% | 2942 |
| `RBD_TOTAL` | Non-Motor (Sleep) | 22.1% | 1711 | 22.0% | 343 | 19.8% | 65 | 52.9% | 2935 |
| `SDMTOTAL` | Non-Motor (Speed) | 22.6% | 1699 | 22.5% | 341 | 18.5% | 66 | 53.0% | 2932 |
| `UPSIT_TOTAL` | Non-Motor (Smell) | 53.8% | 1014 | 66.4% | 148 | 100.0% | 0 | 12.1% | 5479 |
| `NP4TOT` | Motor Complications | 79.2% | 457 | 100.0% | 0 | 100.0% | 0 | 99.8% | 13 |

---

## 9. Candidate Features

The audited candidate features are divided into four explicit groups:

### A. Demographic Features (4 Features)
1. `AGE_AT_VISIT`: Age at visit in years (Continuous)
2. `SEX`: Sex (Binary: 1 = Male, 2/0 = Female)
3. `EDUCYRS`: Years of formal education (Continuous)
4. `HANDED`: Handedness (Categorical: 1 = Right, 2 = Left, 3 = Mixed)

### B. Motor Features (35 Features)
1. `NP1RTOT`: MDS-UPDRS Part I Total Score (Non-motor experiences of daily living)
2. `NP2PTOT`: MDS-UPDRS Part II Total Score (Motor experiences of daily living)
3. `NP3TOT`: MDS-UPDRS Part III Total Score (Motor Examination)
4. `NHY`: Hoehn and Yahr Stage (Ordinal: 0 to 5)
5. Part I Subscore Items: `NP1COG` (Cognitive impairment), `NP1HALL` (Hallucinations), `NP1DPRS` (Depression), `NP1ANXS` (Anxiety), `NP1APAT` (Apathy), `NP1DDS` (Dopamine dysregulation)
6. Part II Subscore Items: `NP2SPCH` (Speech), `NP2SALV` (Saliva & drooling), `NP2SWAL` (Swallowing), `NP2EAT` (Eating tasks), `NP2DRES` (Dressing), `NP2HYGN` (Hygiene), `NP2HWRT` (Handwriting), `NP2HOBB` (Hobbies), `NP2TURN` (Turning in bed), `NP2TRMR` (Tremor), `NP2RISE` (Getting out of bed/chair), `NP2WALK` (Walking & balance), `NP2FREZ` (Freezing)
7. Part III Subscore Items: `NP3SPCH` (Speech), `NP3FACXP` (Facial expression), `NP3RIGN` (Neck rigidity), `NP3FTAPR` / `NP3FTAPL` (Finger tapping R/L), `NP3HMOVR` / `NP3HMOVL` (Hand movements R/L), `NP3PRSPR` / `NP3PRSPL` (Pronation-supination R/L), `NP3GAIT` (Gait), `NP3FRZGT` (Freezing of gait), `NP3PSTBL` (Postural stability), `NP3POSTR` (Posture), `NP3BRADY` (Global bradykinesia), `NP3PTRMR` / `NP3PTRML` (Postural tremor R/L), `NP3RTARU` / `NP3RTALU` / `NP3RTARL` / `NP3RTALL` / `NP3RTALJ` (Rest tremor items)

### C. Non-Motor Features (12 Features)
1. `MCATOT`: Montreal Cognitive Assessment Total Score (0-30)
2. `GDS_TOTAL`: Geriatric Depression Scale Short Version Total (0-15)
3. `ESS_TOTAL`: Epworth Sleepiness Scale Total (0-24)
4. `RBD_TOTAL`: REM Sleep Behavior Disorder Screening Questionnaire Total (0-12)
5. `SDMTOTAL`: Symbol Digit Modalities Test Total Score
6. `UPSIT_TOTAL`: University of Pennsylvania Smell Identification Test Score (0-40)
7. `DVT_TOTAL_RECALL`: HVLT-R Total Recall Score
8. `DVT_DELAYED_RECALL`: HVLT-R Delayed Recall Score
9. `LNS_TOTRAW`: Letter-Number Sequencing Raw Score
10. `TMTASEC`: Trail Making Test Part A Completion Time (seconds)
11. `TMTBSEC`: Trail Making Test Part B Completion Time (seconds)
12. `SCOPA_AUT_TOTAL`: SCOPA-AUT Autonomic Dysfunction Score

---

## 10. Data Leakage Risks

> [!CAUTION]
> **CRITICAL DATA-LEAKAGE AUDIT:** The following **18 columns/feature families MUST BE STRICTLY EXCLUDED** from model features. They directly encode the target diagnosis, study outcome, post-diagnosis treatment, or cohort assignment.

| Column Name | Source File | Leakage Reason & Target Proxy Risk | Action |
|---|---|---|---|
| `COHORT` | `Participant_Status_28Jul2026.csv` | **Direct Target Class** (1=PD, 2=HC, 3=SWEDD, 4=Prodromal) | **EXCLUDE / TARGET** |
| `COHORT_DEFINITION` | `Participant_Status_28Jul2026.csv` | **Direct Target Label String** | **EXCLUDE / TARGET** |
| `APPRDX` | `Subject_Cohort_History_28Jul2026.csv` | **Direct Target Appendix Code** | **EXCLUDE** |
| `ENROLL_STATUS` | `Participant_Status_28Jul2026.csv` | Study enrollment & trial outcome status | **EXCLUDE** |
| `NEWDIAG`, `DIAGSINLV`, `DIAGDT` | `Clinical_Diagnosis_28Jul2026.csv` | Clinical diagnosis determination events | **EXCLUDE** |
| `SXDT` | `PD_Diagnosis_History_28Jul2026.csv` | Date of PD motor symptom onset | **EXCLUDE** |
| `PDDXDT` | `PD_Diagnosis_History_28Jul2026.csv` | Date of formal Parkinson's Disease diagnosis | **EXCLUDE** |
| `DXTREMOR`, `DXRIGID`, `DXBRADY`, `DXPOSINS` | `PD_Diagnosis_History_28Jul2026.csv` | Diagnostic cardinal signs logged by physician at PD diagnosis | **EXCLUDE** |
| `PRIMDIAG`, `NEWDIAGEXP`, `DXLVL` | `Primary_Research_Diagnosis_28Jul2026.csv` | Consensus primary research diagnosis code | **EXCLUDE** |
| `PDTRTMNT`, `PDSTATE` | `MDS-UPDRS_Part_III_28Jul2026.csv` | PD treatment status (1=Medicated, 0=Unmedicated) & ON/OFF state | **EXCLUDE** |
| `PDMEDYN`, `DBSYN`, `HIFUYN`, `DBSONYN` | `MDS-UPDRS_Part_III_28Jul2026.csv` | Parkinson's medication usage & Deep Brain Stimulation status | **EXCLUDE** |
| `NP4TOT`, `NP4WDYSK`, `NP4DYSKI`, `NP4OFF`, `NP4FLCTI`, `NP4DYSTN` | `MDS-UPDRS_Part_IV_28Jul2026.csv` | Motor complications of levodopa therapy (Collected ONLY for PD patients) | **EXCLUDE** |

---

## 11. Subject-Level Split Requirements

1. **Longitudinal Grouping Requirement (`PATNO`)**:
   - The PPMI dataset contains multiple visits per subject (`SC`, `BL`, `V04`, `V06`, etc.).
   - **Rule:** Machine learning cross-validation and train/test splits **MUST perform group-based splitting on `PATNO`** (e.g. `GroupKFold` or `GroupShuffleSplit`).
   - Under no circumstances should visits from the same `PATNO` appear in both training and test folds, as this causes severe data leakage across time.
2. **Cross-Sectional Baseline Recommendation**:
   - For the initial diagnostic classification task, restrict data to 1 baseline sample per `PATNO` (`EVENT_ID == 'BL'` or harmonized `SC`+`BL`).

---

## 12. Recommended Training Dataset Design

### Problem Formulation: Binary Parkinson's Disease (PD) vs. Healthy Control (HC)
- The audited PPMI dataset **strongly supports a binary PD vs. HC classification formulation**.
- Baseline motor assessments (MDS-UPDRS Parts I, II, III), cognitive tests (MoCA), sleep scores (ESS, RBD), mood scales (GDS), and demographics are collected in identical, standardized protocols for both PD and HC participants.

### SWEDD Handling Recommendation
> [!IMPORTANT]
> **RECOMMENDATION: EXCLUDE SWEDD FROM BINARY PD-VS-HC TRAINING.**
>- **Data-Driven Justification:** SWEDD (Scans Without Evidence of Dopaminergic Deficit) subjects (N=81) presented with clinical tremor/parkinsonism at enrollment but had normal baseline DaTscan imaging.
>- Long-term PPMI follow-up studies demonstrate that >80% of SWEDD participants do NOT develop progressive Parkinson's disease and frequently receive alternative diagnoses (e.g., essential tremor, dystonia).
>- Including SWEDD as Healthy Control would inject false negatives, while including SWEDD as PD would inject false positives. Excluding SWEDD ensures clean, gold-standard binary ground-truth labels (`PD` vs `HC`).

### Recommended Baseline Dataset Matrix

| Target Cohort | Total Available | Baseline Motor + Demo (`Age, Sex, UPDRS I, II, III`) | Complete Baseline Motor + Demo + Cognition (`+ MoCA`) | Recommendation |
|---|---|---|---|---|
| **Parkinson's Disease (PD)** | 2,196 | **1,664** | 1,595 | **Include in PD class (Label = 1)** |
| **Healthy Control (HC)** | 440 | **338** | 326 | **Include in HC class (Label = 0)** |
| **Total Usable Binary Dataset** | **2,636** | **2,002** | **1,921** | **Gold-Standard Binary Classification Dataset** |
| **SWEDD** | 81 | 66 | 66 | **EXCLUDE from binary training** |
| **Prodromal** | 6,235 | 2,861 | 2,342 | **Reserve for secondary risk-prediction / prodromal screening** |

---

## 13. Open Questions / Issues

1. **UPSIT Missingness in Healthy Controls**:
   - UPSIT smell test is missing in 66.4% of HC baseline visits (148/440 present) because olfactory screening was prioritized for prodromal enrichment cohorts.
   - *Recommendation:* Evaluate model architectures with and without UPSIT, or use median/MICE imputation if UPSIT is retained as a candidate feature.
2. **Motor Examination ON/OFF State**:
   - In MDS-UPDRS Part III, some PD patients were assessed in the 'OFF' state (off medication) while others were assessed in 'ON' state.
   - *Recommendation:* Filter for baseline unmedicated assessments or include medication state flag if evaluating treated cohorts.

---

## Concise Audit Summary

```text
PD participants: 2196
Healthy Control participants: 440
SWEDD participants: 81
Unique participants: 8952
Baseline participants: 5152
Potential usable participants: 2002
Candidate feature count: 51
Columns excluded for leakage: ['COHORT', 'COHORT_DEFINITION', 'APPRDX', 'ENROLL_STATUS', 'NEWDIAG', 'DIAGSINLV', 'DIAGDT', 'SXDT', 'PDDXDT', 'DXTREMOR', 'DXRIGID', 'DXBRADY', 'DXPOSINS', 'PRIMDIAG', 'NEWDIAGEXP', 'DXLVL', 'PDTRTMNT', 'PDSTATE', 'PDMEDYN', 'DBSYN', 'HIFUYN', 'DBSONYN', 'NP4TOT', 'NP4WDYSK', 'NP4DYSKI', 'NP4OFF', 'NP4FLCTI', 'NP4DYSTN']
```

### Exact Files Used to Derive Audit Numbers
1. `Participant_Status_28Jul2026.csv` (Target cohorts, unique PATNOs, enrollment status)
2. `Subject_Demographics/Demographics_28Jul2026.csv` (Sex, handedness, race/ethnicity)
3. `Subject_Demographics/Age_at_visit_28Jul2026.csv` (Age at baseline/screening visits)
4. `Subject_Demographics/Socio-Economics_28Jul2026.csv` (Education years)
5. `Motor___MDS-UPDRS/MDS-UPDRS_Part_I_28Jul2026.csv` (MDS-UPDRS Part I scores)
6. `Motor___MDS-UPDRS/MDS_UPDRS_Part_II__Patient_Questionnaire_28Jul2026.csv` (MDS-UPDRS Part II scores)
7. `Motor___MDS-UPDRS/MDS-UPDRS_Part_III_28Jul2026.csv` (MDS-UPDRS Part III scores & Hoehn & Yahr)
8. `Motor___MDS-UPDRS/MDS-UPDRS_Part_IV__Motor_Complications_28Jul2026.csv` (MDS-UPDRS Part IV scores)
9. `Non-motor_Assessments/Montreal_Cognitive_Assessment__MoCA__28Jul2026.csv` (MoCA cognition scores)
10. `Non-motor_Assessments/Geriatric_Depression_Scale__Short_Version__28Jul2026.csv` (GDS depression scores)
11. `Non-motor_Assessments/Epworth_Sleepiness_Scale_28Jul2026.csv` (ESS daytime sleepiness scores)
12. `Non-motor_Assessments/REM_Sleep_Behavior_Disorder_Screening_Questionnaire_28Jul2026.csv` (RBD sleep disturbance scores)
13. `Non-motor_Assessments/University_of_Pennsylvania_Smell_Identification_Test_UPSIT_28Jul2026.csv` (UPSIT smell identification scores)
14. `Non-motor_Assessments/Symbol_Digit_Modalities_Test_28Jul2026.csv` (SDMT processing speed scores)
15. `Medical/Clinical_Diagnosis_28Jul2026.csv` (Clinical diagnosis events)
16. `Medical/PD_Diagnosis_History_28Jul2026.csv` (PD symptom onset & diagnosis dates)
17. `Medical/Primary_Research_Diagnosis_28Jul2026.csv` (Primary research diagnosis)
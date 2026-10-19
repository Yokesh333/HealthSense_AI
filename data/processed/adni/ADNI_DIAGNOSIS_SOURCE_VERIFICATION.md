# ADNI Diagnosis Source Verification Report

## 1. All Diagnosis-Related Columns Found
An exhaustive search of all ADNI CSV files was conducted for column names containing `DX`, `DIAGNOSIS`, `STATUS`, `ARM`, or `DIAG`.

| File | Column | Unique Values | Non-null Count | Likely Meaning |
|------|--------|---------------|----------------|----------------|
| `NEUROPATH_28Jul2026.csv` | `NPPDXA` to `NPPDXTX` | Varies (1-43) | Varies | Post-mortem neuropathology (Not baseline) |
| `ARM_28Jul2026.csv` | `ARM` | 11 | 4,703 | Study Arm Assignment |
| `REGISTRY_28Jul2026.csv` | `RGSTATUS` | 1 | 12,009 | Registry/Enrollment Status |
| `REGISTRY_28Jul2026.csv` | `PTSTATUS` | 2 | 11,993 | Patient Screening Status |
| `MAYOADIRL_MRI_QUALITY_ADNI3_28Jul2026.csv` | `STUDY_PROTOCOL_STATUS` | 5 | 28,244 | MRI Scan Protocol Status |
| `MAYOADIRL_MRI_QUALITY_ADNI3_28Jul2026.csv` | `PROTOCOL_STATUS` | 5 | 28,244 | MRI Scan Protocol Status |

## 2. All Candidate Diagnosis Sources
The only variables that could theoretically be linked to patient diagnosis are:
- `PTSTATUS` / `RGSTATUS` (in `REGISTRY.csv`)
- `ARM` (in `ARM.csv`)
- `NPPDXA`-`NPPDXTX` (in `NEUROPATH.csv`)

None of these represent a standard, explicitly defined baseline clinical diagnosis (such as CN vs MCI vs AD).

## 3. ARM Analysis
- **File**: `Enrollment\ARM_28Jul2026.csv`
- **ADNI Phase Coverage**: `ADNI1`, `ADNIGO`, `ADNI2`
- **ARM Unique Values**: 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0.
- **Value Counts**: 
  - 2.0: 1185
  - 1.0: 684
  - 10.0: 618
  - 3.0: 573
  - 5.0: 518
  - 4.0: 272
  - (Others range from 89 to 225)
- **Association**: `PTID`, `RID`
- **Meaning**: `ARM` defines the study enrollment arm (e.g., ADNI1 Normal, ADNI2 EMCI). Because the numbering rules change between ADNI1, ADNIGO, and ADNI2, `ARM = 1` might mean something different depending on the phase. It is an enrollment grouping, not a pure clinical diagnosis label.

## 4. PTSTATUS Analysis
- **File**: `Enrollment\REGISTRY_28Jul2026.csv`
- **Unique Values**: `1.0` (Count: 11,391), `2.0` (Count: 602), `NaN` (Count: 17,431)
- **Conclusion**: NOT A DIAGNOSIS TARGET. This tracks binary patient screening/registry status.

## 5. RGSTATUS Analysis
- **File**: `Enrollment\REGISTRY_28Jul2026.csv`
- **Unique Values**: `1.0` (Count: 12,009), `NaN` (Count: 17,415)
- **Conclusion**: NOT A DIAGNOSIS TARGET. This tracks binary registry status.

## 6. Baseline Diagnosis Availability
NO VALID BASELINE DIAGNOSIS SOURCE FOUND IN CURRENT DATA.

## 7. Demographic Availability
- **Search terms used**: `AGE`, `SEX`, `EDU`, `DOB`, `GENDER`, `RACE`, `ETHNICITY`.
- **Results**: 
  - No baseline patient `AGE` found (only relative ages like `MOTHAGE`, `FATHAGE`, and post-mortem age `NPDAGE`).
  - No patient `SEX` or `GENDER` found (only sibling gender `SIBGENDER`).
  - No `EDUCATION`, `RACE`, or `ETHNICITY` found.
- **Conclusion**: Core patient demographics are entirely missing from the current files.

## 8. Data Leakage Concerns
Using `NEUROPATH.csv` labels as the target would be extreme data leakage (predicting post-mortem pathology instead of baseline diagnosis). Attempting to map `ARM` across multiple ADNI phases without the official dictionary risks mislabeling subjects, which poisons the training data.

## 9. Whether DXSUM_PDXCONV_ADNIALL.csv is Required
**REQUIRED**. This file is mandatory because it contains the official ADNI longitudinal diagnoses (`DXCHANGE`, `DXCURREN`, `DXBL`), which securely label a subject as Cognitively Normal (CN), Mild Cognitive Impairment (MCI), or Alzheimer's Disease (AD) without ambiguous proxy mapping.

## 10. Whether PTDEMO.csv is Required
**REQUIRED**. This file is mandatory because it contains baseline Age, Sex, Education, and Race. These are the most fundamental demographic covariates required for any defensible Alzheimer's predictive model.

## 11. Exact Files We Need to Obtain Before Proceeding
1. `DXSUM_PDXCONV_ADNIALL.csv` (or the equivalent Diagnostic Summary CSV)
2. `PTDEMO.csv` (Patient Demographics)

## 12. Recommended Next Action
Suspend Phase 2 implementation until `DXSUM_PDXCONV_ADNIALL.csv` and `PTDEMO.csv` are downloaded from the ADNI LONI portal and placed into the `Datasets\ADNI` folder. Once added, we will restart the diagnosis verification.

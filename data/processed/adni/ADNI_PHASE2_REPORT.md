# ADNI Phase 2 Data Preparation Report

## 1. Objective
Create a clean, reproducible, subject-level ADNI baseline clinical dataset for Phase 3 machine-learning classification (CN vs MCI vs AD).

## 2. Source Files Inspected
- `ADNIMERGE2/data/DXSUM.rda` (Diagnosis Source)
- `PTDEMOG_31Aug2026.csv` (Demographics)
- `ADAS_28Jul2026.csv`, `CDR_28Jul2026.csv`, `FAQ_28Jul2026.csv`, `MMSE_28Jul2026.csv`, `MOCA_28Jul2026.csv` (Cognitive Tests)

## 3. Dataset Sizes
Initial Baseline DX records: 1,641 (strictly unique subjects).

## 4. Diagnosis Source
The official clinical diagnosis label was extracted from the `DIAGNOSIS` column in `DXSUM.rda`.

## 5. Original Diagnosis Distribution
- MCI: 767
- CN: 608
- Dementia: 266

## 6. CN/MCI/AD Mapping
- CN → CN
- MCI → MCI
- Dementia → AD

> [!WARNING]
> **Dataset Mapping Limitation**: The source data uses the label "Dementia", not strictly "Alzheimer's Disease". For this project, all "Dementia" labels have been explicitly mapped to the `AD` target class.

## 7. Demographic Variables
- `AGE` (Derived from `VISDATE` - `PTDOBYY`)
- `SEX` (Mapped from `PTGENDER`)
- `EDUCATION` (Mapped from `PTEDUCAT`)
- `RACE` (Mapped from `PTRACCAT`)
- `ETHNICITY` (Mapped from `PTETHCAT`)

## 8. Cognitive Variables
- `ADAS` (ADAS-Cog Total Score)
- `MMSE` (Mini-Mental State Exam Score)
- `FAQ` (Functional Assessment Questionnaire Total)
- `CDR` (Clinical Dementia Rating Global)
- `MOCA` (Montreal Cognitive Assessment)

## 9. Medical-History Variables
Excluded. `INITHEALTH` provides uncodified text strings and arbitrary symptom IDs, making them unsuitable for robust structured ML features without a curated dictionary mapping.

## 10. Baseline Definition
Defined strictly as `VISCODE == 'bl'` in `DXSUM`. In `PTDEMOG` and cognitive tests, both `sc` (screening) and `bl` were accepted to find the earliest valid baseline covariate. Missing records were resolved by keeping the chronologically first valid observation per subject (`keep='first'`).

## 11. Merge Strategy
- Started with DX Baseline (1,641 rows).
- Inner join with Demographics on `PTID`.
- Left join with individual cognitive tests on `PTID`.
- Uniqueness asserted before and after merges.

## 12. Duplicate Handling
Duplicate baseline records (if any) were resolved deterministically by sorting by `EXAMDATE` / `VISDATE` in ascending order and taking the first record, enforcing the definition of the earliest baseline.

## 13. Missing-Data Analysis
- `ADAS`: 7 missing
- `CDR`: 0 missing
- `FAQ`: 18 missing
- `MMSE`: 0 missing
- `MOCA`: 966 missing (Expected: MoCA was introduced later in ADNI protocols)
No irreversible imputation was performed. Missingness will be handled natively in Phase 3 ML pipelines.

## 14. Final Feature List
`AGE`, `SEX`, `EDUCATION`, `RACE`, `ETHNICITY`, `ADAS`, `CDR`, `FAQ`, `MMSE`, `MOCA`

## 15. Excluded Leakage Variables
- `VISCODE`, `VISDATE`, `PTDOBYY`, `RID` (Identifiers)
- `DXCHANGE`, `DXCURREN`, `DXBL`, `DXMCI`, `DXAD`, `DXNORM` (Diagnosis Leakage)

## 16. Train/Validation/Test Sizes
- **Train**: 1,147 subjects (70%)
- **Validation**: 245 subjects (15%)
- **Test**: 249 subjects (15%)

## 17. Class Distributions
| Target | Train | Val | Test |
|--------|-------|-----|------|
| MCI    | 536   | 115 | 116  |
| CN     | 425   | 91  | 92   |
| AD     | 186   | 39  | 41   |

## 18. Subject Leakage Validation
`06_validate_adni.py` explicitly tested intersections between Train, Val, and Test splits.
Result: **Zero subject leakage detected. `Train ∩ Val = ∅`, `Train ∩ Test = ∅`, `Val ∩ Test = ∅`.**

## 19. Limitations
- MoCA has a ~58% missing rate due to ADNI study design phases.
- "Dementia" is assumed to be "AD" for modeling purposes.

## 20. Reproducibility Instructions
Run the python scripts in order:
1. `scripts/adni/01_inspect_sources.py`
2. `scripts/adni/02_extract_diagnosis.py`
3. `scripts/adni/03_build_baseline.py`
4. `scripts/adni/04_engineer_features.py`
5. `scripts/adni/05_create_splits.py`
6. `scripts/adni/06_validate_adni.py`

## 21. Final Phase 2 Status
Phase 2 Dataset Preparation and Validation is **COMPLETE**. The output files reside in `data/processed/adni/`.

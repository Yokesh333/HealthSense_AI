# ALTERNATIVE TABULAR DATASET AUDIT

## 1. Audit Strategy
A recursive search was performed across `C:\Users\Yokesh\Desktop\Health_Sense AI\Datasets\` to identify any alternative **tabular/clinical Alzheimer's** datasets that contain demographics (Age, Sex, Education), cognitive measurements, and diagnosis labels (CN/MCI/AD).

## 2. Discovered Datasets & Evaluation

### A. Augmented Alzheimer MRI 4-Classes Dataset
- **Type**: Image Dataset (JPGs)
- **Patient-Level Tabular Data**: No
- **Suitability**: NOT SUITABLE
- **Reason**: The user explicitly requested to exclude MRI/Image datasets. Furthermore, it lacks tabular clinical demographics.

### B. Handwritten_dataset
- **Type**: Image Dataset (Handwriting tests)
- **Patient-Level Tabular Data**: No
- **Suitability**: NOT SUITABLE
- **Reason**: The user explicitly requested to exclude handwriting datasets. 

### C. Voice_Dataset
- **Type**: Audio Dataset (WAV files)
- **Patient-Level Tabular Data**: No
- **Suitability**: NOT SUITABLE
- **Reason**: The user explicitly requested to exclude voice datasets.

### D. PPMI (Parkinson's Progression Markers Initiative)
- **Type**: Tabular/Clinical
- **Patient-Level Tabular Data**: Yes
- **Target Disease**: Parkinson's Disease (not Alzheimer's)
- **Suitability**: NOT SUITABLE (for the Alzheimer's ML model)
- **Reason**: While it is a rich clinical tabular dataset, it is specifically for Parkinson's disease, not Alzheimer's disease.

### E. mri_datscan_ppmi
- **Type**: Image Dataset (DICOM/NIfTI)
- **Patient-Level Tabular Data**: No
- **Suitability**: NOT SUITABLE
- **Reason**: Image dataset for Parkinson's, excluding it per user request.

### F. parkinsons+telemonitoring
- **Type**: Tabular/Voice-derived
- **Patient-Level Tabular Data**: Yes
- **Target Disease**: Parkinson's Disease
- **Suitability**: NOT SUITABLE
- **Reason**: This is for Parkinson's disease progression, not Alzheimer's classification.

### G. ADNI
- **Type**: Tabular/Clinical
- **Patient-Level Tabular Data**: Yes (but critically incomplete)
- **Suitability**: NOT SUITABLE (in its current state)
- **Reason**: As verified in the previous step, the local ADNI folder lacks the baseline diagnosis file (`DXSUM_PDXCONV.csv`) and demographic file (`PTDEMO.csv`). Furthermore, we cannot use `ARM`, `PTSTATUS`, or `RGSTATUS` as labels.

## 3. Dataset Ranking
1. **BEST**: None found.
2. **ACCEPTABLE**: None found.
3. **NOT SUITABLE**: All local datasets (ADNI, PPMI, Voice, MRI, Handwriting, Telemonitoring).

## 4. Conclusion
**Do I already have a suitable dataset locally?**
**NO.** 

There are ZERO alternative tabular/clinical datasets for **Alzheimer's disease** locally. 
The only Alzheimer's tabular dataset is ADNI, which we have already proven is missing the necessary `DXSUM` and `PTDEMO` files to form a scientifically defensible baseline target. 

You must either:
1. Provide the missing ADNI files (`DXSUM_PDXCONV_ADNIALL.csv` and `PTDEMO.csv`).
2. Provide an entirely new tabular Alzheimer's dataset (e.g., OASIS-3 tabular clinical data).

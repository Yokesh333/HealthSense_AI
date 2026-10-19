import pathlib
import pandas as pd
import numpy as np
import json

PPMI_DIR = pathlib.Path(r"C:\Users\Yokesh\Desktop\Health_Sense AI\Datasets\PPMI")

# Load key datasets
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

print("=== 1. PARTICIPANT COUNTS ===")
print("Unique PATNOs in Participant_Status:", status_df['PATNO'].nunique())
cohort_counts = status_df['COHORT_DEFINITION'].value_counts(dropna=False)
print("Cohort Breakdown (All status):")
print(cohort_counts)

print("\nEnroll Status breakdown:")
print(status_df['ENROLL_STATUS'].value_counts(dropna=False))

# Filter Enrolled / Completed vs All
enrolled_mask = status_df['ENROLL_STATUS'].isin(['Enrolled', 'Complete', 'Baseline'])
print("\nEnrolled Cohort Breakdown:")
print(status_df[enrolled_mask]['COHORT_DEFINITION'].value_counts(dropna=False))

print("\n=== 2. BASELINE VISIT (BL) MERGE TEST ===")
# Demographics (1 row per PATNO)
demo_sub = demo_df[['PATNO', 'SEX', 'HANDED']].drop_duplicates('PATNO')

# Socio-Economics (education)
if 'EDUCYRS' in socio_df.columns:
    socio_sub = socio_df[['PATNO', 'EDUCYRS']].drop_duplicates('PATNO')
else:
    print("Socio cols:", socio_df.columns)
    socio_sub = socio_df[['PATNO']].drop_duplicates('PATNO')

# Age at BL
age_bl = age_df[age_df['EVENT_ID'] == 'BL'][['PATNO', 'AGE_AT_VISIT']].drop_duplicates('PATNO')

# MDS-UPDRS BL
updrs1_bl = updrs1_df[updrs1_df['EVENT_ID'] == 'BL'][['PATNO', 'NP1RTOT']].drop_duplicates('PATNO')
updrs2_bl = updrs2_df[updrs2_df['EVENT_ID'] == 'BL'][['PATNO', 'NP2PTOT']].drop_duplicates('PATNO')
updrs3_bl = updrs3_df[updrs3_df['EVENT_ID'] == 'BL'][['PATNO', 'NP3TOT', 'NHY']].drop_duplicates('PATNO')

# Non-motor BL
moca_bl = moca_df[moca_df['EVENT_ID'] == 'BL'][['PATNO', 'MCATOT']].drop_duplicates('PATNO')
gds_bl = gds_df[gds_df['EVENT_ID'] == 'BL'][['PATNO', 'GDSTOT']].drop_duplicates('PATNO')
ess_bl = ess_df[ess_df['EVENT_ID'] == 'BL'][['PATNO', 'ESS1', 'ESS2', 'ESS3', 'ESS4', 'ESS5', 'ESS6', 'ESS7', 'ESS8']].drop_duplicates('PATNO')
if 'ESS1' in ess_bl.columns:
    ess_bl['ESSTOT'] = ess_bl[['ESS1', 'ESS2', 'ESS3', 'ESS4', 'ESS5', 'ESS6', 'ESS7', 'ESS8']].sum(axis=1)

# Merge pipeline
merged = status_df[['PATNO', 'COHORT', 'COHORT_DEFINITION', 'ENROLL_STATUS']].merge(demo_sub, on='PATNO', how='left')
merged = merged.merge(age_bl, on='PATNO', how='left')
merged = merged.merge(socio_sub, on='PATNO', how='left')
merged = merged.merge(updrs1_bl, on='PATNO', how='left')
merged = merged.merge(updrs2_bl, on='PATNO', how='left')
merged = merged.merge(updrs3_bl, on='PATNO', how='left')
merged = merged.merge(moca_bl, on='PATNO', how='left')
merged = merged.merge(gds_bl, on='PATNO', how='left')

print(f"\nTotal merged rows (all participants in Participant_Status): {len(merged)}")
print("Merged columns:", list(merged.columns))

print("\nBaseline feature availability by Cohort:")
print(merged.groupby('COHORT_DEFINITION')[['AGE_AT_VISIT', 'SEX', 'EDUCYRS', 'NP1RTOT', 'NP2PTOT', 'NP3TOT', 'MCATOT', 'GDSTOT']].count())

# Usable baseline participants: participants with baseline age, sex, and at least UPDRS III total or UPDRS I/II or MoCA
usable_mask = merged['AGE_AT_VISIT'].notnull() & merged['SEX'].notnull() & (merged['NP3TOT'].notnull() | merged['NP1RTOT'].notnull() | merged['MCATOT'].notnull())
usable_df = merged[usable_mask]
print("\nUsable Baseline Participants breakdown by Cohort:")
print(usable_df['COHORT_DEFINITION'].value_counts())

# Strict usable baseline participants (PD vs HC vs SWEDD) having Age, Sex, UPDRS-I, UPDRS-II, UPDRS-III, MoCA
strict_mask = merged['AGE_AT_VISIT'].notnull() & merged['SEX'].notnull() & merged['NP1RTOT'].notnull() & merged['NP2PTOT'].notnull() & merged['NP3TOT'].notnull() & merged['MCATOT'].notnull()
strict_df = merged[strict_mask]
print("\nStrict Usable Baseline Participants (having Age, Sex, UPDRS I, II, III, MoCA) by Cohort:")
print(strict_df['COHORT_DEFINITION'].value_counts())


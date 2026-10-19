import pathlib
import pandas as pd
import numpy as np
import json

PPMI_DIR = pathlib.Path(r"C:\Users\Yokesh\Desktop\Health_Sense AI\Datasets\PPMI")

# Load Participant Status
status_df = pd.read_csv(PPMI_DIR / "Participant_Status_28Jul2026.csv", low_memory=False)

print("=== COHORT vs ENROLL_STATUS ===")
print(pd.crosstab(status_df['COHORT_DEFINITION'], status_df['ENROLL_STATUS'], dropna=False))

print("\n=== COHORT breakdown overall ===")
print(status_df['COHORT_DEFINITION'].value_counts(dropna=False))

print("\n=== COHORT breakdown for ENROLLED / COMPLETED ===")
enrolled_df = status_df[status_df['ENROLL_STATUS'].isin(['Enrolled', 'Complete', 'Baseline'])]
print(enrolled_df['COHORT_DEFINITION'].value_counts(dropna=False))

# Load Demographics
demo_df = pd.read_csv(PPMI_DIR / "Subject_Demographics" / "Demographics_28Jul2026.csv", low_memory=False)
age_df = pd.read_csv(PPMI_DIR / "Subject_Demographics" / "Age_at_visit_28Jul2026.csv", low_memory=False)

# Check baseline visit code in Age_at_visit & Motor/Non-motor
print("\n=== EVENT_ID values in Age_at_visit ===")
print(age_df['EVENT_ID'].value_counts().head(10))

# Baseline in Age_at_visit: EVENT_ID == 'BL' or 'SC' or 'V04' etc.
age_bl = age_df[age_df['EVENT_ID'] == 'BL']
print(f"Unique PATNOs in Age_at_visit with EVENT_ID=='BL': {age_bl['PATNO'].nunique()}")

# Let's inspect event_ids across motor and non-motor files
motor_p3 = pd.read_csv(PPMI_DIR / "Motor___MDS-UPDRS" / "MDS-UPDRS_Part_III_28Jul2026.csv", low_memory=False)
print("\n=== EVENT_ID values in MDS-UPDRS Part III ===")
print(motor_p3['EVENT_ID'].value_counts().head(10))

motor_p1 = pd.read_csv(PPMI_DIR / "Motor___MDS-UPDRS" / "MDS-UPDRS_Part_I_28Jul2026.csv", low_memory=False)
motor_p2 = pd.read_csv(PPMI_DIR / "Motor___MDS-UPDRS" / "MDS_UPDRS_Part_II__Patient_Questionnaire_28Jul2026.csv", low_memory=False)
motor_p4 = pd.read_csv(PPMI_DIR / "Motor___MDS-UPDRS" / "MDS-UPDRS_Part_IV__Motor_Complications_28Jul2026.csv", low_memory=False)

moca_df = pd.read_csv(PPMI_DIR / "Non-motor_Assessments" / "Montreal_Cognitive_Assessment__MoCA__28Jul2026.csv", low_memory=False)
gds_df = pd.read_csv(PPMI_DIR / "Non-motor_Assessments" / "Geriatric_Depression_Scale__Short_Version__28Jul2026.csv", low_memory=False)
ess_df = pd.read_csv(PPMI_DIR / "Non-motor_Assessments" / "Epworth_Sleepiness_Scale_28Jul2026.csv", low_memory=False)
rbd_df = pd.read_csv(PPMI_DIR / "Non-motor_Assessments" / "REM_Sleep_Behavior_Disorder_Screening_Questionnaire_28Jul2026.csv", low_memory=False)

print("\n=== Baseline (EVENT_ID=='BL') PATNO counts ===")
print("Demographics PATNOs:", demo_df['PATNO'].nunique())
print("Age at BL PATNOs:", age_bl['PATNO'].nunique())
print("MDS-UPDRS Part I BL PATNOs:", motor_p1[motor_p1['EVENT_ID']=='BL']['PATNO'].nunique())
print("MDS-UPDRS Part II BL PATNOs:", motor_p2[motor_p2['EVENT_ID']=='BL']['PATNO'].nunique())
print("MDS-UPDRS Part III BL PATNOs:", motor_p3[motor_p3['EVENT_ID']=='BL']['PATNO'].nunique())
print("MDS-UPDRS Part IV BL PATNOs:", motor_p4[motor_p4['EVENT_ID']=='BL']['PATNO'].nunique())
print("MoCA BL PATNOs:", moca_df[moca_df['EVENT_ID']=='BL']['PATNO'].nunique())
print("GDS BL PATNOs:", gds_df[gds_df['EVENT_ID']=='BL']['PATNO'].nunique())
print("ESS BL PATNOs:", ess_df[ess_df['EVENT_ID']=='BL']['PATNO'].nunique())
print("RBD BL PATNOs:", rbd_df[rbd_df['EVENT_ID']=='BL']['PATNO'].nunique())


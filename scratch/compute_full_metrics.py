import pathlib
import pandas as pd
import numpy as np
import json

PPMI_DIR = pathlib.Path(r"C:\Users\Yokesh\Desktop\Health_Sense AI\Datasets\PPMI")

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
sdmt_df = pd.read_csv(PPMI_DIR / "Non-motor_Assessments" / "Symbol_Digit_Modalities_Test_28Jul2026.csv", low_memory=False)

# Compute GDS Total score if not present
gds_items = ['GDSSATIS', 'GDSDROPD', 'GDSEMPTY', 'GDSBORED', 'GDSGSPIR', 'GDSAFRAD', 'GDSHAPPY', 'GDSHLPLS', 'GDSHOME', 'GDSMEMRY', 'GDSALIVE', 'GDSWRTLS', 'GDSENRGY', 'GDSHOPLS', 'GDSBETER']
# GDS scoring: GDSSATIS, GDSGSPIR, GDSHAPPY, GDSALIVE, GDSBETER: 0 is depressed if answer is No (0).
# For standard binary items where 1 indicates depressive symptom:
gds_df['GDS_TOTAL'] = gds_df[gds_items].sum(axis=1, skipna=False)

# Compute ESS Total
ess_items = ['ESS1', 'ESS2', 'ESS3', 'ESS4', 'ESS5', 'ESS6', 'ESS7', 'ESS8']
ess_df['ESS_TOTAL'] = ess_df[ess_items].sum(axis=1, skipna=False)

# Compute RBD Total (first 10 items are main score)
rbd_items = ['DRMVIVID', 'DRMAGRAC', 'DRMNOCTB', 'SLPLMBMV', 'SLPINJUR', 'DRMVERBL', 'DRMFIGHT', 'DRMUMV', 'DRMOBJFL', 'MVAWAKEN', 'DRMREMEM', 'SLPDSTRB']
rbd_df['RBD_TOTAL'] = rbd_df[rbd_items].sum(axis=1, skipna=False)

# Extract Baseline Data
demo_sub = demo_df[['PATNO', 'SEX', 'HANDED']].drop_duplicates('PATNO')

if 'EDUCYRS' in socio_df.columns:
    socio_sub = socio_df[['PATNO', 'EDUCYRS']].drop_duplicates('PATNO')
else:
    socio_sub = pd.DataFrame(columns=['PATNO', 'EDUCYRS'])

age_bl = age_df[age_df['EVENT_ID'] == 'BL'][['PATNO', 'AGE_AT_VISIT']].drop_duplicates('PATNO')

updrs1_bl = updrs1_df[updrs1_df['EVENT_ID'] == 'BL'][['PATNO', 'NP1RTOT']].drop_duplicates('PATNO')
updrs2_bl = updrs2_df[updrs2_df['EVENT_ID'] == 'BL'][['PATNO', 'NP2PTOT']].drop_duplicates('PATNO')
updrs3_bl = updrs3_df[updrs3_df['EVENT_ID'] == 'BL'][['PATNO', 'NP3TOT', 'NHY']].drop_duplicates('PATNO')
updrs4_bl = updrs4_df[updrs4_df['EVENT_ID'] == 'BL'][['PATNO', 'NP4TOT']].drop_duplicates('PATNO')

moca_bl = moca_df[moca_df['EVENT_ID'] == 'BL'][['PATNO', 'MCATOT']].drop_duplicates('PATNO')
gds_bl = gds_df[gds_df['EVENT_ID'] == 'BL'][['PATNO', 'GDS_TOTAL']].drop_duplicates('PATNO')
ess_bl = ess_df[ess_df['EVENT_ID'] == 'BL'][['PATNO', 'ESS_TOTAL']].drop_duplicates('PATNO')
rbd_bl = rbd_df[rbd_df['EVENT_ID'] == 'BL'][['PATNO', 'RBD_TOTAL']].drop_duplicates('PATNO')
upsit_bl = upsit_df[upsit_df['EVENT_ID'] == 'BL'][['PATNO', 'TOTAL_CORRECT']].rename(columns={'TOTAL_CORRECT': 'UPSIT_TOTAL'}).drop_duplicates('PATNO')
sdmt_bl = sdmt_df[sdmt_df['EVENT_ID'] == 'BL'][['PATNO', 'SDMTOTAL']].drop_duplicates('PATNO')

# Merge
master = status_df[['PATNO', 'COHORT', 'COHORT_DEFINITION', 'ENROLL_STATUS']].copy()
master = master.merge(demo_sub, on='PATNO', how='left')
master = master.merge(age_bl, on='PATNO', how='left')
master = master.merge(socio_sub, on='PATNO', how='left')
master = master.merge(updrs1_bl, on='PATNO', how='left')
master = master.merge(updrs2_bl, on='PATNO', how='left')
master = master.merge(updrs3_bl, on='PATNO', how='left')
master = master.merge(updrs4_bl, on='PATNO', how='left')
master = master.merge(moca_bl, on='PATNO', how='left')
master = master.merge(gds_bl, on='PATNO', how='left')
master = master.merge(ess_bl, on='PATNO', how='left')
master = master.merge(rbd_bl, on='PATNO', how='left')
master = master.merge(upsit_bl, on='PATNO', how='left')
master = master.merge(sdmt_bl, on='PATNO', how='left')

print("=== MASTER DATASET SUMMARY ===")
print("Total rows:", len(master))
print("Unique PATNOs:", master['PATNO'].nunique())

print("\n--- Cohort Breakdown (All Statuses) ---")
print(master['COHORT_DEFINITION'].value_counts(dropna=False))

print("\n--- Non-Null Feature Counts by Cohort ---")
feat_cols = ['AGE_AT_VISIT', 'SEX', 'HANDED', 'EDUCYRS', 'NP1RTOT', 'NP2PTOT', 'NP3TOT', 'NHY', 'NP4TOT', 'MCATOT', 'GDS_TOTAL', 'ESS_TOTAL', 'RBD_TOTAL', 'UPSIT_TOTAL', 'SDMTOTAL']
print(master.groupby('COHORT_DEFINITION')[feat_cols].count())

print("\n--- Missing Percentage (%) by Cohort for Candidate Features ---")
for cohort, group in master.groupby('COHORT_DEFINITION'):
    print(f"\nCohort: {cohort} (N={len(group)})")
    missing_pct = (group[feat_cols].isnull().sum() / len(group)) * 100
    for col in feat_cols:
        print(f"  {col}: {missing_pct[col]:.1f}% missing ({group[col].notnull().sum()} present)")

# Define "Usable Baseline Participants"
# Option A: Core features available (AGE, SEX, UPDRS III total or UPDRS I/II or MoCA)
has_core = master['AGE_AT_VISIT'].notnull() & master['SEX'].notnull() & (master['NP3TOT'].notnull() | master['NP1RTOT'].notnull() | master['MCATOT'].notnull())

# Option B: Complete Motor + Cognition (AGE, SEX, UPDRS I, II, III, MoCA)
has_complete_motor_cog = master['AGE_AT_VISIT'].notnull() & master['SEX'].notnull() & master['NP1RTOT'].notnull() & master['NP2PTOT'].notnull() & master['NP3TOT'].notnull() & master['MCATOT'].notnull()

# Option C: Enrolled only + Complete Motor + Cognition
has_enrolled_complete = master['ENROLL_STATUS'].isin(['Enrolled', 'Complete', 'Baseline']) & has_complete_motor_cog

print("\n=== PARTICIPANT COUNT SUMMARY MATRIX ===")
print("1. Total Unique Participants in PPMI Participant_Status:", master['PATNO'].nunique())
print("2. Total PD participants:", (master['COHORT_DEFINITION'] == "Parkinson's Disease").sum())
print("3. Total Healthy Control participants:", (master['COHORT_DEFINITION'] == "Healthy Control").sum())
print("4. Total SWEDD participants:", (master['COHORT_DEFINITION'] == "SWEDD").sum())
print("5. Total Prodromal participants:", (master['COHORT_DEFINITION'] == "Prodromal").sum())

print("\n6. Participants with Baseline Data (AGE_AT_VISIT at BL present):", master['AGE_AT_VISIT'].notnull().sum())
print("   - PD with BL Age:", ((master['COHORT_DEFINITION'] == "Parkinson's Disease") & master['AGE_AT_VISIT'].notnull()).sum())
print("   - HC with BL Age:", ((master['COHORT_DEFINITION'] == "Healthy Control") & master['AGE_AT_VISIT'].notnull()).sum())
print("   - SWEDD with BL Age:", ((master['COHORT_DEFINITION'] == "SWEDD") & master['AGE_AT_VISIT'].notnull()).sum())

print("\n7. Usable Baseline Participants (Core Motor + Demographics present):", has_core.sum())
print(master[has_core]['COHORT_DEFINITION'].value_counts())

print("\n8. Strict Usable Baseline Participants (Age, Sex, UPDRS I, II, III, MoCA present):", has_complete_motor_cog.sum())
print(master[has_complete_motor_cog]['COHORT_DEFINITION'].value_counts())

print("\n9. Enrolled Usable Baseline Participants (Enrolled/Complete + Age, Sex, UPDRS I, II, III, MoCA present):", has_enrolled_complete.sum())
print(master[has_enrolled_complete]['COHORT_DEFINITION'].value_counts())


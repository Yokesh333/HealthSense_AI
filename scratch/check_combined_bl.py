import pathlib
import pandas as pd

PPMI_DIR = pathlib.Path(r"C:\Users\Yokesh\Desktop\Health_Sense AI\Datasets\PPMI")

status_df = pd.read_csv(PPMI_DIR / "Participant_Status_28Jul2026.csv", low_memory=False)
demo_df = pd.read_csv(PPMI_DIR / "Subject_Demographics" / "Demographics_28Jul2026.csv", low_memory=False)
age_df = pd.read_csv(PPMI_DIR / "Subject_Demographics" / "Age_at_visit_28Jul2026.csv", low_memory=False)

updrs1_df = pd.read_csv(PPMI_DIR / "Motor___MDS-UPDRS" / "MDS-UPDRS_Part_I_28Jul2026.csv", low_memory=False)
updrs2_df = pd.read_csv(PPMI_DIR / "Motor___MDS-UPDRS" / "MDS_UPDRS_Part_II__Patient_Questionnaire_28Jul2026.csv", low_memory=False)
updrs3_df = pd.read_csv(PPMI_DIR / "Motor___MDS-UPDRS" / "MDS-UPDRS_Part_III_28Jul2026.csv", low_memory=False)

moca_df = pd.read_csv(PPMI_DIR / "Non-motor_Assessments" / "Montreal_Cognitive_Assessment__MoCA__28Jul2026.csv", low_memory=False)
gds_df = pd.read_csv(PPMI_DIR / "Non-motor_Assessments" / "Geriatric_Depression_Scale__Short_Version__28Jul2026.csv", low_memory=False)
ess_df = pd.read_csv(PPMI_DIR / "Non-motor_Assessments" / "Epworth_Sleepiness_Scale_28Jul2026.csv", low_memory=False)
rbd_df = pd.read_csv(PPMI_DIR / "Non-motor_Assessments" / "REM_Sleep_Behavior_Disorder_Screening_Questionnaire_28Jul2026.csv", low_memory=False)
upsit_df = pd.read_csv(PPMI_DIR / "Non-motor_Assessments" / "University_of_Pennsylvania_Smell_Identification_Test_UPSIT_28Jul2026.csv", low_memory=False)

# Get baseline/screening age: take BL first, fallback to SC
age_bl = age_df[age_df['EVENT_ID'] == 'BL'][['PATNO', 'AGE_AT_VISIT']].drop_duplicates('PATNO')
age_sc = age_df[age_df['EVENT_ID'] == 'SC'][['PATNO', 'AGE_AT_VISIT']].drop_duplicates('PATNO')
age_combined = pd.concat([age_bl, age_sc]).drop_duplicates('PATNO', keep='first')

# MoCA: take BL first, fallback to SC
moca_bl = moca_df[moca_df['EVENT_ID'] == 'BL'][['PATNO', 'MCATOT']].drop_duplicates('PATNO')
moca_sc = moca_df[moca_df['EVENT_ID'] == 'SC'][['PATNO', 'MCATOT']].drop_duplicates('PATNO')
moca_combined = pd.concat([moca_bl, moca_sc]).drop_duplicates('PATNO', keep='first')

# UPSIT: take BL first, fallback to SC
upsit_bl = upsit_df[upsit_df['EVENT_ID'] == 'BL'][['PATNO', 'TOTAL_CORRECT']].rename(columns={'TOTAL_CORRECT': 'UPSIT_TOTAL'}).drop_duplicates('PATNO')
upsit_sc = upsit_df[upsit_df['EVENT_ID'] == 'SC'][['PATNO', 'TOTAL_CORRECT']].rename(columns={'TOTAL_CORRECT': 'UPSIT_TOTAL'}).drop_duplicates('PATNO')
upsit_combined = pd.concat([upsit_bl, upsit_sc]).drop_duplicates('PATNO', keep='first')

# Demographics
demo_sub = demo_df[['PATNO', 'SEX', 'HANDED']].drop_duplicates('PATNO')

# Motor BL
updrs1_bl = updrs1_df[updrs1_df['EVENT_ID'] == 'BL'][['PATNO', 'NP1RTOT']].drop_duplicates('PATNO')
updrs2_bl = updrs2_df[updrs2_df['EVENT_ID'] == 'BL'][['PATNO', 'NP2PTOT']].drop_duplicates('PATNO')
updrs3_bl = updrs3_df[updrs3_df['EVENT_ID'] == 'BL'][['PATNO', 'NP3TOT', 'NHY']].drop_duplicates('PATNO')

# Non-motor BL
gds_items = ['GDSSATIS', 'GDSDROPD', 'GDSEMPTY', 'GDSBORED', 'GDSGSPIR', 'GDSAFRAD', 'GDSHAPPY', 'GDSHLPLS', 'GDSHOME', 'GDSMEMRY', 'GDSALIVE', 'GDSWRTLS', 'GDSENRGY', 'GDSHOPLS', 'GDSBETER']
gds_df['GDS_TOTAL'] = gds_df[gds_items].sum(axis=1, skipna=False)
gds_bl = gds_df[gds_df['EVENT_ID'] == 'BL'][['PATNO', 'GDS_TOTAL']].drop_duplicates('PATNO')

ess_items = ['ESS1', 'ESS2', 'ESS3', 'ESS4', 'ESS5', 'ESS6', 'ESS7', 'ESS8']
ess_df['ESS_TOTAL'] = ess_df[ess_items].sum(axis=1, skipna=False)
ess_bl = ess_df[ess_df['EVENT_ID'] == 'BL'][['PATNO', 'ESS_TOTAL']].drop_duplicates('PATNO')

rbd_items = ['DRMVIVID', 'DRMAGRAC', 'DRMNOCTB', 'SLPLMBMV', 'SLPINJUR', 'DRMVERBL', 'DRMFIGHT', 'DRMUMV', 'DRMOBJFL', 'MVAWAKEN', 'DRMREMEM', 'SLPDSTRB']
rbd_df['RBD_TOTAL'] = rbd_df[rbd_items].sum(axis=1, skipna=False)
rbd_bl = rbd_df[rbd_df['EVENT_ID'] == 'BL'][['PATNO', 'RBD_TOTAL']].drop_duplicates('PATNO')

# Merge
master = status_df[['PATNO', 'COHORT', 'COHORT_DEFINITION', 'ENROLL_STATUS']].copy()
master = master.merge(demo_sub, on='PATNO', how='left')
master = master.merge(age_combined, on='PATNO', how='left')
master = master.merge(updrs1_bl, on='PATNO', how='left')
master = master.merge(updrs2_bl, on='PATNO', how='left')
master = master.merge(updrs3_bl, on='PATNO', how='left')
master = master.merge(moca_combined, on='PATNO', how='left')
master = master.merge(gds_bl, on='PATNO', how='left')
master = master.merge(ess_bl, on='PATNO', how='left')
master = master.merge(rbd_bl, on='PATNO', how='left')
master = master.merge(upsit_combined, on='PATNO', how='left')

print("=== COMBINED BL/SC BASELINE COVERAGE ===")
feat_cols = ['AGE_AT_VISIT', 'SEX', 'HANDED', 'NP1RTOT', 'NP2PTOT', 'NP3TOT', 'NHY', 'MCATOT', 'GDS_TOTAL', 'ESS_TOTAL', 'RBD_TOTAL', 'UPSIT_TOTAL']
print(master.groupby('COHORT_DEFINITION')[feat_cols].count())

print("\n--- Missing Percentage (%) by Cohort (SC + BL Combined) ---")
for cohort, group in master.groupby('COHORT_DEFINITION'):
    print(f"\nCohort: {cohort} (N={len(group)})")
    missing_pct = (group[feat_cols].isnull().sum() / len(group)) * 100
    for col in feat_cols:
        print(f"  {col}: {missing_pct[col]:.1f}% missing ({group[col].notnull().sum()} present)")

# Filter for PD vs HC vs SWEDD:
usable_pd_hc = master[master['COHORT_DEFINITION'].isin(["Parkinson's Disease", "Healthy Control"])]
usable_complete = usable_pd_hc[
    usable_pd_hc['AGE_AT_VISIT'].notnull() & 
    usable_pd_hc['SEX'].notnull() & 
    usable_pd_hc['NP1RTOT'].notnull() & 
    usable_pd_hc['NP2PTOT'].notnull() & 
    usable_pd_hc['NP3TOT'].notnull()
]

print(f"\nUsable PD vs HC Baseline Participants (Age, Sex, UPDRS I, II, III present): {len(usable_complete)}")
print(usable_complete['COHORT_DEFINITION'].value_counts())

usable_complete_all = master[
    master['AGE_AT_VISIT'].notnull() & 
    master['SEX'].notnull() & 
    master['NP1RTOT'].notnull() & 
    master['NP2PTOT'].notnull() & 
    master['NP3TOT'].notnull()
]
print(f"\nUsable Baseline Participants Across All Cohorts (Age, Sex, UPDRS I, II, III present): {len(usable_complete_all)}")
print(usable_complete_all['COHORT_DEFINITION'].value_counts())


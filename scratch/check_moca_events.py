import pathlib
import pandas as pd

PPMI_DIR = pathlib.Path(r"C:\Users\Yokesh\Desktop\Health_Sense AI\Datasets\PPMI")

moca_df = pd.read_csv(PPMI_DIR / "Non-motor_Assessments" / "Montreal_Cognitive_Assessment__MoCA__28Jul2026.csv", low_memory=False)

print("=== MoCA EVENT_ID Value Counts ===")
print(moca_df['EVENT_ID'].value_counts())

# Let's check for PATNOs in MoCA: if they have SC or BL or V04 etc.
moca_sc = moca_df[moca_df['EVENT_ID'] == 'SC']['PATNO'].unique()
moca_bl = moca_df[moca_df['EVENT_ID'] == 'BL']['PATNO'].unique()
moca_v04 = moca_df[moca_df['EVENT_ID'] == 'V04']['PATNO'].unique()

print(f"MoCA unique PATNOs with SC: {len(moca_sc)}")
print(f"MoCA unique PATNOs with BL: {len(moca_bl)}")
print(f"MoCA unique PATNOs with V04: {len(moca_v04)}")
print(f"MoCA total unique PATNOs across any visit: {moca_df['PATNO'].nunique()}")

# Check SC or BL combined for MoCA
moca_sc_bl = moca_df[moca_df['EVENT_ID'].isin(['SC', 'BL'])][['PATNO', 'MCATOT']].drop_duplicates('PATNO')
print(f"MoCA unique PATNOs with SC or BL: {moca_sc_bl['PATNO'].nunique()}")
print(f"MoCA non-null MCATOT with SC or BL: {moca_sc_bl['MCATOT'].notnull().sum()}")

# Let's check UPSIT event_ids as well
upsit_df = pd.read_csv(PPMI_DIR / "Non-motor_Assessments" / "University_of_Pennsylvania_Smell_Identification_Test_UPSIT_28Jul2026.csv", low_memory=False)
print("\n=== UPSIT EVENT_ID Value Counts ===")
print(upsit_df['EVENT_ID'].value_counts())


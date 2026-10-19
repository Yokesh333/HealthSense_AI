import pathlib
import pandas as pd
import numpy as np

PPMI_DIR = pathlib.Path(r"C:\Users\Yokesh\Desktop\Health_Sense AI\Datasets\PPMI")

print("=== 1. PARTICIPANT STATUS ANALYSIS ===")
status_path = PPMI_DIR / "Participant_Status_28Jul2026.csv"
if status_path.exists():
    df_status = pd.read_csv(status_path, low_memory=False)
    print("Participant Status columns:", list(df_status.columns))
    print("Shape:", df_status.shape)
    for col in df_status.columns:
        print(f"\nValue counts for {col}:")
        print(df_status[col].value_counts(dropna=False).head(20))
else:
    print("Participant_Status_28Jul2026.csv not found!")

print("\n=== 2. DEMOGRAPHICS ANALYSIS ===")
demo_path = PPMI_DIR / "Subject_Demographics" / "Demographics_28Jul2026.csv"
if demo_path.exists():
    df_demo = pd.read_csv(demo_path, low_memory=False)
    print("Demographics columns:", list(df_demo.columns))
    print("Shape:", df_demo.shape)
    print(df_demo.head(3))
    print("Unique PATNOs in Demographics:", df_demo['PATNO'].nunique() if 'PATNO' in df_demo.columns else "No PATNO")

age_path = PPMI_DIR / "Subject_Demographics" / "Age_at_visit_28Jul2026.csv"
if age_path.exists():
    df_age = pd.read_csv(age_path, low_memory=False)
    print("\nAge_at_visit columns:", list(df_age.columns))
    print("Shape:", df_age.shape)
    print(df_age.head(3))

print("\n=== 3. SUBJECT COHORT HISTORY ===")
cohort_hist_path = PPMI_DIR / "Subject_Demographics" / "Subject_Cohort_History_28Jul2026.csv"
if cohort_hist_path.exists():
    df_ch = pd.read_csv(cohort_hist_path, low_memory=False)
    print("Subject_Cohort_History columns:", list(df_ch.columns))
    print("Shape:", df_ch.shape)
    for c in df_ch.columns:
        if df_ch[c].nunique() < 30:
            print(f"Value counts for {c}:")
            print(df_ch[c].value_counts(dropna=False))

print("\n=== 4. MEDICAL DIAGNOSIS FILES ===")
for fname in ["Clinical_Diagnosis_28Jul2026.csv", "PD_Diagnosis_History_28Jul2026.csv", "Primary_Research_Diagnosis_28Jul2026.csv"]:
    p = PPMI_DIR / "Medical" / fname
    if p.exists():
        df_med = pd.read_csv(p, low_memory=False)
        print(f"\n--- {fname} ---")
        print("Columns:", list(df_med.columns))
        print("Shape:", df_med.shape)
        print(df_med.head(2))

print("\n=== 5. MOTOR MDS-UPDRS FILES ===")
motor_dir = PPMI_DIR / "Motor___MDS-UPDRS"
for p in motor_dir.glob("*.csv"):
    df_m = pd.read_csv(p, low_memory=False)
    print(f"\n--- {p.name} ---")
    print("Columns:", list(df_m.columns))
    print("Shape:", df_m.shape)


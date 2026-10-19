import pathlib
import pandas as pd

PPMI_DIR = pathlib.Path(r"C:\Users\Yokesh\Desktop\Health_Sense AI\Datasets\PPMI")

print("=== NON-MOTOR ASSESSMENTS COLUMNS ===")
nm_dir = PPMI_DIR / "Non-motor_Assessments"
for p in sorted(nm_dir.glob("*.csv")):
    df = pd.read_csv(p, low_memory=False)
    print(f"\n--- {p.name} (Rows: {len(df)}) ---")
    print(list(df.columns))


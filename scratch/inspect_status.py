import pathlib
import pandas as pd

PPMI_DIR = pathlib.Path(r"C:\Users\Yokesh\Desktop\Health_Sense AI\Datasets\PPMI")

status_path = PPMI_DIR / "Participant_Status_28Jul2026.csv"
df = pd.read_csv(status_path, low_memory=False)

print("Columns in Participant_Status:")
for c in df.columns:
    n_unique = df[c].nunique(dropna=False)
    print(f"Column: {c} | Unique values: {n_unique}")
    if n_unique <= 20:
        print(df[c].value_counts(dropna=False))
        print("-" * 40)

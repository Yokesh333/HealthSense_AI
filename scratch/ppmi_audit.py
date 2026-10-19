import os
import glob
import pathlib
import pandas as pd
import numpy as np
import json

PPMI_DIR = pathlib.Path(r"C:\Users\Yokesh\Desktop\Health_Sense AI\Datasets\PPMI")

def analyze_file(filepath):
    rel_path = filepath.relative_to(PPMI_DIR)
    try:
        if str(filepath).endswith('.csv'):
            df = pd.read_csv(filepath, low_memory=False)
        else:
            df = pd.read_excel(filepath)
    except Exception as e:
        return {"error": str(e), "path": str(rel_path)}
    
    num_rows, num_cols = df.shape
    cols = list(df.columns)
    
    # Missing value percentages
    missing_pct = df.isnull().mean() * 100
    missing_dict = {col: round(missing_pct[col], 2) for col in cols}
    
    # Identify PATNO/subject identifier
    patno_col = None
    for c in cols:
        if c.upper() in ['PATNO', 'SUBJECT_ID', 'SUBJID', 'SUBJECT', 'ID']:
            patno_col = c
            break
        elif 'PATNO' in c.upper():
            patno_col = c
            break
            
    # Identify visit / timepoint columns
    visit_cols = [c for c in cols if any(k in c.upper() for k in ['VISIT', 'EVENT', 'EVENT_ID', 'TIMEPOINT', 'CLINICAL_EVENT', 'EVENT_NAME'])]
    
    # Identify date columns
    date_cols = [c for c in cols if any(k in c.upper() for k in ['DATE', 'DT', 'YEAR', 'YR']) or 'DATE' in c.upper()]
    
    # Sample rows (first 3) converted to json/dict (handling NaNs)
    sample_rows = df.head(3).replace({np.nan: None}).to_dict(orient='records')
    
    return {
        "filename": filepath.name,
        "path": str(rel_path),
        "num_rows": num_rows,
        "num_cols": num_cols,
        "columns": cols,
        "patno_col": patno_col,
        "visit_cols": visit_cols,
        "date_cols": date_cols,
        "missing_dict": missing_dict,
        "sample_rows": sample_rows
    }

def main():
    files = sorted(list(PPMI_DIR.rglob('*.csv')) + list(PPMI_DIR.rglob('*.xls*')))
    print(f"Analyzing {len(files)} files...")
    
    inventory = []
    for f in files:
        res = analyze_file(f)
        inventory.append(res)
        
    print(f"Analyzed {len(inventory)} files successfully.")
    
    # Save raw audit inventory to scratch/inventory.json for easy processing
    scratch_dir = pathlib.Path(r"C:\Users\Yokesh\Desktop\Health_Sense AI\scratch")
    scratch_dir.mkdir(parents=True, exist_ok=True)
    with open(scratch_dir / "inventory.json", "w") as out:
        json.dump(inventory, out, indent=2)
        
    print("Saved inventory to scratch/inventory.json")

if __name__ == "__main__":
    main()

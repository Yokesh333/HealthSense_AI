import os
import pandas as pd
import json
import pyreadr
import numpy as np

def inspect_df(df, name):
    res = {
        "name": name,
        "rows": len(df),
        "columns": len(df.columns),
        "columns_list": list(df.columns),
        "head": df.head(3).to_dict('records')
    }
    
    # Specific variables check
    diag_vars = ['DX', 'DXCHANGE', 'DXCURREN', 'DXBL', 'DIAGNOSIS', 'DX_bl']
    demo_vars = ['AGE', 'PTGENDER', 'PTEDUCAT', 'PTRACCAT', 'PTETHCAT', 'SEX']
    cog_vars = ['MMSE', 'MOCA', 'ADAS', 'CDR', 'FAQ']
    
    res['diag_info'] = {}
    res['demo_info'] = {}
    res['cog_info'] = {}
    
    for c in df.columns:
        c_up = c.upper()
        if any(d in c_up for d in diag_vars):
            counts = df[c].value_counts(dropna=False).head(15).to_dict()
            res['diag_info'][c] = {
                "dtype": str(df[c].dtype),
                "notnull": int(df[c].notna().sum()),
                "counts": {str(k): int(v) for k, v in counts.items()}
            }
        if any(d in c_up for d in demo_vars):
            res['demo_info'][c] = {
                "dtype": str(df[c].dtype),
                "notnull": int(df[c].notna().sum())
            }
        if any(d in c_up for d in cog_vars):
            res['cog_info'][c] = {
                "dtype": str(df[c].dtype),
                "notnull": int(df[c].notna().sum())
            }
            
    return res

results = {}

adni_dir = r"C:\Users\Yokesh\Desktop\Health_Sense AI\Datasets\ADNI"
extract_dir = r"C:\Users\Yokesh\Desktop\Health_Sense AI\scratch\temp_extract\ADNIMERGE2\data"

# 1. PTDEMOG
ptdemog_path = os.path.join(adni_dir, "PTDEMOG_31Aug2026.csv")
if os.path.exists(ptdemog_path):
    df = pd.read_csv(ptdemog_path, low_memory=False)
    results['PTDEMOG'] = inspect_df(df, "PTDEMOG_31Aug2026.csv")

# 2. BLCHANGE
blchange_path = os.path.join(adni_dir, "BLCHANGE_31Aug2026.csv")
if os.path.exists(blchange_path):
    df = pd.read_csv(blchange_path, low_memory=False)
    results['BLCHANGE'] = inspect_df(df, "BLCHANGE_31Aug2026.csv")

# 3. DXSUM.rda
dxsum_path = os.path.join(extract_dir, "DXSUM.rda")
if os.path.exists(dxsum_path):
    rda = pyreadr.read_r(dxsum_path)
    df = list(rda.values())[0] # first dataframe
    results['DXSUM'] = inspect_df(df, "DXSUM.rda")

# 4. Try to find ADNIMERGE
for f in os.listdir(extract_dir):
    if "ADNIMERGE" in f.upper() and f.endswith(".rda"):
        path = os.path.join(extract_dir, f)
        rda = pyreadr.read_r(path)
        df = list(rda.values())[0]
        results['ADNIMERGE'] = inspect_df(df, f)

with open(r"C:\Users\Yokesh\Desktop\Health_Sense AI\scratch\new_files_audit.json", "w") as f:
    json.dump(results, f, indent=2, default=str)

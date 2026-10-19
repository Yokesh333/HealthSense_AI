import os
import pandas as pd
import json

base_dir = r"C:\Users\Yokesh\Desktop\Health_Sense AI\Datasets\ADNI"

results = {
    "diagnosis_cols": [],
    "arm_analysis": {},
    "demographic_cols": [],
    "ptstatus_analysis": {},
    "rgstatus_analysis": {}
}

diag_keywords = ['DX', 'DIAGNOSIS', 'STATUS', 'ARM', 'DIAG']
demo_keywords = ['AGE', 'SEX', 'EDU', 'DOB', 'GENDER', 'RACE', 'ETHN']

for root, dirs, files in os.walk(base_dir):
    for f in files:
        if f.endswith('.csv'):
            path = os.path.join(root, f)
            rel_path = os.path.relpath(path, base_dir)
            try:
                df = pd.read_csv(path, low_memory=False)
                cols = list(df.columns)
                
                # Check Diagnosis columns
                for c in cols:
                    c_up = c.upper()
                    if any(k in c_up for k in diag_keywords):
                        counts = df[c].value_counts(dropna=False).head(10).to_dict()
                        results["diagnosis_cols"].append({
                            "file": rel_path,
                            "column": c,
                            "unique_values": len(df[c].dropna().unique()),
                            "non_null_count": int(df[c].notna().sum()),
                            "counts": {str(k): int(v) for k, v in counts.items()}
                        })
                        
                        if c == 'PTSTATUS' and 'REGISTRY' in f.upper():
                            results['ptstatus_analysis'] = {
                                "file": rel_path,
                                "counts": {str(k): int(v) for k, v in counts.items()}
                            }
                        if c == 'RGSTATUS' and 'REGISTRY' in f.upper():
                            results['rgstatus_analysis'] = {
                                "file": rel_path,
                                "counts": {str(k): int(v) for k, v in counts.items()}
                            }
                        if c == 'ARM' and 'ARM' in f.upper():
                            arm_phase = df['PHASE'].unique().tolist() if 'PHASE' in df.columns else []
                            arm_vis = df['VISCODE'].unique().tolist() if 'VISCODE' in df.columns else []
                            results['arm_analysis'] = {
                                "file": rel_path,
                                "phases": [str(x) for x in arm_phase],
                                "viscodes": [str(x) for x in arm_vis][:10],
                                "counts": {str(k): int(v) for k, v in counts.items()}
                            }
                            
                # Check Demographic columns
                for c in cols:
                    c_up = c.upper()
                    if any(k in c_up for k in demo_keywords):
                        results["demographic_cols"].append({
                            "file": rel_path,
                            "column": c
                        })
                        
            except Exception as e:
                pass

with open(r"C:\Users\Yokesh\Desktop\Health_Sense AI\scratch\verify_results.json", "w") as f:
    json.dump(results, f, indent=2)

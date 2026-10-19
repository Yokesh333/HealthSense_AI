import os
import pandas as pd
import pyreadr

def main():
    adni_dir = r"C:\Users\Yokesh\Desktop\Health_Sense AI\Datasets\ADNI"
    extract_dir = r"C:\Users\Yokesh\Desktop\Health_Sense AI\scratch\temp_extract\ADNIMERGE2\data"
    output_path = r"C:\Users\Yokesh\Desktop\Health_Sense AI\data\processed\adni\adni_dx_baseline.csv"

    # Read DXSUM
    dxsum_path = os.path.join(extract_dir, "DXSUM.rda")
    rda = pyreadr.read_r(dxsum_path)
    dxsum = list(rda.values())[0]

    # Keep relevant columns
    dxsum = dxsum[['PTID', 'RID', 'VISCODE', 'DIAGNOSIS', 'EXAMDATE']].copy()

    # Filter to baseline
    baseline_dx = dxsum[dxsum['VISCODE'] == 'bl'].copy()

    # Create original diagnosis and target
    baseline_dx['diagnosis_original'] = baseline_dx['DIAGNOSIS']
    
    def map_diagnosis(dx):
        if pd.isna(dx): return None
        if dx == "CN": return "CN"
        if dx == "MCI": return "MCI"
        if dx == "Dementia": return "AD"
        return None

    baseline_dx['target'] = baseline_dx['diagnosis_original'].apply(map_diagnosis)

    # Remove rows with missing target
    baseline_dx = baseline_dx.dropna(subset=['target'])

    # Handle duplicates deterministically
    # If multiple baseline records exist, sort by EXAMDATE (descending to get latest baseline attempt)
    # or ascending to get earliest. ADNI standard is earliest baseline is the true baseline.
    baseline_dx['EXAMDATE'] = pd.to_datetime(baseline_dx['EXAMDATE'], errors='coerce')
    baseline_dx = baseline_dx.sort_values(by=['PTID', 'EXAMDATE'], ascending=[True, True])
    
    dup_count = baseline_dx.duplicated(subset=['PTID']).sum()
    print(f"Resolving {dup_count} duplicate baseline records (keeping earliest EXAMDATE).")
    baseline_dx = baseline_dx.drop_duplicates(subset=['PTID'], keep='first')

    print(f"Final baseline diagnosis dataset has {len(baseline_dx)} rows.")
    print(baseline_dx['target'].value_counts())

    baseline_dx.to_csv(output_path, index=False)
    print(f"Saved to {output_path}")

if __name__ == "__main__":
    main()

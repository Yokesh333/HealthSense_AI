import os
import pandas as pd
import sys

def main():
    base_dir = r"C:\Users\Yokesh\Desktop\Health_Sense AI"
    processed_dir = os.path.join(base_dir, "data", "processed", "adni")
    
    train_df = pd.read_csv(os.path.join(processed_dir, "adni_train.csv"))
    val_df = pd.read_csv(os.path.join(processed_dir, "adni_validation.csv"))
    test_df = pd.read_csv(os.path.join(processed_dir, "adni_test.csv"))
    full_df = pd.read_csv(os.path.join(processed_dir, "adni_baseline_clean.csv"))

    print("Starting Data Quality Validation...\n")
    
    errors = []

    # 1. PTID Uniqueness in splits
    for name, df in [("Train", train_df), ("Val", val_df), ("Test", test_df), ("Full", full_df)]:
        if df['PTID'].nunique() != len(df):
            errors.append(f"{name} split has duplicate PTIDs!")

    # 2. No subject leakage
    train_ptids = set(train_df['PTID'])
    val_ptids = set(val_df['PTID'])
    test_ptids = set(test_df['PTID'])

    if len(train_ptids.intersection(val_ptids)) > 0:
        errors.append("Leakage: Train and Validation sets overlap.")
    if len(train_ptids.intersection(test_ptids)) > 0:
        errors.append("Leakage: Train and Test sets overlap.")
    if len(val_ptids.intersection(test_ptids)) > 0:
        errors.append("Leakage: Validation and Test sets overlap.")

    # 3 & 4. Covered by #1 (since there's exactly 1 row per PTID, no row multiplication)
    
    # 5. Valid target labels
    valid_targets = {'CN', 'MCI', 'AD'}
    actual_targets = set(full_df['target'].unique())
    if not actual_targets.issubset(valid_targets):
        errors.append(f"Invalid target labels found: {actual_targets - valid_targets}")

    # 6. No missing target labels
    if full_df['target'].isna().sum() > 0:
        errors.append("Missing target labels found.")

    # 7 & 9 Covered by missingness report

    # 10. Impossible age values
    if full_df['AGE'].min() < 40 or full_df['AGE'].max() > 120:
        errors.append(f"Suspicious age values detected: Min {full_df['AGE'].min()}, Max {full_df['AGE'].max()}")

    # 11. Duplicate records
    if full_df.duplicated().sum() > 0:
        errors.append("Exact duplicate records found in full dataset.")

    # 13. Leakage variables absent
    leakage_vars = ['DXCHANGE', 'DXCURREN', 'DXBL', 'EXAMDATE', 'VISDATE', 'VISCODE', 'RID']
    found_leaks = [v for v in leakage_vars if v in full_df.columns]
    if found_leaks:
        errors.append(f"Leakage variables found in final dataset: {found_leaks}")

    if errors:
        print("VALIDATION FAILED:")
        for e in errors:
            print(" -", e)
        sys.exit(1)
    else:
        print("VALIDATION PASSED! All conditions strictly met.")

if __name__ == "__main__":
    main()

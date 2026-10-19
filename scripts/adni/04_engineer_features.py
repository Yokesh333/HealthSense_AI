import os
import pandas as pd
import numpy as np

def main():
    base_dir = r"C:\Users\Yokesh\Desktop\Health_Sense AI"
    processed_dir = os.path.join(base_dir, "data", "processed", "adni")
    raw_path = os.path.join(processed_dir, "adni_merged_raw.csv")
    output_path = os.path.join(processed_dir, "adni_baseline_clean.csv")
    dict_path = os.path.join(processed_dir, "feature_dictionary.csv")
    missing_path = os.path.join(processed_dir, "missingness_report.csv")

    df = pd.read_csv(raw_path, low_memory=False)

    # Calculate AGE
    df['VISDATE'] = pd.to_datetime(df['VISDATE'], errors='coerce')
    df['PTDOBYY'] = pd.to_datetime(df['PTDOBYY'], errors='coerce')
    df['AGE'] = (df['VISDATE'] - df['PTDOBYY']).dt.days / 365.25

    # Replace -4.0 (ADNI missing code) with NaN for numerical/categorical features
    cols_to_clean = ['PTEDUCAT', 'TOTSCORE', 'CDGLOBAL', 'FAQTOTAL', 'MMSCORE', 'MOCA', 'PTGENDER', 'PTRACCAT', 'PTETHCAT']
    for c in cols_to_clean:
        df[c] = df[c].replace([-4, -4.0, '-4', '-4.0'], np.nan)

    # Encode categorical variables as requested (keep interpretable)
    # PTGENDER: 1=Male, 2=Female
    gender_map = {1.0: "Male", 2.0: "Female"}
    df['SEX'] = df['PTGENDER'].map(gender_map)

    # PTRACCAT: 1=Am Indian/Alaskan, 2=Asian, 3=Hawaiian/Pac Isl, 4=Black, 5=White, 6=More than one, 7=Unknown
    race_map = {
        '1': "Am Indian/Alaskan", '1.0': "Am Indian/Alaskan",
        '2': "Asian", '2.0': "Asian",
        '3': "Hawaiian/Pac Isl", '3.0': "Hawaiian/Pac Isl",
        '4': "Black", '4.0': "Black",
        '5': "White", '5.0': "White",
        '6': "More than one", '6.0': "More than one",
        '7': "Unknown", '7.0': "Unknown",
    }
    df['RACE'] = df['PTRACCAT'].astype(str).map(race_map)

    # PTETHCAT: 1=Hispanic, 2=Not Hispanic, 3=Unknown
    eth_map = {1.0: "Hispanic", 2.0: "Not Hispanic", 3.0: "Unknown"}
    df['ETHNICITY'] = df['PTETHCAT'].map(eth_map)

    # Select final columns
    final_cols = [
        'PTID', 'target', 'AGE', 'SEX', 'PTEDUCAT', 'RACE', 'ETHNICITY',
        'TOTSCORE', 'CDGLOBAL', 'FAQTOTAL', 'MMSCORE', 'MOCA'
    ]
    df = df[final_cols]
    
    # Rename columns for clarity
    df = df.rename(columns={
        'PTEDUCAT': 'EDUCATION',
        'TOTSCORE': 'ADAS',
        'CDGLOBAL': 'CDR',
        'FAQTOTAL': 'FAQ',
        'MMSCORE': 'MMSE'
    })

    # Save Missingness Report
    missing_report = pd.DataFrame({
        'feature': df.columns,
        'total_rows': len(df),
        'missing_count': df.isna().sum().values,
        'missing_percentage': (df.isna().sum().values / len(df)) * 100,
        'data_type': df.dtypes.astype(str).values
    })
    missing_report.to_csv(missing_path, index=False)

    # Save feature dictionary
    feat_dict = [
        {"feature_name": "PTID", "source_file": "DXSUM", "source_column": "PTID", "description": "Patient ID", "feature_type": "IDENTIFIER", "baseline_only": "Yes", "possible_leakage": "No", "missing_percentage": 0, "included_in_model": "No", "reason_for_inclusion/exclusion": "Identifier"},
        {"feature_name": "target", "source_file": "DXSUM", "source_column": "DIAGNOSIS", "description": "Diagnosis target (CN, MCI, AD)", "feature_type": "TARGET", "baseline_only": "Yes", "possible_leakage": "No", "missing_percentage": missing_report.loc[missing_report['feature']=='target', 'missing_percentage'].values[0], "included_in_model": "Yes", "reason_for_inclusion/exclusion": "Target variable"},
        {"feature_name": "AGE", "source_file": "PTDEMOG", "source_column": "VISDATE - PTDOBYY", "description": "Age at baseline", "feature_type": "PREDICTOR", "baseline_only": "Yes", "possible_leakage": "No", "missing_percentage": missing_report.loc[missing_report['feature']=='AGE', 'missing_percentage'].values[0], "included_in_model": "Yes", "reason_for_inclusion/exclusion": "Core demographic"},
        {"feature_name": "SEX", "source_file": "PTDEMOG", "source_column": "PTGENDER", "description": "Biological sex", "feature_type": "PREDICTOR", "baseline_only": "Yes", "possible_leakage": "No", "missing_percentage": missing_report.loc[missing_report['feature']=='SEX', 'missing_percentage'].values[0], "included_in_model": "Yes", "reason_for_inclusion/exclusion": "Core demographic"},
        {"feature_name": "EDUCATION", "source_file": "PTDEMOG", "source_column": "PTEDUCAT", "description": "Years of education", "feature_type": "PREDICTOR", "baseline_only": "Yes", "possible_leakage": "No", "missing_percentage": missing_report.loc[missing_report['feature']=='EDUCATION', 'missing_percentage'].values[0], "included_in_model": "Yes", "reason_for_inclusion/exclusion": "Core demographic"},
        {"feature_name": "RACE", "source_file": "PTDEMOG", "source_column": "PTRACCAT", "description": "Patient race", "feature_type": "PREDICTOR", "baseline_only": "Yes", "possible_leakage": "No", "missing_percentage": missing_report.loc[missing_report['feature']=='RACE', 'missing_percentage'].values[0], "included_in_model": "Yes", "reason_for_inclusion/exclusion": "Core demographic"},
        {"feature_name": "ETHNICITY", "source_file": "PTDEMOG", "source_column": "PTETHCAT", "description": "Patient ethnicity", "feature_type": "PREDICTOR", "baseline_only": "Yes", "possible_leakage": "No", "missing_percentage": missing_report.loc[missing_report['feature']=='ETHNICITY', 'missing_percentage'].values[0], "included_in_model": "Yes", "reason_for_inclusion/exclusion": "Core demographic"},
        {"feature_name": "ADAS", "source_file": "ADAS.csv", "source_column": "TOTSCORE", "description": "ADAS-Cog Score", "feature_type": "PREDICTOR", "baseline_only": "Yes", "possible_leakage": "No", "missing_percentage": missing_report.loc[missing_report['feature']=='ADAS', 'missing_percentage'].values[0], "included_in_model": "Yes", "reason_for_inclusion/exclusion": "Core cognitive test"},
        {"feature_name": "CDR", "source_file": "CDR.csv", "source_column": "CDGLOBAL", "description": "Clinical Dementia Rating", "feature_type": "PREDICTOR", "baseline_only": "Yes", "possible_leakage": "No", "missing_percentage": missing_report.loc[missing_report['feature']=='CDR', 'missing_percentage'].values[0], "included_in_model": "Yes", "reason_for_inclusion/exclusion": "Core cognitive test"},
        {"feature_name": "FAQ", "source_file": "FAQ.csv", "source_column": "FAQTOTAL", "description": "Functional Assessment Questionnaire", "feature_type": "PREDICTOR", "baseline_only": "Yes", "possible_leakage": "No", "missing_percentage": missing_report.loc[missing_report['feature']=='FAQ', 'missing_percentage'].values[0], "included_in_model": "Yes", "reason_for_inclusion/exclusion": "Core functional test"},
        {"feature_name": "MMSE", "source_file": "MMSE.csv", "source_column": "MMSCORE", "description": "Mini-Mental State Exam", "feature_type": "PREDICTOR", "baseline_only": "Yes", "possible_leakage": "No", "missing_percentage": missing_report.loc[missing_report['feature']=='MMSE', 'missing_percentage'].values[0], "included_in_model": "Yes", "reason_for_inclusion/exclusion": "Core cognitive test"},
        {"feature_name": "MOCA", "source_file": "MOCA.csv", "source_column": "MOCA", "description": "Montreal Cognitive Assessment", "feature_type": "PREDICTOR", "baseline_only": "Yes", "possible_leakage": "No", "missing_percentage": missing_report.loc[missing_report['feature']=='MOCA', 'missing_percentage'].values[0], "included_in_model": "Yes", "reason_for_inclusion/exclusion": "Core cognitive test"}
    ]
    pd.DataFrame(feat_dict).to_csv(dict_path, index=False)

    df.to_csv(output_path, index=False)
    print(f"Engineered features saved to {output_path}")
    print("Missingness summary:")
    print(df.isna().sum())

if __name__ == "__main__":
    main()

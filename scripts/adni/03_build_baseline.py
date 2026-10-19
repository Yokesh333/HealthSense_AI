import os
import pandas as pd

def load_cog(filename, score_col):
    path = os.path.join(r"C:\Users\Yokesh\Desktop\Health_Sense AI\Datasets\ADNI\Cognitive Assessment", filename)
    df = pd.read_csv(path, low_memory=False)
    # Filter to baseline
    df_bl = df[df['VISCODE'].isin(['bl', 'sc'])].copy()
    # Keep needed columns
    df_bl = df_bl[['PTID', 'VISCODE', score_col]]
    # Handle duplicates by taking the latest/first valid
    df_bl = df_bl.dropna(subset=[score_col])
    df_bl = df_bl.drop_duplicates(subset=['PTID'], keep='first')
    df_bl = df_bl.drop(columns=['VISCODE'])
    return df_bl

def main():
    base_dir = r"C:\Users\Yokesh\Desktop\Health_Sense AI"
    processed_dir = os.path.join(base_dir, "data", "processed", "adni")
    adni_dir = os.path.join(base_dir, "Datasets", "ADNI")

    dx_path = os.path.join(processed_dir, "adni_dx_baseline.csv")
    demo_path = os.path.join(adni_dir, "PTDEMOG_31Aug2026.csv")
    output_path = os.path.join(processed_dir, "adni_merged_raw.csv")

    df_dx = pd.read_csv(dx_path)
    
    # Demographics
    df_demo = pd.read_csv(demo_path, low_memory=False)
    df_demo_bl = df_demo[df_demo['VISCODE'].isin(['sc', 'bl'])].copy()
    df_demo_bl = df_demo_bl[['PTID', 'PTGENDER', 'PTEDUCAT', 'PTRACCAT', 'PTETHCAT', 'VISDATE', 'PTDOBYY']]
    df_demo_bl = df_demo_bl.drop_duplicates(subset=['PTID'], keep='first')

    # Load cognitive
    adas = load_cog("ADAS_28Jul2026.csv", "TOTSCORE")
    cdr = load_cog("CDR_28Jul2026.csv", "CDGLOBAL")
    faq = load_cog("FAQ_28Jul2026.csv", "FAQTOTAL")
    mmse = load_cog("MMSE_28Jul2026.csv", "MMSCORE")
    moca = load_cog("MOCA_28Jul2026.csv", "MOCA")

    # Merge
    merged = pd.merge(df_dx, df_demo_bl, on='PTID', how='inner')
    merged = pd.merge(merged, adas, on='PTID', how='left')
    merged = pd.merge(merged, cdr, on='PTID', how='left')
    merged = pd.merge(merged, faq, on='PTID', how='left')
    merged = pd.merge(merged, mmse, on='PTID', how='left')
    merged = pd.merge(merged, moca, on='PTID', how='left')

    assert merged['PTID'].nunique() == len(merged), "Row multiplication occurred!"

    merged.to_csv(output_path, index=False)
    print(f"Merged raw baseline data saved to {output_path}. Subjects: {len(merged)}")

if __name__ == "__main__":
    main()

import os
import pandas as pd
import pyreadr

def main():
    adni_dir = r"C:\Users\Yokesh\Desktop\Health_Sense AI\Datasets\ADNI"
    extract_dir = r"C:\Users\Yokesh\Desktop\Health_Sense AI\scratch\temp_extract\ADNIMERGE2\data"
    output_path = r"C:\Users\Yokesh\Desktop\Health_Sense AI\data\processed\adni\ADNI_SOURCE_INSPECTION_REPORT.txt"

    with open(output_path, "w") as f:
        f.write("ADNI Source Inspection Report\n")
        f.write("=============================\n\n")

        # Inspect DXSUM
        dxsum_path = os.path.join(extract_dir, "DXSUM.rda")
        rda = pyreadr.read_r(dxsum_path)
        dxsum = list(rda.values())[0]
        f.write(f"--- DXSUM.rda ---\n")
        f.write(f"Rows: {len(dxsum)}\n")
        f.write(f"Unique PTIDs: {dxsum['PTID'].nunique()}\n")
        f.write(f"VISCODE counts:\n{dxsum['VISCODE'].value_counts().head(5)}\n")
        f.write(f"DIAGNOSIS distribution:\n{dxsum['DIAGNOSIS'].value_counts(dropna=False)}\n\n")

        # Inspect PTDEMOG
        ptdemog_path = os.path.join(adni_dir, "PTDEMOG_31Aug2026.csv")
        ptdemog = pd.read_csv(ptdemog_path, low_memory=False)
        f.write(f"--- PTDEMOG_31Aug2026.csv ---\n")
        f.write(f"Rows: {len(ptdemog)}\n")
        f.write(f"Unique PTIDs: {ptdemog['PTID'].nunique()}\n")
        f.write(f"VISCODE counts:\n{ptdemog['VISCODE'].value_counts().head(5)}\n\n")

        # Inspect BLCHANGE
        blchange_path = os.path.join(adni_dir, "BLCHANGE_31Aug2026.csv")
        blchange = pd.read_csv(blchange_path, low_memory=False)
        f.write(f"--- BLCHANGE_31Aug2026.csv ---\n")
        f.write(f"Rows: {len(blchange)}\n")
        f.write(f"Unique PTIDs: {blchange['PTID'].nunique()}\n")
        f.write(f"VISCODE counts:\n{blchange['VISCODE'].value_counts().head(5)}\n\n")

    print("Source inspection complete. Report saved.")

if __name__ == "__main__":
    main()

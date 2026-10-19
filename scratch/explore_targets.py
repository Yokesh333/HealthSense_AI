import pandas as pd
import os

adni_dir = r"C:\Users\Yokesh\Desktop\Health_Sense AI\Datasets\ADNI"

reg_path = os.path.join(adni_dir, "Enrollment", "REGISTRY_28Jul2026.csv")
arm_path = os.path.join(adni_dir, "Enrollment", "ARM_28Jul2026.csv")
adas_path = os.path.join(adni_dir, "Cognitive Assessment", "ADAS_28Jul2026.csv")

if os.path.exists(reg_path):
    df_reg = pd.read_csv(reg_path)
    print("REGISTRY.csv Shape:", df_reg.shape)
    if 'PTSTATUS' in df_reg.columns:
        print("PTSTATUS value counts:\n", df_reg['PTSTATUS'].value_counts(dropna=False))
    if 'RGSTATUS' in df_reg.columns:
        print("RGSTATUS value counts:\n", df_reg['RGSTATUS'].value_counts(dropna=False))
    if 'VISCODE' in df_reg.columns:
        print("REGISTRY VISCODE value counts:\n", df_reg['VISCODE'].value_counts(dropna=False).head(10))

if os.path.exists(arm_path):
    df_arm = pd.read_csv(arm_path)
    print("\nARM.csv Shape:", df_arm.shape)
    if 'ARM' in df_arm.columns:
        print("ARM value counts:\n", df_arm['ARM'].value_counts(dropna=False))
    if 'VISCODE' in df_arm.columns:
        print("ARM VISCODE value counts:\n", df_arm['VISCODE'].value_counts(dropna=False).head(10))

if os.path.exists(adas_path):
    df_adas = pd.read_csv(adas_path)
    print("\nADAS.csv Shape:", df_adas.shape)
    if 'VISCODE' in df_adas.columns:
        print("ADAS VISCODE value counts:\n", df_adas['VISCODE'].value_counts(dropna=False).head(10))
    if 'VISCODE2' in df_adas.columns:
        print("ADAS VISCODE2 value counts:\n", df_adas['VISCODE2'].value_counts(dropna=False).head(10))


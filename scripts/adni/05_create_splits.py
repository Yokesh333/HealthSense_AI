import os
import pandas as pd
import numpy as np

def main():
    base_dir = r"C:\Users\Yokesh\Desktop\Health_Sense AI"
    processed_dir = os.path.join(base_dir, "data", "processed", "adni")
    input_path = os.path.join(processed_dir, "adni_baseline_clean.csv")
    
    df = pd.read_csv(input_path)

    assert df['PTID'].nunique() == len(df), "Row multiplication error before split."

    # Stratified split without sklearn
    # Group by target, shuffle, and take 70/15/15
    np.random.seed(42)
    
    train_dfs = []
    val_dfs = []
    test_dfs = []

    for tgt, group in df.groupby('target'):
        shuffled = group.sample(frac=1, random_state=42).reset_index(drop=True)
        n = len(shuffled)
        n_train = int(n * 0.7)
        n_val = int(n * 0.15)
        
        train_dfs.append(shuffled.iloc[:n_train])
        val_dfs.append(shuffled.iloc[n_train:n_train + n_val])
        test_dfs.append(shuffled.iloc[n_train + n_val:])
        
    train_df = pd.concat(train_dfs).sample(frac=1, random_state=42).reset_index(drop=True)
    val_df = pd.concat(val_dfs).sample(frac=1, random_state=42).reset_index(drop=True)
    test_df = pd.concat(test_dfs).sample(frac=1, random_state=42).reset_index(drop=True)

    # Save splits
    train_df.to_csv(os.path.join(processed_dir, "adni_train.csv"), index=False)
    val_df.to_csv(os.path.join(processed_dir, "adni_validation.csv"), index=False)
    test_df.to_csv(os.path.join(processed_dir, "adni_test.csv"), index=False)

    # Calculate class distributions
    dist = pd.DataFrame({
        'Train': train_df['target'].value_counts(),
        'Validation': val_df['target'].value_counts(),
        'Test': test_df['target'].value_counts()
    }).fillna(0).astype(int)

    dist.to_csv(os.path.join(processed_dir, "class_distribution.csv"))
    
    print("Splits created successfully.")
    print("\nClass Distributions:")
    print(dist)

if __name__ == "__main__":
    main()

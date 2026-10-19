import nbformat as nbf
import os

def create_notebook():
    nb = nbf.v4.new_notebook()
    
    cells = []
    
    # Instructions
    cells.append(nbf.v4.new_markdown_cell("""# Phase 3: ADNI Machine Learning Training

**Google Colab Instructions**
STEP 1: Open this notebook in Google Colab.
STEP 2: Upload `adni_train.csv`, `adni_validation.csv`, and `adni_test.csv` to the session storage (`/content/`).
STEP 3: Run all cells sequentially.
STEP 4: Download `adni_model.joblib` and `model_metadata.json`.
STEP 5: Place them into `models/` of the HealthSense AI project.

**Medical/Research Limitations**
- This is a research/prototype ML classifier. It is not a medical diagnosis.
- ADNI has study-specific selection characteristics.
- The dataset contains only 1,641 baseline subjects in this pipeline.
- The classes are imbalanced.
- MOCA has approximately 58.9% missingness. Missingness may relate to ADNI study phase.
- The project operationally maps Dementia → AD. This mapping does not mean every Dementia record is pathologically confirmed Alzheimer's disease.
- External validation on an independent dataset has not yet been performed. Performance on this dataset does not establish clinical utility.
"""))

    # 1. Environment Setup
    cells.append(nbf.v4.new_markdown_cell("## 1. Environment Setup"))
    cells.append(nbf.v4.new_code_cell("""DATA_DIR = '/content/'
import os
print(f"Data directory: {DATA_DIR}")
"""))

    # 2. Package Installation
    cells.append(nbf.v4.new_markdown_cell("## 2. Package Installation"))
    cells.append(nbf.v4.new_code_cell("""!pip install xgboost shap imbalanced-learn -q"""))

    # 3. Imports
    cells.append(nbf.v4.new_markdown_cell("## 3. Imports"))
    cells.append(nbf.v4.new_code_cell("""import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import json
import shap
from datetime import datetime

from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from xgboost import XGBClassifier
from sklearn.model_selection import StratifiedKFold, GridSearchCV
from sklearn.metrics import accuracy_score, balanced_accuracy_score, precision_recall_fscore_support, classification_report, confusion_matrix, ConfusionMatrixDisplay, roc_auc_score

import warnings
warnings.filterwarnings('ignore')
"""))

    # 4. Dataset Upload / Loading
    cells.append(nbf.v4.new_markdown_cell("## 4. Dataset Upload / Loading"))
    cells.append(nbf.v4.new_code_cell("""# Check files
expected_files = ['adni_train.csv', 'adni_validation.csv', 'adni_test.csv']
for f in expected_files:
    if not os.path.exists(os.path.join(DATA_DIR, f)):
        print(f"WARNING: {f} not found in {DATA_DIR}. Please upload it.")

train_df = pd.read_csv(os.path.join(DATA_DIR, 'adni_train.csv'))
val_df = pd.read_csv(os.path.join(DATA_DIR, 'adni_validation.csv'))
test_df = pd.read_csv(os.path.join(DATA_DIR, 'adni_test.csv'))

print(f"Train: {train_df.shape}")
print(f"Validation: {val_df.shape}")
print(f"Test: {test_df.shape}")
"""))

    # 5. Dataset Verification
    cells.append(nbf.v4.new_markdown_cell("## 5. Dataset Verification"))
    cells.append(nbf.v4.new_code_cell("""# Verify no overlap
train_ids = set(train_df['PTID'])
val_ids = set(val_df['PTID'])
test_ids = set(test_df['PTID'])

assert len(train_ids.intersection(val_ids)) == 0, "Leakage Train-Val"
assert len(train_ids.intersection(test_ids)) == 0, "Leakage Train-Test"
assert len(val_ids.intersection(test_ids)) == 0, "Leakage Val-Test"
print("Subject leakage verification passed.")
"""))

    # 6. Exploratory Data Analysis
    cells.append(nbf.v4.new_markdown_cell("## 6. Exploratory Data Analysis"))
    cells.append(nbf.v4.new_code_cell("""# Class distribution
print("Train Class Distribution:")
print(train_df['target'].value_counts())
sns.countplot(data=train_df, x='target', order=['CN', 'MCI', 'AD'])
plt.title('Train Target Distribution')
plt.show()
"""))

    # 7. Missing Data Analysis
    cells.append(nbf.v4.new_markdown_cell("## 7. Missing Data Analysis"))
    cells.append(nbf.v4.new_code_cell("""print("Missing data in Train:")
print(train_df.isna().sum())
print(f"\\nMOCA missing percentage: {train_df['MOCA'].isna().mean()*100:.2f}%")
"""))

    # 8. Feature and Target Separation
    cells.append(nbf.v4.new_markdown_cell("## 8. Feature and Target Separation"))
    cells.append(nbf.v4.new_code_cell("""numeric_features = ['AGE', 'EDUCATION', 'ADAS', 'CDR', 'FAQ', 'MMSE', 'MOCA']
numeric_features_no_moca = ['AGE', 'EDUCATION', 'ADAS', 'CDR', 'FAQ', 'MMSE']
categorical_features = ['SEX', 'RACE', 'ETHNICITY']
features = numeric_features + categorical_features
features_no_moca = numeric_features_no_moca + categorical_features

X_train = train_df[features]
y_train = train_df['target']

X_val = val_df[features]
y_val = val_df['target']

X_test = test_df[features]
y_test = test_df['target']

X_train_no_moca = train_df[features_no_moca]
X_val_no_moca = val_df[features_no_moca]
X_test_no_moca = test_df[features_no_moca]

target_map = {'CN': 0, 'MCI': 1, 'AD': 2}
y_train_enc = y_train.map(target_map)
y_val_enc = y_val.map(target_map)
y_test_enc = y_test.map(target_map)
"""))

    # 9. Preprocessing Pipeline
    cells.append(nbf.v4.new_markdown_cell("## 9. Preprocessing Pipeline"))
    cells.append(nbf.v4.new_code_cell("""def get_preprocessor(num_cols, cat_cols):
    numeric_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median', add_indicator=True)),
        ('scaler', StandardScaler())
    ])

    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='constant', fill_value='Unknown')),
        ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, num_cols),
            ('cat', categorical_transformer, cat_cols)
        ])
    return preprocessor

preprocessor_with_moca = get_preprocessor(numeric_features, categorical_features)
preprocessor_no_moca = get_preprocessor(numeric_features_no_moca, categorical_features)
"""))

    # 10. Baseline Model Training
    cells.append(nbf.v4.new_markdown_cell("## 10. Baseline Model Training"))
    cells.append(nbf.v4.new_code_cell("""models = {
    'Logistic Regression': LogisticRegression(class_weight='balanced', random_state=42, max_iter=1000),
    'Random Forest': RandomForestClassifier(class_weight='balanced', random_state=42),
    'SVM': SVC(class_weight='balanced', probability=True, random_state=42),
    'XGBoost': XGBClassifier(random_state=42, eval_metric='mlogloss')
}

def evaluate_model(y_true, y_pred, y_prob):
    acc = accuracy_score(y_true, y_pred)
    bacc = balanced_accuracy_score(y_true, y_pred)
    precision, recall, f1, _ = precision_recall_fscore_support(y_true, y_pred, average=None)
    macro_p, macro_r, macro_f1, _ = precision_recall_fscore_support(y_true, y_pred, average='macro')
    weighted_p, weighted_r, weighted_f1, _ = precision_recall_fscore_support(y_true, y_pred, average='weighted')
    
    auc_macro = roc_auc_score(y_true, y_prob, multi_class='ovr', average='macro') if y_prob is not None else None
    
    return {
        'Accuracy': acc, 'Balanced Accuracy': bacc,
        'Macro Precision': macro_p, 'Macro Recall': macro_r, 'Macro F1': macro_f1,
        'Weighted F1': weighted_f1, 'ROC-AUC Macro': auc_macro,
        'CN Precision': precision[0], 'CN Recall': recall[0], 'CN F1': f1[0],
        'MCI Precision': precision[1], 'MCI Recall': recall[1], 'MCI F1': f1[1],
        'AD Precision': precision[2], 'AD Recall': recall[2], 'AD F1': f1[2]
    }
"""))

    # 11. Cross-Validation
    cells.append(nbf.v4.new_markdown_cell("## 11. Cross-Validation & 12. Hyperparameter Tuning"))
    cells.append(nbf.v4.new_code_cell("""cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

param_grids = {
    'Logistic Regression': {'classifier__C': [0.1, 1, 10]},
    'Random Forest': {'classifier__n_estimators': [100, 200], 'classifier__max_depth': [None, 5, 10]},
    'SVM': {'classifier__C': [0.1, 1, 10], 'classifier__kernel': ['linear', 'rbf']},
    'XGBoost': {'classifier__n_estimators': [100, 200], 'classifier__max_depth': [3, 5], 'classifier__learning_rate': [0.01, 0.1]}
}

best_estimators = {}
best_scores = {}

for name, clf in models.items():
    print(f"Tuning {name}...")
    pipeline = Pipeline(steps=[('preprocessor', preprocessor_with_moca), ('classifier', clf)])
    grid = GridSearchCV(pipeline, param_grids[name], cv=cv, scoring='f1_macro', n_jobs=-1)
    grid.fit(X_train, y_train_enc)
    best_estimators[name] = grid.best_estimator_
    best_scores[name] = grid.best_score_
    print(f"Best CV Macro F1 for {name}: {grid.best_score_:.4f}")
"""))

    # 13. Validation Evaluation & 14. Model Comparison
    cells.append(nbf.v4.new_markdown_cell("## 13. Validation Evaluation & 14. Model Comparison"))
    cells.append(nbf.v4.new_code_cell("""val_results = []
for name, estimator in best_estimators.items():
    y_val_pred = estimator.predict(X_val)
    y_val_prob = estimator.predict_proba(X_val) if hasattr(estimator, 'predict_proba') else None
    res = evaluate_model(y_val_enc, y_val_pred, y_val_prob)
    res['Model'] = name
    val_results.append(res)

val_df_results = pd.DataFrame(val_results).set_index('Model')
display(val_df_results[['Macro F1', 'AD Recall', 'Accuracy', 'Balanced Accuracy']])
"""))

    # 15. Final Model Selection
    cells.append(nbf.v4.new_markdown_cell("## 15. Final Model Selection"))
    cells.append(nbf.v4.new_code_cell("""# Select based on Macro F1 on validation set
best_model_name = val_df_results['Macro F1'].idxmax()
final_model = best_estimators[best_model_name]
print(f"Selected Final Model: {best_model_name}")
"""))

    # 16. Final Test Evaluation & 17. Confusion Matrix
    cells.append(nbf.v4.new_markdown_cell("## 16. Final Test Evaluation & 17. Confusion Matrix"))
    cells.append(nbf.v4.new_code_cell("""print("FINAL TEST RESULTS")
y_test_pred = final_model.predict(X_test)
y_test_prob = final_model.predict_proba(X_test) if hasattr(final_model, 'predict_proba') else None

test_res = evaluate_model(y_test_enc, y_test_pred, y_test_prob)
for k, v in test_res.items():
    print(f"{k}: {v:.4f}" if v is not None else f"{k}: None")

cm = confusion_matrix(y_test_enc, y_test_pred)
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=['CN', 'MCI', 'AD'])
disp.plot(cmap='Blues')
plt.title(f"Final Test Confusion Matrix ({best_model_name})")
plt.savefig('confusion_matrix.png')
plt.show()
"""))

    # 22. MOCA Ablation Experiment
    cells.append(nbf.v4.new_markdown_cell("## 22. MOCA Ablation Experiment"))
    cells.append(nbf.v4.new_code_cell("""print("Training model WITHOUT MOCA...")
clf_no_moca = models[best_model_name]
pipeline_no_moca = Pipeline(steps=[('preprocessor', preprocessor_no_moca), ('classifier', clf_no_moca)])
pipeline_no_moca.fit(X_train_no_moca, y_train_enc)
y_test_pred_no_moca = pipeline_no_moca.predict(X_test_no_moca)
test_res_no_moca = evaluate_model(y_test_enc, y_test_pred_no_moca, None)

print(f"WITH MOCA    - Macro F1: {test_res['Macro F1']:.4f}, AD Recall: {test_res['AD Recall']:.4f}")
print(f"WITHOUT MOCA - Macro F1: {test_res_no_moca['Macro F1']:.4f}, AD Recall: {test_res_no_moca['AD Recall']:.4f}")
"""))

    # 18. Feature Importance / SHAP
    cells.append(nbf.v4.new_markdown_cell("## 18. Feature Importance / SHAP"))
    cells.append(nbf.v4.new_code_cell("""# Extract feature names from preprocessor
try:
    cat_enc = final_model.named_steps['preprocessor'].named_transformers_['cat'].named_steps['onehot']
    cat_names = cat_enc.get_feature_names_out(categorical_features)
    
    # Num names + missing indicators
    num_imp = final_model.named_steps['preprocessor'].named_transformers_['num'].named_steps['imputer']
    indicator_cols = [numeric_features[i] + '_is_missing' for i in num_imp.indicator_.features_]
    num_names = numeric_features + indicator_cols
    
    feature_names = list(num_names) + list(cat_names)
    
    # Feature Importance for tree models
    if hasattr(final_model.named_steps['classifier'], 'feature_importances_'):
        importances = final_model.named_steps['classifier'].feature_importances_
        indices = np.argsort(importances)[::-1]
        
        plt.figure(figsize=(10, 6))
        plt.title("Feature Importances")
        plt.bar(range(len(importances)), importances[indices], align="center")
        plt.xticks(range(len(importances)), [feature_names[i] for i in indices], rotation=90)
        plt.tight_layout()
        plt.savefig('feature_importance.png')
        plt.show()
except Exception as e:
    print(f"Could not generate feature names/importance: {e}")
"""))

    # 19. Final Model Export
    cells.append(nbf.v4.new_markdown_cell("## 19. Final Model Export & 20. Metadata Export"))
    cells.append(nbf.v4.new_code_cell("""joblib.dump(final_model, 'adni_model.joblib')

metadata = {
  "project_name": "HealthSense AI",
  "model_name": best_model_name,
  "model_version": "1.0",
  "training_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
  "target_name": "target",
  "target_classes": ["CN", "MCI", "AD"],
  "feature_names": features,
  "categorical_features": categorical_features,
  "numerical_features": numeric_features,
  "training_samples": len(X_train),
  "validation_samples": len(X_val),
  "test_samples": len(X_test),
  "selected_metric": "Macro F1",
  "test_metrics": test_res,
  "preprocessing_description": "Median imputation with missing indicators for numericals. Constant imputation with OneHotEncoding for categoricals. StandardScaler applied to numericals.",
  "missing_value_strategy": "SimpleImputer(strategy='median', add_indicator=True)",
  "random_seed": 42,
  "diagnosis_mapping": {
      "CN": "CN",
      "MCI": "MCI",
      "Dementia": "AD"
  },
  "limitations": "Prototype ML classifier, not clinical diagnosis. AD class mapped from Dementia. MOCA has ~58% missingness."
}

with open('model_metadata.json', 'w') as f:
    json.dump(metadata, f, indent=4)
print("Saved adni_model.joblib and model_metadata.json")
"""))

    # 21. Reload Verification
    cells.append(nbf.v4.new_markdown_cell("## 21. Reload Verification & 22. Example Backend Inference"))
    cells.append(nbf.v4.new_code_cell("""loaded_model = joblib.load('adni_model.joblib')

sample = pd.DataFrame([{
    "AGE": 72.0, "SEX": "Male", "EDUCATION": 16.0, "RACE": "White", "ETHNICITY": "Not Hispanic",
    "ADAS": 12.5, "CDR": 0.5, "FAQ": 5.0, "MMSE": 27.0, "MOCA": 22.0
}])

pred_enc = loaded_model.predict(sample)[0]
prob = loaded_model.predict_proba(sample)[0] if hasattr(loaded_model, 'predict_proba') else None

class_names = ["CN", "MCI", "AD"]
pred_class = class_names[pred_enc]

result = {
    "prediction": pred_class,
    "probabilities": {class_names[i]: float(prob[i]) for i in range(len(class_names))} if prob is not None else None
}
import json
print(json.dumps(result, indent=2))
print("Reload verification successful!")
"""))

    nb['cells'] = cells
    
    with open(r'C:\Users\Yokesh\Desktop\Health_Sense AI\notebooks\Phase3_ADNI_ML_Training.ipynb', 'w', encoding='utf-8') as f:
        nbf.write(nb, f)
    
    print("Generated Notebook Phase3_ADNI_ML_Training.ipynb")

if __name__ == '__main__':
    create_notebook()

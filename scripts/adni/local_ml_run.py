import os
import pandas as pd
import numpy as np
import joblib
import json
from datetime import datetime

from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.model_selection import StratifiedKFold, GridSearchCV
from sklearn.metrics import accuracy_score, balanced_accuracy_score, precision_recall_fscore_support, classification_report

def main():
    base_dir = r"C:\Users\Yokesh\Desktop\Health_Sense AI"
    data_dir = os.path.join(base_dir, "data", "processed", "adni")
    models_dir = os.path.join(base_dir, "models")
    reports_dir = os.path.join(base_dir, "training_reports")

    train_df = pd.read_csv(os.path.join(data_dir, 'adni_train.csv'))
    val_df = pd.read_csv(os.path.join(data_dir, 'adni_validation.csv'))
    test_df = pd.read_csv(os.path.join(data_dir, 'adni_test.csv'))

    numeric_features = ['AGE', 'EDUCATION', 'ADAS', 'CDR', 'FAQ', 'MMSE', 'MOCA']
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
    X_test_no_moca = test_df[features_no_moca]

    target_map = {'CN': 0, 'MCI': 1, 'AD': 2}
    y_train_enc = y_train.map(target_map)
    y_val_enc = y_val.map(target_map)
    y_test_enc = y_test.map(target_map)

    def get_preprocessor(num_cols):
        return ColumnTransformer(transformers=[
            ('num', Pipeline([
                ('imputer', SimpleImputer(strategy='median', add_indicator=True)),
                ('scaler', StandardScaler())
            ]), num_cols),
            ('cat', Pipeline([
                ('imputer', SimpleImputer(strategy='constant', fill_value='Unknown')),
                ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
            ]), categorical_features)
        ])

    preprocessor_with_moca = get_preprocessor(numeric_features)
    preprocessor_no_moca = get_preprocessor(numeric_features_no_moca)

    models = {
        'Logistic Regression': LogisticRegression(class_weight='balanced', random_state=42),
        'Random Forest': RandomForestClassifier(n_estimators=50, class_weight='balanced', random_state=42)
    }

    # Extremely lightweight grid search just to run
    cv = StratifiedKFold(n_splits=2, shuffle=True, random_state=42)
    param_grids = {
        'Logistic Regression': {'classifier__C': [1]},
        'Random Forest': {'classifier__max_depth': [5]}
    }

    best_estimators = {}
    val_results = []

    for name, clf in models.items():
        pipeline = Pipeline([('preprocessor', preprocessor_with_moca), ('classifier', clf)])
        grid = GridSearchCV(pipeline, param_grids[name], cv=cv, scoring='f1_macro')
        grid.fit(X_train, y_train_enc)
        best_estimators[name] = grid.best_estimator_

        # Eval on val
        y_val_pred = grid.predict(X_val)
        mac_f1 = precision_recall_fscore_support(y_val_enc, y_val_pred, average='macro')[2]
        acc = accuracy_score(y_val_enc, y_val_pred)
        val_results.append({'Model': name, 'Macro F1': mac_f1, 'Accuracy': acc})

    val_df_res = pd.DataFrame(val_results).set_index('Model')
    best_model_name = val_df_res['Macro F1'].idxmax()
    final_model = best_estimators[best_model_name]

    # Test Eval
    y_test_pred = final_model.predict(X_test)
    test_acc = accuracy_score(y_test_enc, y_test_pred)
    p, r, f, _ = precision_recall_fscore_support(y_test_enc, y_test_pred, average=None)
    mac_f = precision_recall_fscore_support(y_test_enc, y_test_pred, average='macro')[2]

    # No Moca experiment
    pipeline_no_moca = Pipeline([('preprocessor', preprocessor_no_moca), ('classifier', models[best_model_name])])
    pipeline_no_moca.fit(X_train_no_moca, y_train_enc)
    y_test_pred_no = pipeline_no_moca.predict(X_test_no_moca)
    mac_f_no = precision_recall_fscore_support(y_test_enc, y_test_pred_no, average='macro')[2]

    # Export
    joblib.dump(final_model, os.path.join(models_dir, 'adni_model.joblib'))
    
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
      "test_metrics": {"Accuracy": test_acc, "Macro F1": mac_f, "CN F1": f[0], "MCI F1": f[1], "AD F1": f[2], "AD Recall": r[2]},
      "missing_value_strategy": "SimpleImputer(strategy='median', add_indicator=True)",
      "random_seed": 42,
      "diagnosis_mapping": {"CN": "CN", "MCI": "MCI", "Dementia": "AD"},
      "limitations": "Prototype ML classifier, not clinical diagnosis."
    }
    with open(os.path.join(models_dir, 'model_metadata.json'), 'w') as f_out:
        json.dump(metadata, f_out, indent=4)

    # Save reports
    val_df_res.to_csv(os.path.join(reports_dir, 'model_comparison.csv'))
    pd.DataFrame(classification_report(y_test_enc, y_test_pred, target_names=['CN', 'MCI', 'AD'], output_dict=True)).transpose().to_csv(os.path.join(reports_dir, 'classification_report.csv'))
    
    report_md = f"""# ADNI Phase 3 Training Report
- Dataset: 1641 subjects
- Model selected: {best_model_name}
- Validation Macro F1: {val_df_res.loc[best_model_name, 'Macro F1']:.4f}
- Test Accuracy: {test_acc:.4f}
- Test Macro F1: {mac_f:.4f}
- CN F1: {f[0]:.4f}, MCI F1: {f[1]:.4f}, AD F1: {f[2]:.4f}
- AD Recall: {r[2]:.4f}
- MOCA Experiment: With MOCA Macro F1 = {mac_f:.4f} | Without MOCA Macro F1 = {mac_f_no:.4f}
"""
    with open(os.path.join(reports_dir, 'training_report.md'), 'w') as f_out:
        f_out.write(report_md)
        
    print(report_md)

if __name__ == '__main__':
    main()

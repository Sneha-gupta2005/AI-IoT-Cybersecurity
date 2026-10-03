import pandas as pd
import numpy as np
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, label_binarize
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
    confusion_matrix,
    classification_report
)

from xgboost import XGBClassifier


# ============================================================
# PATHS
# ============================================================

DATASET_PATH = "datasets/processed/ton_iot_network_processed.csv"

REPORT_PATH = "reports/ml_evaluation_report.txt"


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 70)
print("PROPER ML MODEL EVALUATION")
print("=" * 70)

print("\nLoading dataset...")

df = pd.read_csv(DATASET_PATH)

print("Dataset shape:", df.shape)


# ============================================================
# FEATURES
# ============================================================

X = df.drop(columns=["label", "attack_type"])

y_binary = df["label"]
y_attack_type = df["attack_type"]


# ============================================================
# TRAIN / TEST SPLIT
# ============================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y_binary,
    test_size=0.20,
    random_state=42,
    stratify=y_binary
)

print("\nTraining samples:", len(X_train))
print("Testing samples :", len(X_test))


# ============================================================
# SCALE
# ============================================================

scaler = StandardScaler()

X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)


# ============================================================
# BINARY MODEL
# ============================================================

print("\nTraining binary XGBoost model...")

negative_count = (y_train == 0).sum()
positive_count = (y_train == 1).sum()

scale_pos_weight = negative_count / positive_count

binary_model = XGBClassifier(
    n_estimators=300,
    max_depth=8,
    learning_rate=0.08,
    subsample=0.8,
    colsample_bytree=0.8,
    objective="binary:logistic",
    eval_metric="logloss",
    scale_pos_weight=scale_pos_weight,
    random_state=42,
    n_jobs=-1
)

binary_model.fit(
    X_train_scaled,
    y_train
)


# ============================================================
# BINARY PREDICTION
# ============================================================

binary_predictions = binary_model.predict(X_test_scaled)

binary_probabilities = binary_model.predict_proba(
    X_test_scaled
)[:, 1]


# ============================================================
# BINARY METRICS
# ============================================================

accuracy = accuracy_score(
    y_test,
    binary_predictions
)

precision = precision_score(
    y_test,
    binary_predictions
)

recall = recall_score(
    y_test,
    binary_predictions
)

f1 = f1_score(
    y_test,
    binary_predictions
)

roc_auc = roc_auc_score(
    y_test,
    binary_probabilities
)

pr_auc = average_precision_score(
    y_test,
    binary_probabilities
)

cm = confusion_matrix(
    y_test,
    binary_predictions
)

tn, fp, fn, tp = cm.ravel()

false_positive_rate = fp / (fp + tn)

false_negative_rate = fn / (fn + tp)


# ============================================================
# DISPLAY BINARY RESULTS
# ============================================================

print("\n")
print("=" * 70)
print("BINARY CYBER ATTACK DETECTION")
print("=" * 70)

print(f"\nAccuracy          : {accuracy:.4f}")
print(f"Precision         : {precision:.4f}")
print(f"Recall            : {recall:.4f}")
print(f"F1 Score          : {f1:.4f}")
print(f"ROC-AUC           : {roc_auc:.4f}")
print(f"PR-AUC            : {pr_auc:.4f}")
print(f"False Positive Rate: {false_positive_rate:.4f}")
print(f"False Negative Rate: {false_negative_rate:.4f}")

print("\nConfusion Matrix:")
print(cm)


# ============================================================
# MULTI-CLASS MODEL
# ============================================================

print("\n")
print("=" * 70)
print("MULTI-CLASS ATTACK TYPE CLASSIFICATION")
print("=" * 70)

attack_types = sorted(
    y_attack_type.unique()
)

attack_type_mapping = {
    attack_type: index
    for index, attack_type
    in enumerate(attack_types)
}

y_multi = y_attack_type.map(
    attack_type_mapping
)


# ------------------------------------------------------------
# Split using SAME indexes
# ------------------------------------------------------------

X_train_m, X_test_m, y_train_m, y_test_m = train_test_split(
    X,
    y_multi,
    test_size=0.20,
    random_state=42,
    stratify=y_multi
)


# ============================================================
# MULTI-CLASS MODEL
# ============================================================

multi_model = XGBClassifier(
    n_estimators=300,
    max_depth=8,
    learning_rate=0.08,
    subsample=0.8,
    colsample_bytree=0.8,
    objective="multi:softprob",
    num_class=len(attack_types),
    eval_metric="mlogloss",
    random_state=42,
    n_jobs=-1
)

multi_model.fit(
    X_train_m,
    y_train_m
)


# ============================================================
# MULTI-CLASS PREDICTION
# ============================================================

multi_predictions = multi_model.predict(
    X_test_m
)


# ============================================================
# MULTI-CLASS METRICS
# ============================================================

multi_accuracy = accuracy_score(
    y_test_m,
    multi_predictions
)

multi_precision = precision_score(
    y_test_m,
    multi_predictions,
    average="weighted",
    zero_division=0
)

multi_recall = recall_score(
    y_test_m,
    multi_predictions,
    average="weighted",
    zero_division=0
)

multi_f1 = f1_score(
    y_test_m,
    multi_predictions,
    average="weighted",
    zero_division=0
)


print(f"\nAccuracy          : {multi_accuracy:.4f}")
print(f"Precision         : {multi_precision:.4f}")
print(f"Recall            : {multi_recall:.4f}")
print(f"F1 Score          : {multi_f1:.4f}")

print("\nClassification Report:")

classification_report_text = classification_report(
    y_test_m,
    multi_predictions,
    target_names=attack_types,
    zero_division=0
)

print(classification_report_text)


print("\nConfusion Matrix:")

multi_cm = confusion_matrix(
    y_test_m,
    multi_predictions
)

print(multi_cm)


# ============================================================
# SAVE REPORT
# ============================================================

report = f"""
AI-BASED IOT CYBERSECURITY SYSTEM
ML EVALUATION REPORT
===============================================

Dataset
-------
TON-IoT Network Dataset

Dataset Shape:
{df.shape}

Binary Cyber Attack Detection
-----------------------------

Accuracy           : {accuracy:.4f}
Precision          : {precision:.4f}
Recall             : {recall:.4f}
F1 Score           : {f1:.4f}
ROC-AUC            : {roc_auc:.4f}
PR-AUC             : {pr_auc:.4f}

False Positive Rate: {false_positive_rate:.4f}
False Negative Rate: {false_negative_rate:.4f}

Confusion Matrix:
{cm}


Multi-Class Attack Classification
----------------------------------

Accuracy           : {multi_accuracy:.4f}
Precision          : {multi_precision:.4f}
Recall             : {multi_recall:.4f}
F1 Score           : {multi_f1:.4f}

Classification Report:

{classification_report_text}

Confusion Matrix:

{multi_cm}
"""


with open(
    REPORT_PATH,
    "w",
    encoding="utf-8"
) as file:

    file.write(report)


# ============================================================
# COMPLETE
# ============================================================

print("\n")
print("=" * 70)
print("EVALUATION COMPLETED")
print("=" * 70)

print("\nReport saved to:")
print(REPORT_PATH)
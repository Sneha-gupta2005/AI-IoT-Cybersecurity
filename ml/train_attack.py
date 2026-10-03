import pandas as pd
import numpy as np
import os
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
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
# CONFIGURATION
# ============================================================

DATASET_PATH = "datasets/processed/ton_iot_network_processed.csv"

MODEL_DIR = "ml/models"

MODEL_PATH = os.path.join(
    MODEL_DIR,
    "attack_model.joblib"
)

SCALER_PATH = os.path.join(
    MODEL_DIR,
    "attack_scaler.joblib"
)


# ============================================================
# START
# ============================================================

print("=" * 70)
print("TON-IOT CYBER ATTACK DETECTION - XGBOOST")
print("=" * 70)


# ============================================================
# LOAD DATASET
# ============================================================

print("\nLoading processed dataset...")

df = pd.read_csv(DATASET_PATH)

print("Dataset shape:", df.shape)


# ============================================================
# TARGET
# ============================================================

X = df.drop(
    columns=["label", "attack_type"]
)

y = df["label"]


print("\nFeatures:", X.shape[1])
print("Samples:", X.shape[0])


print("\nTarget distribution:")
print(y.value_counts())


# ============================================================
# TRAIN / TEST SPLIT
# ============================================================

print("\nCreating train/test split...")

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print("Training samples:", X_train.shape[0])
print("Testing samples:", X_test.shape[0])


# ============================================================
# FEATURE SCALING
# ============================================================

print("\nScaling features...")

scaler = StandardScaler()

X_train_scaled = scaler.fit_transform(X_train)

X_test_scaled = scaler.transform(X_test)


# ============================================================
# CALCULATE CLASS WEIGHT
# ============================================================

negative_count = (y_train == 0).sum()
positive_count = (y_train == 1).sum()

scale_pos_weight = negative_count / positive_count

print("\nClass weight:")
print("scale_pos_weight:", scale_pos_weight)


# ============================================================
# XGBOOST MODEL
# ============================================================

print("\nTraining XGBoost model...")

model = XGBClassifier(
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


model.fit(
    X_train_scaled,
    y_train
)


print("Training completed.")


# ============================================================
# PREDICTION
# ============================================================

print("\nGenerating predictions...")

y_pred = model.predict(
    X_test_scaled
)

y_probability = model.predict_proba(
    X_test_scaled
)[:, 1]


# ============================================================
# METRICS
# ============================================================

accuracy = accuracy_score(
    y_test,
    y_pred
)

precision = precision_score(
    y_test,
    y_pred,
    zero_division=0
)

recall = recall_score(
    y_test,
    y_pred,
    zero_division=0
)

f1 = f1_score(
    y_test,
    y_pred,
    zero_division=0
)

roc_auc = roc_auc_score(
    y_test,
    y_probability
)

pr_auc = average_precision_score(
    y_test,
    y_probability
)


# ============================================================
# RESULTS
# ============================================================

print("\n" + "=" * 70)
print("MODEL PERFORMANCE")
print("=" * 70)

print(f"\nAccuracy  : {accuracy:.4f}")
print(f"Precision : {precision:.4f}")
print(f"Recall    : {recall:.4f}")
print(f"F1 Score  : {f1:.4f}")
print(f"ROC-AUC   : {roc_auc:.4f}")
print(f"PR-AUC    : {pr_auc:.4f}")


# ============================================================
# CONFUSION MATRIX
# ============================================================

cm = confusion_matrix(
    y_test,
    y_pred
)

print("\nConfusion Matrix:")
print(cm)


# ============================================================
# CLASSIFICATION REPORT
# ============================================================

print("\nClassification Report:")
print(
    classification_report(
        y_test,
        y_pred,
        target_names=[
            "NORMAL",
            "ATTACK"
        ],
        zero_division=0
    )
)


# ============================================================
# SAVE MODEL
# ============================================================

os.makedirs(
    MODEL_DIR,
    exist_ok=True
)

joblib.dump(
    model,
    MODEL_PATH
)

joblib.dump(
    scaler,
    SCALER_PATH
)


# ============================================================
# SAVE FEATURE NAMES
# ============================================================

FEATURE_PATH = os.path.join(
    MODEL_DIR,
    "attack_features.joblib"
)

joblib.dump(
    list(X.columns),
    FEATURE_PATH
)


# ============================================================
# FINAL
# ============================================================

print("\n" + "=" * 70)
print("MODEL SAVED")
print("=" * 70)

print("\nModel:")
print(MODEL_PATH)

print("\nScaler:")
print(SCALER_PATH)

print("\nFeature list:")
print(FEATURE_PATH)

print("\nTraining pipeline completed successfully.")

print("=" * 70)
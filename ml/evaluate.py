import pandas as pd
import joblib

from sklearn.metrics import (
    confusion_matrix,
    classification_report,
    roc_auc_score,
    average_precision_score
)


# ============================================================
# PATHS
# ============================================================

DATASET_PATH = "datasets/processed/ton_iot_network_processed.csv"

MODEL_PATH = "ml/models/attack_model.joblib"
SCALER_PATH = "ml/models/attack_scaler.joblib"
FEATURE_PATH = "ml/models/attack_features.joblib"


# ============================================================
# LOAD
# ============================================================

print("=" * 70)
print("MODEL VALIDATION")
print("=" * 70)

print("\nLoading dataset...")

df = pd.read_csv(DATASET_PATH)

model = joblib.load(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)
features = joblib.load(FEATURE_PATH)

print("Dataset:", df.shape)
print("Features saved:", len(features))


# ============================================================
# CHECK FEATURE CONSISTENCY
# ============================================================

current_features = [
    col for col in df.columns
    if col not in ["label", "attack_type"]
]

print("\nChecking feature consistency...")

missing_features = [
    col for col in features
    if col not in current_features
]

extra_features = [
    col for col in current_features
    if col not in features
]

print("Missing features:", missing_features)
print("Extra features:", extra_features)


if missing_features or extra_features:

    print("\nERROR: Feature mismatch detected.")

    raise SystemExit


# ============================================================
# PREPARE DATA
# ============================================================

X = df[features]

y = df["label"]


# ============================================================
# TRANSFORM
# ============================================================

print("\nApplying saved scaler...")

X_scaled = scaler.transform(X)


# ============================================================
# PREDICT
# ============================================================

print("\nRunning predictions...")

predictions = model.predict(X_scaled)

probabilities = model.predict_proba(
    X_scaled
)[:, 1]


# ============================================================
# METRICS
# ============================================================

print("\n" + "=" * 70)
print("FULL DATASET VALIDATION")
print("=" * 70)

print("\nROC-AUC:")

print(
    roc_auc_score(
        y,
        probabilities
    )
)

print("\nPR-AUC:")

print(
    average_precision_score(
        y,
        probabilities
    )
)


print("\nConfusion Matrix:")

print(
    confusion_matrix(
        y,
        predictions
    )
)


print("\nClassification Report:")

print(
    classification_report(
        y,
        predictions,
        target_names=[
            "NORMAL",
            "ATTACK"
        ],
        zero_division=0
    )
)


# ============================================================
# ATTACK TYPE ANALYSIS
# ============================================================

print("\n" + "=" * 70)
print("ATTACK TYPE DISTRIBUTION")
print("=" * 70)

print(
    df["attack_type"].value_counts()
)


# ============================================================
# PREDICTION DISTRIBUTION
# ============================================================

print("\n" + "=" * 70)
print("PREDICTION DISTRIBUTION")
print("=" * 70)

print(
    pd.Series(predictions).value_counts()
)


print("\nValidation completed.")
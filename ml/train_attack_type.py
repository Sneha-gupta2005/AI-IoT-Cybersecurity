import pandas as pd
import numpy as np
import os
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
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
    "attack_type_model.joblib"
)

FEATURE_PATH = os.path.join(
    MODEL_DIR,
    "attack_type_features.joblib"
)

LABEL_ENCODER_PATH = os.path.join(
    MODEL_DIR,
    "attack_type_label_encoder.joblib"
)


# ============================================================
# LOAD DATASET
# ============================================================

print("=" * 70)
print("TON-IOT MULTI-CLASS ATTACK CLASSIFICATION")
print("=" * 70)

print("\nLoading processed dataset...")

df = pd.read_csv(DATASET_PATH)

print("Dataset shape:", df.shape)


# ============================================================
# FEATURES AND TARGET
# ============================================================

X = df.drop(
    columns=["label", "attack_type"]
)

y = df["attack_type"]


print("\nNumber of features:", X.shape[1])

print("\nAttack classes:")
print(y.value_counts())


# ============================================================
# LABEL ENCODING
# ============================================================

print("\nEncoding attack classes...")

label_encoder = LabelEncoder()

y_encoded = label_encoder.fit_transform(y)

print("\nClass mapping:")

for index, class_name in enumerate(
    label_encoder.classes_
):
    print(
        index,
        "->",
        class_name
    )


# ============================================================
# TRAIN / TEST SPLIT
# ============================================================

print("\nCreating train/test split...")

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y_encoded,
    test_size=0.20,
    random_state=42,
    stratify=y_encoded
)

print("Training samples:", X_train.shape[0])
print("Testing samples:", X_test.shape[0])


# ============================================================
# XGBOOST MULTI-CLASS MODEL
# ============================================================

print("\nTraining XGBoost multi-class model...")

model = XGBClassifier(
    n_estimators=300,
    max_depth=8,
    learning_rate=0.08,
    subsample=0.8,
    colsample_bytree=0.8,
    objective="multi:softprob",
    num_class=len(label_encoder.classes_),
    eval_metric="mlogloss",
    random_state=42,
    n_jobs=-1
)


model.fit(
    X_train,
    y_train
)

print("Training completed.")


# ============================================================
# PREDICTION
# ============================================================

print("\nGenerating predictions...")

y_pred = model.predict(X_test)


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
    average="weighted",
    zero_division=0
)

recall = recall_score(
    y_test,
    y_pred,
    average="weighted",
    zero_division=0
)

f1 = f1_score(
    y_test,
    y_pred,
    average="weighted",
    zero_division=0
)


# ============================================================
# RESULTS
# ============================================================

print("\n" + "=" * 70)
print("MULTI-CLASS MODEL PERFORMANCE")
print("=" * 70)

print(f"\nAccuracy  : {accuracy:.4f}")
print(f"Precision : {precision:.4f}")
print(f"Recall    : {recall:.4f}")
print(f"F1 Score  : {f1:.4f}")


# ============================================================
# CLASSIFICATION REPORT
# ============================================================

print("\nClassification Report:")

print(
    classification_report(
        y_test,
        y_pred,
        target_names=label_encoder.classes_,
        zero_division=0
    )
)


# ============================================================
# CONFUSION MATRIX
# ============================================================

print("\nConfusion Matrix:")

cm = confusion_matrix(
    y_test,
    y_pred
)

print(cm)


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
    list(X.columns),
    FEATURE_PATH
)

joblib.dump(
    label_encoder,
    LABEL_ENCODER_PATH
)


# ============================================================
# FINAL
# ============================================================

print("\n" + "=" * 70)
print("MULTI-CLASS MODEL SAVED")
print("=" * 70)

print("\nModel:")
print(MODEL_PATH)

print("\nFeature list:")
print(FEATURE_PATH)

print("\nLabel encoder:")
print(LABEL_ENCODER_PATH)

print("\nTraining completed successfully.")

print("=" * 70)
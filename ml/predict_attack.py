import pandas as pd
import joblib


# ============================================================
# PATHS
# ============================================================

DATASET_PATH = "datasets/processed/ton_iot_network_processed.csv"

BINARY_MODEL_PATH = "ml/models/attack_model.joblib"
BINARY_SCALER_PATH = "ml/models/attack_scaler.joblib"
BINARY_FEATURE_PATH = "ml/models/attack_features.joblib"

MULTI_MODEL_PATH = "ml/models/attack_type_model.joblib"
MULTI_FEATURE_PATH = "ml/models/attack_type_features.joblib"
LABEL_ENCODER_PATH = "ml/models/attack_type_label_encoder.joblib"


# ============================================================
# LOAD MODELS
# ============================================================

print("=" * 70)
print("AI CYBER ATTACK INFERENCE TEST")
print("=" * 70)

print("\nLoading models...")

binary_model = joblib.load(
    BINARY_MODEL_PATH
)

binary_scaler = joblib.load(
    BINARY_SCALER_PATH
)

binary_features = joblib.load(
    BINARY_FEATURE_PATH
)

multi_model = joblib.load(
    MULTI_MODEL_PATH
)

multi_features = joblib.load(
    MULTI_FEATURE_PATH
)

label_encoder = joblib.load(
    LABEL_ENCODER_PATH
)

print("All models loaded successfully.")


# ============================================================
# LOAD TEST DATA
# ============================================================

print("\nLoading test samples...")

df = pd.read_csv(
    DATASET_PATH
)


# Take a small sample from dataset
sample = df.sample(
    n=10,
    random_state=42
)


# ============================================================
# PREPARE FEATURES
# ============================================================

X = sample[binary_features]


# ============================================================
# BINARY PREDICTION
# ============================================================

print("\nRunning binary attack detection...")

X_scaled = binary_scaler.transform(X)

binary_predictions = binary_model.predict(
    X_scaled
)

binary_probabilities = binary_model.predict_proba(
    X_scaled
)[:, 1]


# ============================================================
# MULTI-CLASS PREDICTION
# ============================================================

multi_predictions = multi_model.predict(
    sample[multi_features]
)

multi_probabilities = multi_model.predict_proba(
    sample[multi_features]
)


# ============================================================
# DISPLAY RESULTS
# ============================================================

print("\n" + "=" * 70)
print("PREDICTION RESULTS")
print("=" * 70)

for i in range(len(sample)):

    binary_result = (
        "ATTACK"
        if binary_predictions[i] == 1
        else "NORMAL"
    )

    predicted_type = label_encoder.inverse_transform(
        [multi_predictions[i]]
    )[0]

    confidence = multi_probabilities[i].max()

    actual_type = sample.iloc[i]["attack_type"]

    print("\nSample:", i + 1)

    print("Actual type     :", actual_type)

    print("Binary result   :", binary_result)

    print(
        "Attack probability:",
        round(float(binary_probabilities[i]), 4)
    )

    print(
        "Predicted type  :",
        predicted_type
    )

    print(
        "Type confidence :",
        round(float(confidence), 4)
    )


print("\n" + "=" * 70)
print("INFERENCE TEST COMPLETED")
print("=" * 70)
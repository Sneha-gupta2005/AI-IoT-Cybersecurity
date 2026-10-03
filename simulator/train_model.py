import pandas as pd
import joblib
import psycopg2

from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

from config import (
    POSTGRES_HOST,
    POSTGRES_PORT,
    POSTGRES_DB,
    POSTGRES_USER,
    POSTGRES_PASSWORD
)


# ==========================================
# CONFIGURATION
# ==========================================

MODEL_FILE = "anomaly_model.joblib"

FEATURES = [
    "temperature",
    "voltage",
    "current",
    "power",
    "cpu_usage",
    "memory_usage",
    "network_traffic",
    "packet_rate",
    "latency"
]


# ==========================================
# CONNECT TO POSTGRESQL
# ==========================================

print("Connecting to PostgreSQL...")

connection = psycopg2.connect(
    host=POSTGRES_HOST,
    port=POSTGRES_PORT,
    database=POSTGRES_DB,
    user=POSTGRES_USER,
    password=POSTGRES_PASSWORD
)

print("Connected to PostgreSQL successfully.")


# ==========================================
# LOAD NORMAL TELEMETRY
# ==========================================

query = """
SELECT
    temperature,
    voltage,
    current,
    power,
    cpu_usage,
    memory_usage,
    network_traffic,
    packet_rate,
    latency
FROM iot_telemetry
WHERE anomaly_status = 'NORMAL'
ORDER BY id DESC
LIMIT 5000;
"""


df = pd.read_sql(query, connection)

connection.close()


print("\nDataset loaded.")
print("Number of records:", len(df))


# ==========================================
# CHECK DATA
# ==========================================

if len(df) < 100:

    print("\nERROR: Not enough data for training.")

    print(
        "Please run the IoT publisher for a few minutes "
        "and collect at least 100 normal records."
    )

    exit()


print("\nFeatures used for training:")

for feature in FEATURES:
    print("-", feature)


# ==========================================
# HANDLE MISSING VALUES
# ==========================================

df = df.dropna(subset=FEATURES)

print("\nRecords after removing missing values:", len(df))


# ==========================================
# PREPARE FEATURES
# ==========================================

X = df[FEATURES].copy()


# ==========================================
# FEATURE SCALING
# ==========================================

scaler = StandardScaler()

X_scaled = scaler.fit_transform(X)


# ==========================================
# CREATE ISOLATION FOREST
# ==========================================

print("\nTraining Isolation Forest...")

model = IsolationForest(
    n_estimators=200,
    contamination=0.02,
    random_state=42,
    n_jobs=-1
)


# ==========================================
# TRAIN MODEL
# ==========================================

model.fit(X_scaled)


print("Isolation Forest training completed.")


# ==========================================
# SAVE MODEL + SCALER
# ==========================================

model_package = {
    "model": model,
    "scaler": scaler,
    "features": FEATURES
}

joblib.dump(
    model_package,
    MODEL_FILE
)


print("\nModel saved successfully!")

print(
    f"Model file: {MODEL_FILE}"
)


# ==========================================
# TRAINING SUMMARY
# ==========================================

predictions = model.predict(X_scaled)

normal_count = (predictions == 1).sum()
anomaly_count = (predictions == -1).sum()

print("\n========== TRAINING SUMMARY ==========")

print("Total records:", len(X))

print("AI detected NORMAL:", normal_count)

print("AI detected ANOMALY:", anomaly_count)

print(
    "Anomaly percentage:",
    round((anomaly_count / len(X)) * 100, 2),
    "%"
)

print("======================================")
import os
from datetime import datetime

import joblib
import numpy as np
import psycopg2
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel

from ml.feature_builder import build_ml_features


# =========================================================
# ENVIRONMENT
# =========================================================

load_dotenv()


# =========================================================
# FASTAPI
# =========================================================

app = FastAPI(
    title="AI-IoT Cybersecurity API",
    description="AI-based IoT cyber attack detection API",
    version="1.0.0"
)


# =========================================================
# MODEL PATHS
# =========================================================

BINARY_MODEL_PATH = "ml/models/attack_model.joblib"

MULTI_CLASS_MODEL_PATH = (
    "ml/models/attack_type_model.joblib"
)

LABEL_ENCODER_PATH = (
    "ml/models/attack_type_label_encoder.joblib"
)


# =========================================================
# LOAD MODELS
# =========================================================

binary_model = joblib.load(
    BINARY_MODEL_PATH
)

multi_class_model = joblib.load(
    MULTI_CLASS_MODEL_PATH
)

label_encoder = joblib.load(
    LABEL_ENCODER_PATH
)


# =========================================================
# REQUEST MODEL
# =========================================================

class PredictionRequest(BaseModel):

    features: dict


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_db_connection():

    return psycopg2.connect(
        host=os.getenv(
            "POSTGRES_HOST",
            "localhost"
        ),

        port=os.getenv(
            "POSTGRES_PORT",
            "5432"
        ),

        database=os.getenv(
            "POSTGRES_DB",
            "iot_cybersecurity"
        ),

        user=os.getenv(
            "POSTGRES_USER",
            "postgres"
        ),

        password=os.getenv(
            "POSTGRES_PASSWORD"
        )
    )


# =========================================================
# SAVE PREDICTION
# =========================================================

def save_prediction(
    result,
    features
):

    conn = get_db_connection()

    cursor = conn.cursor()

    query = """
    INSERT INTO network_ml_predictions (

        timestamp,

        attack_status,
        attack_probability,

        predicted_attack_type,
        attack_type_confidence,

        src_port,
        dst_port,

        proto,
        service,

        duration,
        src_bytes,
        dst_bytes,

        src_pkts,
        dst_pkts,

        conn_state,

        processed_at
    )

    VALUES (

        %s,

        %s,
        %s,

        %s,
        %s,

        %s,
        %s,

        %s,
        %s,

        %s,
        %s,
        %s,

        %s,
        %s,

        %s,

        %s
    )
    """

    values = (

        datetime.now(),

        result["attack_status"],
        result["attack_probability"],

        result["predicted_attack_type"],
        result["attack_type_confidence"],

        features.get("src_port"),
        features.get("dst_port"),

        features.get("proto"),
        features.get("service"),

        features.get("duration"),
        features.get("src_bytes"),
        features.get("dst_bytes"),

        features.get("src_pkts"),
        features.get("dst_pkts"),

        features.get("conn_state"),

        datetime.now()
    )

    cursor.execute(
        query,
        values
    )

    conn.commit()

    cursor.close()
    conn.close()


# =========================================================
# ROOT
# =========================================================

@app.get("/")
def root():

    return {
        "service": "AI-IoT Cybersecurity API",
        "status": "running",
        "version": "1.0.0"
    }


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/health")
def health():

    return {
        "status": "healthy",

        "binary_model": "loaded",

        "multi_class_model": "loaded",

        "feature_count": 72,

        "database": "configured"
    }


# =========================================================
# PREDICTION
# =========================================================

@app.post("/predict")
def predict(
    request: PredictionRequest
):

    # -----------------------------------------------------
    # Build exact 72-feature input
    # -----------------------------------------------------

    X = build_ml_features(
        request.features
    )


    # -----------------------------------------------------
    # Binary prediction
    # -----------------------------------------------------

    binary_prediction = binary_model.predict(
        X
    )[0]

    binary_probability = binary_model.predict_proba(
        X
    )[0][1]


    # -----------------------------------------------------
    # Multi-class prediction
    # -----------------------------------------------------

    multi_probability = (
        multi_class_model
        .predict_proba(X)[0]
    )

    multi_prediction = np.argmax(
        multi_probability
    )

    attack_type = label_encoder.inverse_transform(
        [multi_prediction]
    )[0]

    attack_type_confidence = float(
        multi_probability[multi_prediction]
    )


    # -----------------------------------------------------
    # Final status
    # -----------------------------------------------------

    if binary_prediction == 1:

        attack_status = "ATTACK"

    else:

        attack_status = "NORMAL"

        attack_type = "normal"

        attack_type_confidence = float(
            multi_probability[
                list(
                    label_encoder.classes_
                ).index("normal")
            ]
        )


    # -----------------------------------------------------
    # Result
    # -----------------------------------------------------

    result = {

        "status": "success",

        "attack_status":
            attack_status,

        "attack_probability":
            round(
                float(binary_probability),
                4
            ),

        "predicted_attack_type":
            attack_type,

        "attack_type_confidence":
            round(
                attack_type_confidence,
                4
            ),

        "feature_count":
            X.shape[1]
    }


    # -----------------------------------------------------
    # SAVE TO DATABASE
    # -----------------------------------------------------

    try:

        save_prediction(
            result,
            request.features
        )

        result["database_status"] = "saved"

    except Exception as e:

        result["database_status"] = "failed"

        result["database_error"] = str(e)


    return result
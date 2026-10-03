import pandas as pd
import joblib


FEATURE_PATH = "ml/models/attack_features.joblib"


def build_ml_features(raw_data):
    """
    Convert raw network telemetry into the exact
    72-feature schema expected by the trained model.
    """

    # Load training feature schema
    feature_names = joblib.load(FEATURE_PATH)

    # Convert incoming dictionary to DataFrame
    df = pd.DataFrame([raw_data])

    # --------------------------------------------------------
    # Convert boolean values
    # --------------------------------------------------------

    bool_columns = [
        "dns_AA",
        "dns_RD",
        "dns_RA",
        "dns_rejected",
        "ssl_resumed",
        "ssl_established"
    ]

    for column in bool_columns:
        if column in df.columns:
            df[column] = df[column].astype(int)

    # --------------------------------------------------------
    # One-hot encode categorical columns
    # --------------------------------------------------------

    categorical_columns = [
        "proto",
        "service",
        "conn_state",
        "dns_AA",
        "dns_RD",
        "dns_RA",
        "dns_rejected",
        "ssl_version",
        "ssl_cipher",
        "ssl_resumed",
        "ssl_established",
        "http_trans_depth",
        "http_method",
        "http_version"
    ]

    categorical_columns = [
        column
        for column in categorical_columns
        if column in df.columns
    ]

    df = pd.get_dummies(
        df,
        columns=categorical_columns,
        drop_first=True
    )

    # --------------------------------------------------------
    # Add missing model features
    # --------------------------------------------------------

    for feature in feature_names:

        if feature not in df.columns:
            df[feature] = 0

    # --------------------------------------------------------
    # Remove extra features
    # --------------------------------------------------------

    df = df[feature_names]

    # --------------------------------------------------------
    # Convert everything to numeric
    # --------------------------------------------------------

    df = df.apply(
        pd.to_numeric,
        errors="coerce"
    )

    df = df.fillna(0)

    return df
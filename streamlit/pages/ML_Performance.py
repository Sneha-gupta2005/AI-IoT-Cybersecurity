import streamlit as st
import pandas as pd
import plotly.express as px


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="ML Performance",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 ML Performance")
st.caption(
    "Performance evaluation of the trained TON-IoT cybersecurity models"
)

st.divider()


# =========================================================
# MODEL 1 — BINARY ATTACK DETECTION
# =========================================================

st.subheader("🛡️ Binary Cyber Attack Detection")

st.info(
    "Model: XGBoost Binary Classifier | "
    "Dataset: TON-IoT Network Traffic | "
    "Evaluation: Stratified Test Split (20%)"
)

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Accuracy", "99.86%")
col2.metric("Precision", "99.93%")
col3.metric("Recall", "99.89%")
col4.metric("F1 Score", "99.91%")
col5.metric("ROC-AUC", "1.0000")

st.metric(
    "PR-AUC",
    "1.0000"
)

st.divider()


# =========================================================
# BINARY CONFUSION MATRIX
# =========================================================

st.subheader("📊 Binary Confusion Matrix")

binary_cm = pd.DataFrame(
    [
        [8387, 21],
        [32, 29655]
    ],
    index=["Actual Normal", "Actual Attack"],
    columns=["Predicted Normal", "Predicted Attack"]
)

fig_binary_cm = px.imshow(
    binary_cm,
    text_auto=True,
    title="Binary Attack Detection Confusion Matrix",
    labels={
        "x": "Predicted",
        "y": "Actual",
        "color": "Samples"
    }
)

st.plotly_chart(
    fig_binary_cm,
    use_container_width=True
)


# =========================================================
# BINARY METRICS CHART
# =========================================================

st.subheader("📈 Binary Model Metrics")

binary_metrics = pd.DataFrame(
    {
        "Metric": [
            "Accuracy",
            "Precision",
            "Recall",
            "F1 Score",
            "ROC-AUC",
            "PR-AUC"
        ],
        "Score": [
            0.9986,
            0.9993,
            0.9989,
            0.9991,
            1.0000,
            1.0000
        ]
    }
)

fig_binary_metrics = px.bar(
    binary_metrics,
    x="Metric",
    y="Score",
    text="Score",
    title="Binary Model Performance"
)

fig_binary_metrics.update_yaxes(
    range=[0, 1.05]
)

st.plotly_chart(
    fig_binary_metrics,
    use_container_width=True
)


# =========================================================
# MODEL 2 — MULTI-CLASS ATTACK TYPE
# =========================================================

st.divider()

st.subheader("🎯 Multi-Class Attack Type Detection")

st.info(
    "Model: XGBoost Multi-Class Classifier | "
    "Classes: 10 | "
    "Evaluation: Stratified Test Split (20%)"
)

col1, col2, col3, col4 = st.columns(4)

col1.metric("Accuracy", "98.98%")
col2.metric("Precision", "98.99%")
col3.metric("Recall", "98.98%")
col4.metric("F1 Score", "98.98%")


# =========================================================
# CLASS-WISE PERFORMANCE
# =========================================================

st.subheader("📋 Class-wise Performance")

class_metrics = pd.DataFrame(
    {
        "Attack Type": [
            "backdoor",
            "ddos",
            "dos",
            "injection",
            "mitm",
            "normal",
            "password",
            "ransomware",
            "scanning",
            "xss"
        ],

        "Precision": [
            1.00,
            0.99,
            0.99,
            0.98,
            0.75,
            1.00,
            0.99,
            1.00,
            0.99,
            0.97
        ],

        "Recall": [
            1.00,
            0.98,
            0.99,
            0.97,
            0.79,
            1.00,
            0.99,
            1.00,
            0.99,
            0.98
        ],

        "F1 Score": [
            1.00,
            0.99,
            0.99,
            0.98,
            0.77,
            1.00,
            0.99,
            1.00,
            0.99,
            0.97
        ]
    }
)

st.dataframe(
    class_metrics,
    use_container_width=True,
    hide_index=True
)


# =========================================================
# F1 SCORE BY ATTACK TYPE
# =========================================================

st.subheader("📊 F1 Score by Attack Type")

fig_f1 = px.bar(
    class_metrics,
    x="Attack Type",
    y="F1 Score",
    text="F1 Score",
    title="Attack Type Classification Performance"
)

fig_f1.update_yaxes(
    range=[0, 1.05]
)

st.plotly_chart(
    fig_f1,
    use_container_width=True
)


# =========================================================
# MULTI-CLASS CONFUSION MATRIX
# =========================================================

st.subheader("🔢 Multi-Class Confusion Matrix")

labels = [
    "backdoor",
    "ddos",
    "dos",
    "injection",
    "mitm",
    "normal",
    "password",
    "ransomware",
    "scanning",
    "xss"
]

multi_cm = pd.DataFrame(
    [
        [3741, 0, 1, 0, 0, 0, 0, 0, 0, 0],
        [0, 3937, 0, 20, 0, 8, 1, 1, 0, 32],
        [0, 1, 3744, 4, 25, 1, 5, 0, 19, 0],
        [0, 15, 5, 3883, 4, 2, 1, 0, 12, 71],
        [0, 2, 9, 6, 165, 7, 13, 0, 4, 2],
        [0, 8, 3, 0, 6, 8389, 0, 0, 1, 1],
        [0, 2, 6, 1, 17, 1, 3941, 0, 2, 2],
        [0, 0, 0, 0, 0, 0, 0, 2947, 0, 0],
        [0, 0, 13, 2, 1, 2, 2, 0, 3978, 0],
        [0, 4, 0, 40, 1, 2, 0, 0, 0, 2980]
    ],
    index=labels,
    columns=labels
)

fig_multi_cm = px.imshow(
    multi_cm,
    text_auto=True,
    aspect="auto",
    title="Multi-Class Attack Type Confusion Matrix",
    labels={
        "x": "Predicted Attack Type",
        "y": "Actual Attack Type",
        "color": "Samples"
    }
)

st.plotly_chart(
    fig_multi_cm,
    use_container_width=True
)


# =========================================================
# IMPORTANT RESEARCH NOTE
# =========================================================

st.divider()

st.subheader("ℹ️ Evaluation Note")

st.warning(
    "These metrics represent the current train/test evaluation results "
    "from the TON-IoT experiment. Before using them as final research "
    "claims, a leakage/generalization check should be performed using "
    "a preprocessing pipeline fitted only on the training data and, "
    "ideally, an independent or time-based validation split."
)

st.caption(
    "MITM has comparatively lower class-wise performance because the "
    "dataset contains substantially fewer MITM samples than the other "
    "attack classes."
)
import streamlit as st
import pandas as pd
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="AI-IoT Cybersecurity",
    page_icon="🛡️",
    layout="wide"
)


# ==========================================
# DATABASE CONNECTION
# ==========================================

def get_connection():

    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", "5432"),
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


# ==========================================
# LOAD CYBER DATA
# ==========================================

@st.cache_data(ttl=5)
def load_cyber_data():

    conn = get_connection()

    query = """
    SELECT
        id,
        device_id,
        timestamp,
        ai_anomaly_status,
        anomaly_score,
        attack_status,
        attack_type,
        severity,
        network_traffic,
        packet_rate,
        latency,
        cpu_usage,
        memory_usage,
        detection_reason
    FROM cyber_attack_results
    ORDER BY timestamp DESC
    LIMIT 1000
    """

    df = pd.read_sql(query, conn)

    conn.close()

    return df


# ==========================================
# HEADER
# ==========================================

st.title("🛡️ AI-Based IoT Cybersecurity System")

st.caption(
    "AI-powered Device Anomaly and Cyber Attack Detection"
)

st.divider()


# ==========================================
# LOAD DATA
# ==========================================

try:

    df = load_cyber_data()

except Exception as e:

    st.error("Database connection failed.")

    st.code(str(e))

    st.stop()


if df.empty:

    st.warning(
        "No cybersecurity data available yet."
    )

    st.stop()


# ==========================================
# KPI CALCULATIONS
# ==========================================

total_records = len(df)

total_attacks = len(
    df[df["attack_status"] == "SUSPICIOUS"]
)

total_anomalies = len(
    df[df["ai_anomaly_status"] == "ANOMALY"]
)

high_severity = len(
    df[df["severity"] == "HIGH"]
)

# ==========================================
# KPI CARDS
# ==========================================

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        "Total Events",
        total_records
    )

with col2:

    st.metric(
        "Cyber Attacks",
        total_attacks
    )

with col3:

    st.metric(
        "AI Anomalies",
        total_anomalies
    )

with col4:

    st.metric(
        "High Severity",
        high_severity
    )


st.divider()


# ==========================================
# ATTACK STATUS
# ==========================================

st.subheader("Security Status")

col1, col2 = st.columns(2)

with col1:

    status_counts = (
        df["attack_status"]
        .value_counts()
    )

    st.bar_chart(status_counts)


with col2:

    attack_counts = (
        df[df["attack_status"] == "SUSPICIOUS"]
        ["attack_type"]
        .value_counts()
    )

    st.bar_chart(attack_counts)


# ==========================================
# SEVERITY
# ==========================================

st.subheader("Severity Distribution")

severity_counts = (
    df["severity"]
    .value_counts()
)

st.bar_chart(severity_counts)


# ==========================================
# DEVICE SECURITY
# ==========================================

st.subheader("Device Security Overview")

device_summary = (
    df.groupby("device_id")
    .agg(
        total_events=("id", "count"),
        anomalies=(
            "ai_anomaly_status",
            lambda x: (x == "ANOMALY").sum()
        ),
        attacks=(
            "attack_status",
            lambda x: (x == "SUSPICIOUS").sum()
        ),
        high_severity=(
            "severity",
            lambda x: (x == "HIGH").sum()
        )
    )
    .reset_index()
)

st.dataframe(
    device_summary,
    use_container_width=True,
    hide_index=True
)


# ==========================================
# RECENT EVENTS
# ==========================================

st.subheader("Recent Security Events")

st.dataframe(
    df[
        [
            "timestamp",
            "device_id",
            "ai_anomaly_status",
            "attack_status",
            "attack_type",
            "severity",
            "detection_reason"
        ]
    ].head(50),
    use_container_width=True,
    hide_index=True
)


# ==========================================
# LIVE REFRESH
# ==========================================

st.caption(
    "Dashboard automatically refreshes data every 5 seconds."
)
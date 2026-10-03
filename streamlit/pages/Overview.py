import streamlit as st
import pandas as pd
import psycopg2
import os
import time
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Security Overview",
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
        database=os.getenv("POSTGRES_DB", "iot_cybersecurity"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD")
    )


# ==========================================
# LOAD LIVE DATA
# ==========================================

@st.cache_data(ttl=3)
def load_data():

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

st.title("🛡️ Security Overview")

st.caption(
    "AI-Based IoT Cyber Attack and Device Anomaly Detection"
)

st.divider()


# ==========================================
# LOAD DATA
# ==========================================

try:

    df = load_data()

except Exception as e:

    st.error("Unable to connect to PostgreSQL")
    st.code(str(e))
    st.stop()


if df.empty:

    st.warning("No security events available.")
    st.stop()


# ==========================================
# LIVE STATUS
# ==========================================

latest_time = pd.to_datetime(
    df["timestamp"]
).max()

st.success(
    f"🟢 Live Monitoring Active | Last Event: {latest_time}"
)


# ==========================================
# METRICS
# ==========================================

total_events = len(df)

attacks = (
    df["attack_status"] == "SUSPICIOUS"
).sum()

anomalies = (
    df["ai_anomaly_status"] == "ANOMALY"
).sum()

high = (
    df["severity"] == "HIGH"
).sum()


col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Events",
    total_events
)

col2.metric(
    "Cyber Attacks",
    attacks
)

col3.metric(
    "AI Anomalies",
    anomalies
)

col4.metric(
    "High Severity",
    high
)


st.divider()


# ==========================================
# ATTACK TYPES
# ==========================================

st.subheader("Attack Type Distribution")

attack_data = df[
    df["attack_status"] == "SUSPICIOUS"
]

if not attack_data.empty:

    attack_counts = (
        attack_data["attack_type"]
        .value_counts()
    )

    st.bar_chart(attack_counts)

else:

    st.info("No attacks detected.")


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
    ].head(25),
    use_container_width=True,
    hide_index=True
)


# ==========================================
# AUTO REFRESH
# ==========================================

st.caption(
    "🔄 Live data refreshes automatically every 5 seconds."
)

time.sleep(5)

st.cache_data.clear()

st.rerun()
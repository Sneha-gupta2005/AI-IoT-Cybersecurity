from ui import apply_theme
apply_theme()

import streamlit as st
import pandas as pd
import psycopg2
import os
import time
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Live Monitor",
    page_icon="📡",
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
    LIMIT 100
    """

    df = pd.read_sql(query, conn)

    conn.close()

    return df


# ==========================================
# PAGE HEADER
# ==========================================

st.title("📡 Live Security Monitor")

st.caption(
    "Real-time monitoring of IoT device anomalies and cyber attacks"
)

st.divider()


# ==========================================
# LOAD DATA
# ==========================================

try:

    df = load_data()

except Exception as e:

    st.error("Database connection failed.")
    st.code(str(e))
    st.stop()


if df.empty:

    st.warning("No security events available.")
    st.stop()


# ==========================================
# SYSTEM STATUS
# ==========================================

latest_time = pd.to_datetime(
    df["timestamp"]
).max()

st.success(
    f"🟢 Monitoring Active | Last Event: {latest_time}"
)


# ==========================================
# METRICS
# ==========================================

total = len(df)

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
    "Events",
    total
)

col2.metric(
    "Attacks",
    attacks
)

col3.metric(
    "Anomalies",
    anomalies
)

col4.metric(
    "High Severity",
    high
)


st.divider()


# ==========================================
# LIVE TELEMETRY
# ==========================================

st.subheader("📊 Live Network Telemetry")

col1, col2, col3 = st.columns(3)

latest = df.iloc[0]


with col1:

    st.metric(
        "Network Traffic",
        f"{latest['network_traffic']:.2f}"
    )

    st.metric(
        "Packet Rate",
        f"{latest['packet_rate']:.2f}"
    )


with col2:

    st.metric(
        "Latency",
        f"{latest['latency']:.2f}"
    )

    st.metric(
        "CPU Usage",
        f"{latest['cpu_usage']:.2f}%"
    )


with col3:

    st.metric(
        "Memory Usage",
        f"{latest['memory_usage']:.2f}%"
    )

    st.metric(
        "Device",
        latest["device_id"]
    )


st.divider()


# ==========================================
# LIVE SECURITY EVENTS
# ==========================================

st.subheader("🚨 Latest Security Events")

display_df = df[
    [
        "timestamp",
        "device_id",
        "ai_anomaly_status",
        "attack_status",
        "attack_type",
        "severity",
        "detection_reason"
    ]
]

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True
)


st.divider()


# ==========================================
# AUTO REFRESH
# ==========================================

st.caption("🔄 Live data refreshes automatically every 5 seconds.")

time.sleep(5)

st.cache_data.clear()

st.rerun()
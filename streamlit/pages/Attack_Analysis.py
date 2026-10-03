import streamlit as st
import pandas as pd
import psycopg2
import os
import time
import plotly.express as px
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Attack Analysis",
    page_icon="🚨",
    layout="wide"
)


# ==========================================
# DATABASE
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
    LIMIT 5000
    """

    df = pd.read_sql(query, conn)

    conn.close()

    return df


# ==========================================
# PAGE HEADER
# ==========================================

st.title("🚨 Attack Analysis")

st.caption(
    "Real-time analysis of detected cyber attacks and security events"
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

    st.warning("No attack data available.")
    st.stop()


# ==========================================
# FILTER ONLY ATTACKS
# ==========================================

attacks = df[
    df["attack_status"] == "SUSPICIOUS"
].copy()


if attacks.empty:

    st.success("🟢 No suspicious attacks detected.")

else:

    # ==========================================
    # TOP METRICS
    # ==========================================

    total_attacks = len(attacks)

    high_attacks = (
        attacks["severity"] == "HIGH"
    ).sum()

    medium_attacks = (
        attacks["severity"] == "MEDIUM"
    ).sum()

    devices_affected = (
        attacks["device_id"]
        .nunique()
    )


    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Attacks",
        total_attacks
    )

    col2.metric(
        "High Severity",
        high_attacks
    )

    col3.metric(
        "Medium Severity",
        medium_attacks
    )

    col4.metric(
        "Affected Devices",
        devices_affected
    )


    st.divider()


    # ==========================================
    # ATTACK TYPE
    # ==========================================

    st.subheader("Attack Type Distribution")

    attack_type_counts = (
        attacks["attack_type"]
        .value_counts()
        .reset_index()
    )

    attack_type_counts.columns = [
        "attack_type",
        "count"
    ]


    fig_attack = px.bar(
        attack_type_counts,
        x="attack_type",
        y="count",
        title="Detected Attack Types",
        labels={
            "attack_type": "Attack Type",
            "count": "Number of Events"
        }
    )

    st.plotly_chart(
        fig_attack,
        use_container_width=True
    )


    # ==========================================
    # SEVERITY
    # ==========================================

    st.subheader("Severity Distribution")

    severity_counts = (
        attacks["severity"]
        .value_counts()
        .reset_index()
    )

    severity_counts.columns = [
        "severity",
        "count"
    ]


    fig_severity = px.pie(
        severity_counts,
        names="severity",
        values="count",
        title="Attack Severity"
    )

    st.plotly_chart(
        fig_severity,
        use_container_width=True
    )


    # ==========================================
    # ATTACK TIMELINE
    # ==========================================

    st.subheader("Attack Timeline")

    timeline = (
        attacks
        .set_index("timestamp")
        .resample("1min")
        .size()
        .reset_index(name="attacks")
    )


    fig_timeline = px.line(
        timeline,
        x="timestamp",
        y="attacks",
        title="Attacks Over Time",
        labels={
            "timestamp": "Time",
            "attacks": "Attack Events"
        }
    )

    st.plotly_chart(
        fig_timeline,
        use_container_width=True
    )


    # ==========================================
    # DEVICE-WISE ATTACKS
    # ==========================================

    st.subheader("Device-wise Attack Distribution")

    device_counts = (
        attacks["device_id"]
        .value_counts()
        .reset_index()
    )

    device_counts.columns = [
        "device_id",
        "attacks"
    ]


    fig_device = px.bar(
        device_counts,
        x="device_id",
        y="attacks",
        title="Attacks by Device"
    )

    st.plotly_chart(
        fig_device,
        use_container_width=True
    )


    # ==========================================
    # DETECTION REASONS
    # ==========================================

    st.subheader("Detection Reasons")

    reason_counts = (
        attacks["detection_reason"]
        .value_counts()
        .reset_index()
    )

    reason_counts.columns = [
        "detection_reason",
        "count"
    ]


    st.dataframe(
        reason_counts,
        use_container_width=True,
        hide_index=True
    )


    # ==========================================
    # DETAILED ATTACK TABLE
    # ==========================================

    st.subheader("Detailed Attack Events")

    st.dataframe(
        attacks[
            [
                "timestamp",
                "device_id",
                "attack_type",
                "severity",
                "anomaly_score",
                "network_traffic",
                "packet_rate",
                "latency",
                "detection_reason"
            ]
        ].sort_values(
            "timestamp",
            ascending=False
        ),
        use_container_width=True,
        hide_index=True
    )


# ==========================================
# AUTO REFRESH
# ==========================================

st.divider()

st.caption(
    "🔄 Live data refreshes automatically every 5 seconds."
)

time.sleep(5)

st.cache_data.clear()

st.rerun()
import streamlit as st
import pandas as pd
import psycopg2
import os
import time
import plotly.express as px
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Device Analysis",
    page_icon="📱",
    layout="wide"
)


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_connection():

    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        database=os.getenv("POSTGRES_DB", "iot_cybersecurity"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD")
    )


# =========================================================
# LOAD LIVE DATA
# =========================================================

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

    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        errors="coerce"
    )

    return df


# =========================================================
# PAGE HEADER
# =========================================================

st.title("📱 Device Analysis")

st.caption(
    "Device-wise security, anomaly and network activity analysis"
)

st.divider()


# =========================================================
# DATABASE CHECK
# =========================================================

try:

    df = load_data()

except Exception as e:

    st.error("Database connection failed.")

    st.code(str(e))

    st.stop()


if df.empty:

    st.warning("No device data available.")

    st.stop()


# =========================================================
# DEVICE SUMMARY
# =========================================================

device_summary = (
    df.groupby("device_id")
    .agg(
        total_events=("id", "count"),

        anomaly_count=(
            "ai_anomaly_status",
            lambda x: (x == "ANOMALY").sum()
        ),

        attack_count=(
            "attack_status",
            lambda x: (x == "SUSPICIOUS").sum()
        ),

        high_severity_count=(
            "severity",
            lambda x: (x == "HIGH").sum()
        ),

        last_seen=("timestamp", "max"),

        avg_network_traffic=(
            "network_traffic",
            "mean"
        ),

        avg_packet_rate=(
            "packet_rate",
            "mean"
        ),

        avg_latency=(
            "latency",
            "mean"
        ),

        avg_cpu=(
            "cpu_usage",
            "mean"
        ),

        avg_memory=(
            "memory_usage",
            "mean"
        )
    )
    .reset_index()
)


# =========================================================
# DEVICE SELECTOR
# =========================================================

st.subheader("🔍 Select Device")

selected_device = st.selectbox(
    "Choose a device",
    ["All Devices"] +
    sorted(
        df["device_id"]
        .dropna()
        .unique()
        .tolist()
    )
)


# =========================================================
# ALL DEVICES VIEW
# =========================================================

if selected_device == "All Devices":

    st.subheader("📊 Overall Device Summary")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Devices",
        df["device_id"].nunique()
    )

    col2.metric(
        "Total Events",
        len(df)
    )

    col3.metric(
        "Devices with Attacks",
        device_summary[
            device_summary["attack_count"] > 0
        ]["device_id"].nunique()
    )

    col4.metric(
        "Devices with Anomalies",
        device_summary[
            device_summary["anomaly_count"] > 0
        ]["device_id"].nunique()
    )

    st.divider()


    # -----------------------------------------------------
    # ATTACKS BY DEVICE
    # -----------------------------------------------------

    st.subheader("🚨 Attacks by Device")

    fig_attacks = px.bar(
        device_summary,
        x="device_id",
        y="attack_count",
        title="Cyber Attacks Detected per Device",
        labels={
            "device_id": "Device",
            "attack_count": "Attack Events"
        }
    )

    st.plotly_chart(
        fig_attacks,
        use_container_width=True
    )


    # -----------------------------------------------------
    # ANOMALIES BY DEVICE
    # -----------------------------------------------------

    st.subheader("⚠️ Anomalies by Device")

    fig_anomaly = px.bar(
        device_summary,
        x="device_id",
        y="anomaly_count",
        title="AI Anomalies Detected per Device",
        labels={
            "device_id": "Device",
            "anomaly_count": "Anomaly Events"
        }
    )

    st.plotly_chart(
        fig_anomaly,
        use_container_width=True
    )


    # -----------------------------------------------------
    # NETWORK ACTIVITY
    # -----------------------------------------------------

    st.subheader("🌐 Average Network Activity")

    network_df = device_summary[
        [
            "device_id",
            "avg_network_traffic",
            "avg_packet_rate",
            "avg_latency"
        ]
    ].copy()

    network_long = network_df.melt(
        id_vars="device_id",
        var_name="metric",
        value_name="value"
    )

    fig_network = px.bar(
        network_long,
        x="device_id",
        y="value",
        color="metric",
        barmode="group",
        title="Average Network Metrics by Device"
    )

    st.plotly_chart(
        fig_network,
        use_container_width=True
    )


    # -----------------------------------------------------
    # DEVICE TABLE
    # -----------------------------------------------------

    st.subheader("📋 Device Security Summary")

    display_df = device_summary.copy()

    display_df["avg_network_traffic"] = (
        display_df["avg_network_traffic"]
        .round(2)
    )

    display_df["avg_packet_rate"] = (
        display_df["avg_packet_rate"]
        .round(2)
    )

    display_df["avg_latency"] = (
        display_df["avg_latency"]
        .round(2)
    )

    display_df["avg_cpu"] = (
        display_df["avg_cpu"]
        .round(2)
    )

    display_df["avg_memory"] = (
        display_df["avg_memory"]
        .round(2)
    )

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# SINGLE DEVICE VIEW
# =========================================================

else:

    device_data = df[
        df["device_id"] == selected_device
    ].copy()

    device_info = device_summary[
        device_summary["device_id"] == selected_device
    ].iloc[0]

    st.subheader(
        f"📱 Device: {selected_device}"
    )


    # -----------------------------------------------------
    # DEVICE KPIs
    # -----------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Events",
        int(device_info["total_events"])
    )

    col2.metric(
        "AI Anomalies",
        int(device_info["anomaly_count"])
    )

    col3.metric(
        "Cyber Attacks",
        int(device_info["attack_count"])
    )

    col4.metric(
        "High Severity",
        int(device_info["high_severity_count"])
    )

    st.divider()


    # -----------------------------------------------------
    # CURRENT TELEMETRY
    # -----------------------------------------------------

    latest = (
        device_data
        .sort_values("timestamp")
        .iloc[-1]
    )

    st.subheader("📡 Latest Telemetry")

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric(
        "Network Traffic",
        f"{latest['network_traffic']:.2f}"
    )

    col2.metric(
        "Packet Rate",
        f"{latest['packet_rate']:.2f}"
    )

    col3.metric(
        "Latency",
        f"{latest['latency']:.2f}"
    )

    col4.metric(
        "CPU Usage",
        f"{latest['cpu_usage']:.2f}%"
    )

    col5.metric(
        "Memory Usage",
        f"{latest['memory_usage']:.2f}%"
    )

    st.divider()


    # -----------------------------------------------------
    # SECURITY TIMELINE
    # -----------------------------------------------------

    st.subheader("📈 Security Activity")

    timeline = (
        device_data
        .set_index("timestamp")
        .resample("1min")
        .agg(
            attacks=(
                "attack_status",
                lambda x: (x == "SUSPICIOUS").sum()
            ),

            anomalies=(
                "ai_anomaly_status",
                lambda x: (x == "ANOMALY").sum()
            )
        )
        .reset_index()
    )

    fig_timeline = px.line(
        timeline,
        x="timestamp",
        y=["attacks", "anomalies"],
        title="Attacks and Anomalies Over Time",
        labels={
            "value": "Events",
            "timestamp": "Time"
        }
    )

    st.plotly_chart(
        fig_timeline,
        use_container_width=True
    )


    # -----------------------------------------------------
    # NETWORK METRICS
    # -----------------------------------------------------

    st.subheader("🌐 Network Metrics")

    network_metrics = device_data[
        [
            "timestamp",
            "network_traffic",
            "packet_rate",
            "latency"
        ]
    ].sort_values("timestamp")

    fig_metrics = px.line(
        network_metrics,
        x="timestamp",
        y=[
            "network_traffic",
            "packet_rate",
            "latency"
        ],
        title="Network Behaviour",
        labels={
            "value": "Metric Value",
            "timestamp": "Time"
        }
    )

    st.plotly_chart(
        fig_metrics,
        use_container_width=True
    )


    # -----------------------------------------------------
    # CPU AND MEMORY
    # -----------------------------------------------------

    st.subheader("💻 Resource Utilization")

    resource_data = device_data[
        [
            "timestamp",
            "cpu_usage",
            "memory_usage"
        ]
    ].sort_values("timestamp")

    fig_resource = px.line(
        resource_data,
        x="timestamp",
        y=[
            "cpu_usage",
            "memory_usage"
        ],
        title="CPU and Memory Usage",
        labels={
            "value": "Usage (%)",
            "timestamp": "Time"
        }
    )

    st.plotly_chart(
        fig_resource,
        use_container_width=True
    )


    # -----------------------------------------------------
    # ATTACK TYPES
    # -----------------------------------------------------

    st.subheader("🚨 Attack Types")

    attack_data = device_data[
        device_data["attack_status"] == "SUSPICIOUS"
    ]

    if not attack_data.empty:

        attack_counts = (
            attack_data["attack_type"]
            .value_counts()
            .reset_index()
        )

        attack_counts.columns = [
            "attack_type",
            "count"
        ]

        fig_attack_types = px.pie(
            attack_counts,
            names="attack_type",
            values="count",
            title=f"Attack Types for {selected_device}"
        )

        st.plotly_chart(
            fig_attack_types,
            use_container_width=True
        )

    else:

        st.success(
            "No cyber attacks detected for this device."
        )


    # -----------------------------------------------------
    # RECENT DEVICE EVENTS
    # -----------------------------------------------------

    st.subheader("📝 Recent Device Events")

    st.dataframe(
        device_data[
            [
                "timestamp",
                "ai_anomaly_status",
                "attack_status",
                "attack_type",
                "severity",
                "network_traffic",
                "packet_rate",
                "latency",
                "detection_reason"
            ]
        ]
        .sort_values(
            "timestamp",
            ascending=False
        )
        .head(50),
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# AUTO REFRESH
# =========================================================

st.divider()

st.caption(
    "🔄 Live data refreshes automatically every 5 seconds."
)

time.sleep(5)

st.cache_data.clear()

st.rerun()
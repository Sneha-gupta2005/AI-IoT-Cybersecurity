from ui import apply_theme, hero
apply_theme()

import streamlit as st
import pandas as pd
import psycopg2
import os
import time
import plotly.express as px
from dotenv import load_dotenv

load_dotenv()
st.set_page_config(page_title="Device Analysis", page_icon="📱", layout="wide")

def get_connection():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        database=os.getenv("POSTGRES_DB", "iot_cybersecurity"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD")
    )

@st.cache_data(ttl=3)
def load_data():
    conn = get_connection()
    df = pd.read_sql("""
        SELECT id, device_id, timestamp, ai_anomaly_status, anomaly_score,
               attack_status, attack_type, severity, network_traffic, packet_rate,
               latency, cpu_usage, memory_usage, detection_reason
        FROM cyber_attack_results
        ORDER BY timestamp DESC LIMIT 5000
    """, conn)
    conn.close()
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    return df

hero("Device Analysis", "Device-level security posture, live telemetry and behavioural trends.", True)

with st.sidebar:
    st.markdown("### 📱 Device Controls")
    auto = st.checkbox("🔄 Auto refresh", value=True)
    selected = st.selectbox("Device", ["All Devices", "SE-001", "SE-002", "SE-003"])

try:
    df = load_data()
except Exception as e:
    st.error("Database connection failed.")
    st.code(str(e))
    st.stop()

if df.empty:
    st.warning("No device data available.")
    st.stop()

attack_mask = df["attack_status"].astype(str).str.upper().isin(["SUSPICIOUS", "ATTACK", "MALICIOUS"])
anomaly_mask = df["ai_anomaly_status"].astype(str).str.upper().eq("ANOMALY")

if selected == "All Devices":
    summary = df.groupby("device_id").agg(
        events=("id", "count"),
        anomalies=("ai_anomaly_status", lambda x: (x.astype(str).str.upper() == "ANOMALY").sum()),
        attacks=("attack_status", lambda x: x.astype(str).str.upper().isin(["SUSPICIOUS", "ATTACK", "MALICIOUS"]).sum()),
        high=("severity", lambda x: (x.astype(str).str.upper() == "HIGH").sum()),
        last_seen=("timestamp", "max")
    ).reset_index()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📱 Devices", df["device_id"].nunique())
    c2.metric("📡 Events", f"{len(df):,}")
    c3.metric("🚨 Devices with Attacks", int((summary["attacks"] > 0).sum()))
    c4.metric("🧠 Devices with Anomalies", int((summary["anomalies"] > 0).sum()))

    st.subheader("🛡️ Device Security Overview")
    fig = px.bar(summary, x="device_id", y=["events", "anomalies", "attacks"],
                 barmode="group", text_auto=True, template="plotly_dark")
    fig.update_layout(height=380, margin=dict(l=10, r=10, t=30, b=10), xaxis_title="", yaxis_title="Events")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("🌐 Average Device Telemetry")
    avg = df.groupby("device_id")[["network_traffic", "packet_rate", "latency", "cpu_usage", "memory_usage"]].mean().reset_index()
    avg_long = avg.melt("device_id", var_name="metric", value_name="value")
    fig = px.bar(avg_long, x="device_id", y="value", color="metric", barmode="group",
                 template="plotly_dark", text_auto=".1f")
    fig.update_layout(height=380, margin=dict(l=10, r=10, t=30, b=10))
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("📋 Device Security Table")
    st.dataframe(summary.sort_values(["attacks", "anomalies"], ascending=False),
                 use_container_width=True, hide_index=True)
else:
    device_data = df[df["device_id"] == selected].copy()
    if device_data.empty:
        st.warning("No data for this device.")
        st.stop()

    device_data = device_data.sort_values("timestamp")
    attacks = device_data["attack_status"].astype(str).str.upper().isin(["SUSPICIOUS", "ATTACK", "MALICIOUS"])
    anomalies = device_data["ai_anomaly_status"].astype(str).str.upper().eq("ANOMALY")
    latest = device_data.iloc[-1]

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Events", f"{len(device_data):,}")
    c2.metric("🧠 AI Anomalies", int(anomalies.sum()))
    c3.metric("🚨 Attacks", int(attacks.sum()))
    c4.metric("CPU", f"{float(latest['cpu_usage']):.1f}%")
    c5.metric("Memory", f"{float(latest['memory_usage']):.1f}%")

    st.success(f"🟢 {selected} LIVE • Last seen {latest['timestamp'].strftime('%H:%M:%S')}")

    st.subheader("📡 Live Telemetry")
    left, right = st.columns(2)
    with left:
        fig = px.line(device_data, x="timestamp", y=["network_traffic", "packet_rate"],
                      template="plotly_dark")
        fig.update_layout(height=330, margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig, use_container_width=True)
    with right:
        fig = px.line(device_data, x="timestamp", y=["cpu_usage", "memory_usage"],
                      template="plotly_dark")
        fig.update_layout(height=330, margin=dict(l=10, r=10, t=30, b=10), yaxis_title="%")
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("🧠 AI Security Signal")
    fig = px.scatter(device_data, x="timestamp", y="anomaly_score",
                     color="ai_anomaly_status",
                     hover_data=["attack_type", "severity", "attack_status"],
                     template="plotly_dark")
    fig.update_layout(height=330, margin=dict(l=10, r=10, t=30, b=10))
    st.plotly_chart(fig, use_container_width=True)

    left, right = st.columns(2)
    with left:
        st.subheader("🚨 Attack Types")
        attack_data = device_data[attacks]
        if attack_data.empty:
            st.info("No suspicious attacks for this device.")
        else:
            counts = attack_data["attack_type"].fillna("Unknown").value_counts().reset_index()
            counts.columns = ["attack_type", "count"]
            fig = px.pie(counts, names="attack_type", values="count", hole=.5,
                         template="plotly_dark")
            fig.update_layout(height=330, margin=dict(l=10, r=10, t=30, b=10))
            st.plotly_chart(fig, use_container_width=True)
    with right:
        st.subheader("🛡️ Severity")
        severity = device_data["severity"].fillna("Unknown").value_counts().reset_index()
        severity.columns = ["severity", "count"]
        fig = px.pie(severity, names="severity", values="count", hole=.5,
                     template="plotly_dark")
        fig.update_layout(height=330, margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("📝 Recent Device Events")
    st.dataframe(
        device_data.sort_values("timestamp", ascending=False)[
            ["timestamp", "ai_anomaly_status", "attack_status", "attack_type",
             "severity", "network_traffic", "packet_rate", "latency", "detection_reason"]
        ].head(100),
        use_container_width=True, hide_index=True
    )

st.caption("🔄 Live data refreshes every 5 seconds when Auto refresh is enabled.")
if auto:
    time.sleep(5)
    st.cache_data.clear()
    st.rerun()

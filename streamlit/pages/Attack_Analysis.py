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
st.set_page_config(page_title="Attack Analysis", page_icon="🚨", layout="wide")

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
        ORDER BY timestamp DESC
        LIMIT 5000
    """, conn)
    conn.close()
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    return df

hero("Attack Analysis", "Interactive investigation of attacks, severity, affected devices and AI detection signals.", True)

with st.sidebar:
    st.markdown("### 🔎 Investigation Filters")
    auto = st.checkbox("🔄 Auto refresh", value=True)
    devices = ["All devices"] + sorted(pd.Series(["SE-001", "SE-002", "SE-003"]).unique().tolist())
    selected_device = st.selectbox("Device", devices)
    severity_options = ["HIGH", "MEDIUM", "LOW"]
    selected_severity = st.multiselect("Severity", severity_options, default=severity_options)

try:
    df = load_data()
except Exception as e:
    st.error("Database connection failed.")
    st.code(str(e))
    st.stop()

if df.empty:
    st.warning("No security data available.")
    st.stop()

attack_mask = df["attack_status"].astype(str).str.upper().isin(["SUSPICIOUS", "ATTACK", "MALICIOUS"])
attacks = df[attack_mask].copy()

if selected_device != "All devices":
    attacks = attacks[attacks["device_id"] == selected_device]

if selected_severity:
    attacks = attacks[attacks["severity"].astype(str).str.upper().isin(selected_severity)]

c1, c2, c3, c4 = st.columns(4)
c1.metric("🚨 Attacks", f"{len(attacks):,}")
c2.metric("🔴 High", int((attacks["severity"].astype(str).str.upper() == "HIGH").sum()))
c3.metric("🟠 Medium", int((attacks["severity"].astype(str).str.upper() == "MEDIUM").sum()))
c4.metric("📱 Affected Devices", attacks["device_id"].nunique())

if attacks.empty:
    st.success("🟢 No suspicious attacks match the selected filters.")
else:
    left, right = st.columns([1.2, 1])

    with left:
        counts = attacks["attack_type"].fillna("Unknown").astype(str).value_counts().reset_index()
        counts.columns = ["attack_type", "count"]
        fig = px.bar(counts, x="attack_type", y="count", text_auto=True, template="plotly_dark")
        fig.update_layout(height=350, margin=dict(l=10, r=10, t=30, b=10),
                          xaxis_title="", yaxis_title="Events")
        st.plotly_chart(fig, use_container_width=True)

    with right:
        sev = attacks["severity"].fillna("Unknown").astype(str).value_counts().reset_index()
        sev.columns = ["severity", "count"]
        fig = px.pie(sev, names="severity", values="count", hole=.55, template="plotly_dark")
        fig.update_layout(height=350, margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig, use_container_width=True)

    timeline = (attacks.sort_values("timestamp").set_index("timestamp")
                .resample("1min").size().reset_index(name="attacks"))
    fig = px.area(timeline, x="timestamp", y="attacks", template="plotly_dark")
    fig.update_layout(height=320, margin=dict(l=10, r=10, t=30, b=10),
                      xaxis_title="", yaxis_title="Attack events")
    st.plotly_chart(fig, use_container_width=True)

    left, right = st.columns(2)

    with left:
        dev = attacks["device_id"].value_counts().reset_index()
        dev.columns = ["device_id", "attacks"]
        fig = px.bar(dev, x="device_id", y="attacks", text_auto=True, template="plotly_dark")
        fig.update_layout(height=300, margin=dict(l=10, r=10, t=30, b=10), xaxis_title="")
        st.plotly_chart(fig, use_container_width=True)

    with right:
        reason = attacks["detection_reason"].fillna("Unknown").astype(str).value_counts().head(8).reset_index()
        reason.columns = ["reason", "count"]
        fig = px.bar(reason, x="count", y="reason", orientation="h", text_auto=True,
                     template="plotly_dark")
        fig.update_layout(height=300, margin=dict(l=10, r=10, t=30, b=10), xaxis_title="")
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("🧾 Attack Event Explorer")
    st.dataframe(
        attacks[["timestamp", "device_id", "attack_type", "severity", "anomaly_score",
                 "network_traffic", "packet_rate", "latency", "detection_reason"]]
        .sort_values("timestamp", ascending=False).head(200),
        use_container_width=True,
        hide_index=True
    )

st.caption("🔄 Live data refreshes every 5 seconds when Auto refresh is enabled.")

if auto:
    time.sleep(5)
    st.cache_data.clear()
    st.rerun()

from ui import apply_theme, hero
apply_theme()

import streamlit as st
import pandas as pd
import psycopg2
import os
import plotly.express as px
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="AI-IoT Cybersecurity", page_icon="🛡️", layout="wide")

def get_connection():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        database=os.getenv("POSTGRES_DB", "iot_cybersecurity"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD")
    )

@st.cache_data(ttl=3)
def load_cyber_data(limit=1500):
    conn = get_connection()
    query = """
    SELECT id, device_id, timestamp, ai_anomaly_status, anomaly_score,
           attack_status, attack_type, severity, network_traffic, packet_rate,
           latency, cpu_usage, memory_usage, detection_reason
    FROM cyber_attack_results
    ORDER BY timestamp DESC
    LIMIT %s
    """
    df = pd.read_sql(query, conn, params=(limit,))
    conn.close()
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df

hero("AI-Based IoT Cybersecurity", "Real-time AI anomaly detection, cyber attack monitoring and device security analytics.", True)

with st.sidebar:
    st.markdown("### 🎛️ Dashboard Controls")
    window = st.selectbox("Time window", ["Latest 100 events", "Latest 500 events", "Latest 1500 events"], index=2)
    limit = {"Latest 100 events":100, "Latest 500 events":500, "Latest 1500 events":1500}[window]
    refresh = st.checkbox("🔄 Auto refresh", value=True)
    if refresh:
        st.caption("Data refreshes every 5 seconds.")
    device_choice = st.selectbox("Device", ["All devices", "SE-001", "SE-002", "SE-003"])

try:
    df = load_cyber_data(limit)
except Exception as e:
    st.error("Database connection failed.")
    st.code(str(e))
    st.stop()

if df.empty:
    st.warning("No cybersecurity data available yet.")
    st.stop()

if device_choice != "All devices":
    df = df[df["device_id"] == device_choice].copy()

if df.empty:
    st.warning("No data for the selected device.")
    st.stop()

attack_mask = df["attack_status"].astype(str).str.upper().isin(["SUSPICIOUS", "ATTACK", "MALICIOUS"])
anomaly_mask = df["ai_anomaly_status"].astype(str).str.upper().eq("ANOMALY")
high_mask = df["severity"].astype(str).str.upper().eq("HIGH")

latest = df.iloc[0]
active_devices = df["device_id"].nunique()
attack_rate = attack_mask.mean() * 100

c1,c2,c3,c4,c5 = st.columns(5)
c1.metric("📡 Events", f"{len(df):,}")
c2.metric("🚨 Attacks", f"{attack_mask.sum():,}")
c3.metric("🧠 AI Anomalies", f"{anomaly_mask.sum():,}")
c4.metric("🔴 High Severity", f"{high_mask.sum():,}")
c5.metric("📱 Active Devices", active_devices)

st.caption(f"Latest event: {latest['timestamp'].strftime('%d %b %Y, %H:%M:%S')}  •  Attack rate: {attack_rate:.1f}%")

left,right = st.columns([1.15,1])

with left:
    st.subheader("📈 Security Activity")
    trend = df.sort_values("timestamp").copy()
    trend["attacks"] = attack_mask.loc[trend.index].astype(int).rolling(20, min_periods=1).sum()
    trend["anomalies"] = anomaly_mask.loc[trend.index].astype(int).rolling(20, min_periods=1).sum()
    trend = trend.rename(columns={"timestamp":"time"})
    fig = px.line(trend, x="time", y=["attacks","anomalies"], markers=False,
                  template="plotly_dark", labels={"value":"Events","variable":"Signal"})
    fig.update_layout(height=360, margin=dict(l=10,r=10,t=30,b=10), legend_title_text="")
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("🛡️ Security Status")
    status = df["attack_status"].fillna("UNKNOWN").astype(str).value_counts().reset_index()
    status.columns=["status","count"]
    fig = px.pie(status, names="status", values="count", hole=.58,
                  template="plotly_dark")
    fig.update_layout(height=360, margin=dict(l=10,r=10,t=30,b=10), showlegend=True)
    st.plotly_chart(fig, use_container_width=True)

left,right = st.columns(2)
with left:
    st.subheader("🚨 Attack Types")
    attacks_df = df[attack_mask]
    if attacks_df.empty:
        st.info("No suspicious attacks in the selected data.")
    else:
        counts = attacks_df["attack_type"].fillna("unknown").astype(str).value_counts().reset_index()
        counts.columns=["attack_type","count"]
        fig = px.bar(counts, x="attack_type", y="count", text_auto=True, template="plotly_dark")
        fig.update_layout(height=330, margin=dict(l=10,r=10,t=30,b=10), xaxis_title="", yaxis_title="Events")
        st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("📱 Device Security")
    device_summary = df.groupby("device_id").agg(
        events=("id","count"),
        anomalies=("ai_anomaly_status", lambda x:(x.astype(str).str.upper()=="ANOMALY").sum()),
        attacks=("attack_status", lambda x:x.astype(str).str.upper().isin(["SUSPICIOUS","ATTACK","MALICIOUS"]).sum()),
        high=("severity", lambda x:(x.astype(str).str.upper()=="HIGH").sum())
    ).reset_index()
    fig = px.bar(device_summary, x="device_id", y=["events","anomalies","attacks"],
                 barmode="group", template="plotly_dark")
    fig.update_layout(height=330, margin=dict(l=10,r=10,t=30,b=10), xaxis_title="", yaxis_title="Count")
    st.plotly_chart(fig, use_container_width=True)

st.subheader("⚡ Current Telemetry")
m1,m2,m3,m4,m5 = st.columns(5)
m1.metric("Network Traffic", f"{float(latest['network_traffic']):.2f}")
m2.metric("Packet Rate", f"{float(latest['packet_rate']):.2f}")
m3.metric("Latency", f"{float(latest['latency']):.2f}")
m4.metric("CPU", f"{float(latest['cpu_usage']):.1f}%")
m5.metric("Memory", f"{float(latest['memory_usage']):.1f}%")

st.subheader("🧾 Latest Security Events")
show = df[["timestamp","device_id","ai_anomaly_status","attack_status","attack_type","severity","detection_reason"]].head(25).copy()
st.dataframe(show, use_container_width=True, hide_index=True)

if refresh:
    import time
    time.sleep(5)
    st.cache_data.clear()
    st.rerun()

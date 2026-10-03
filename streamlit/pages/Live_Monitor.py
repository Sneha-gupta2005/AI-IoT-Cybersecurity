from ui import apply_theme, hero
apply_theme()

import streamlit as st
import pandas as pd
import psycopg2
import os
import plotly.express as px
import time
from dotenv import load_dotenv

load_dotenv()
st.set_page_config(page_title="Live Monitor", page_icon="📡", layout="wide")

def get_connection():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        database=os.getenv("POSTGRES_DB", "iot_cybersecurity"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD")
    )

@st.cache_data(ttl=2)
def load_data():
    conn = get_connection()
    df = pd.read_sql("""
        SELECT id, device_id, timestamp, ai_anomaly_status, anomaly_score,
               attack_status, attack_type, severity, network_traffic, packet_rate,
               latency, cpu_usage, memory_usage, detection_reason
        FROM cyber_attack_results
        ORDER BY timestamp DESC LIMIT 200
    """, conn)
    conn.close()
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df

hero("Live Security Monitor", "Continuous device telemetry with AI anomaly and cyber attack detection.", True)

with st.sidebar:
    st.markdown("### 📡 Live Controls")
    auto = st.checkbox("🔄 Auto refresh", value=True)
    device = st.selectbox("Device", ["All devices","SE-001","SE-002","SE-003"])

try:
    df=load_data()
except Exception as e:
    st.error("Database connection failed.")
    st.code(str(e))
    st.stop()

if device != "All devices":
    df=df[df["device_id"]==device].copy()

if df.empty:
    st.warning("No live events available.")
    st.stop()

attack = df["attack_status"].astype(str).str.upper().isin(["SUSPICIOUS","ATTACK","MALICIOUS"])
anomaly = df["ai_anomaly_status"].astype(str).str.upper().eq("ANOMALY")
latest=df.iloc[0]

st.success(f"🟢 LIVE • {latest['device_id']} • Last event {latest['timestamp'].strftime('%H:%M:%S')}")

a,b,c,d = st.columns(4)
a.metric("Events",len(df))
b.metric("Attacks",int(attack.sum()))
c.metric("AI Anomalies",int(anomaly.sum()))
d.metric("High Severity",int((df["severity"].astype(str).str.upper()=="HIGH").sum()))

st.subheader("📊 Live Telemetry")
m1,m2,m3,m4,m5=st.columns(5)
m1.metric("Network Traffic",f"{float(latest['network_traffic']):.2f}")
m2.metric("Packet Rate",f"{float(latest['packet_rate']):.2f}")
m3.metric("Latency",f"{float(latest['latency']):.2f}")
m4.metric("CPU",f"{float(latest['cpu_usage']):.1f}%")
m5.metric("Memory",f"{float(latest['memory_usage']):.1f}%")

trend=df.sort_values("timestamp").rename(columns={"timestamp":"time"})
left,right=st.columns(2)
with left:
    fig=px.line(trend,x="time",y="packet_rate",template="plotly_dark",markers=True)
    fig.update_layout(height=330,margin=dict(l=10,r=10,t=30,b=10),yaxis_title="Packets / rate")
    st.plotly_chart(fig,use_container_width=True)
with right:
    fig=px.line(trend,x="time",y=["network_traffic","latency"],template="plotly_dark")
    fig.update_layout(height=330,margin=dict(l=10,r=10,t=30,b=10))
    st.plotly_chart(fig,use_container_width=True)

st.subheader("🧠 AI Detection Signal")
fig=px.scatter(trend,x="time",y="anomaly_score",color="ai_anomaly_status",
               hover_data=["device_id","attack_type","severity"],template="plotly_dark")
fig.update_layout(height=320,margin=dict(l=10,r=10,t=30,b=10))
st.plotly_chart(fig,use_container_width=True)

st.subheader("🚨 Latest Security Events")
st.dataframe(df[["timestamp","device_id","ai_anomaly_status","attack_status","attack_type","severity","detection_reason"]],
             use_container_width=True,hide_index=True)

if auto:
    time.sleep(5)
    st.cache_data.clear()
    st.rerun()

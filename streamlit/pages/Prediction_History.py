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

st.set_page_config(
    page_title="Prediction History",
    page_icon="📜",
    layout="wide"
)


def get_connection():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        database=os.getenv("POSTGRES_DB", "iot_cybersecurity"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD")
    )


@st.cache_data(ttl=3)
def load_predictions():
    conn = get_connection()
    query = """
        SELECT
            id, timestamp, attack_status, attack_probability,
            predicted_attack_type, attack_type_confidence,
            src_port, dst_port, proto, service, duration,
            src_bytes, dst_bytes, src_pkts, dst_pkts,
            conn_state, processed_at
        FROM network_ml_predictions
        ORDER BY timestamp DESC
        LIMIT 5000
    """
    df = pd.read_sql(query, conn)
    conn.close()
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    return df


hero(
    "Prediction History",
    "Explore AI-generated network security predictions, confidence and attack behaviour over time.",
    True
)

with st.sidebar:
    st.markdown("### 🎛️ History Controls")
    auto = st.checkbox("🔄 Auto refresh", value=True)
    status_filter = st.selectbox(
        "Security Status",
        ["All", "NORMAL", "ATTACK"]
    )

try:
    df = load_predictions()
except Exception as e:
    st.error("Database connection failed.")
    st.code(str(e))
    st.stop()

if df.empty:
    st.info("No predictions have been stored yet.")
    st.stop()

df["attack_status"] = df["attack_status"].fillna("UNKNOWN").astype(str)
df["predicted_attack_type"] = df["predicted_attack_type"].fillna("unknown").astype(str)
df["attack_probability"] = pd.to_numeric(df["attack_probability"], errors="coerce").fillna(0)
df["attack_type_confidence"] = pd.to_numeric(
    df["attack_type_confidence"], errors="coerce"
).fillna(0)

filtered = df.copy()

if status_filter != "All":
    filtered = filtered[
        filtered["attack_status"].str.upper() == status_filter
    ]

type_options = ["All"] + sorted(
    df["predicted_attack_type"].dropna().unique().tolist()
)

with st.sidebar:
    type_filter = st.selectbox("Predicted Attack Type", type_options)
    min_probability = st.slider(
        "Minimum Attack Probability",
        0.0, 1.0, 0.0, 0.05
    )

if type_filter != "All":
    filtered = filtered[
        filtered["predicted_attack_type"] == type_filter
    ]

filtered = filtered[
    filtered["attack_probability"] >= min_probability
].copy()

total = len(df)
attacks = int(
    df["attack_status"].str.upper().eq("ATTACK").sum()
)
normal = int(
    df["attack_status"].str.upper().eq("NORMAL").sum()
)
avg_probability = float(df["attack_probability"].mean())
avg_confidence = float(df["attack_type_confidence"].mean())

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("📜 Predictions", f"{total:,}")
c2.metric("🚨 Attacks", f"{attacks:,}")
c3.metric("🟢 Normal", f"{normal:,}")
c4.metric("🎯 Avg Attack Probability", f"{avg_probability * 100:.1f}%")
c5.metric("🧠 Avg Confidence", f"{avg_confidence * 100:.1f}%")

st.markdown("### 📊 Prediction Intelligence")

left, right = st.columns(2)

with left:
    status_counts = df["attack_status"].value_counts().reset_index()
    status_counts.columns = ["status", "count"]
    fig = px.pie(
        status_counts,
        names="status",
        values="count",
        hole=0.58,
        template="plotly_dark"
    )
    fig.update_layout(
        height=350,
        margin=dict(l=10, r=10, t=25, b=10),
        legend_title_text="Status"
    )
    st.plotly_chart(fig, use_container_width=True)

with right:
    type_counts = (
        df["predicted_attack_type"]
        .value_counts()
        .reset_index()
    )
    type_counts.columns = ["attack_type", "count"]
    fig = px.bar(
        type_counts.head(12),
        x="attack_type",
        y="count",
        text_auto=True,
        template="plotly_dark"
    )
    fig.update_layout(
        height=350,
        margin=dict(l=10, r=10, t=25, b=10),
        xaxis_title="",
        yaxis_title="Predictions"
    )
    st.plotly_chart(fig, use_container_width=True)

st.markdown("### 📈 AI Risk Trends")

trend = df.sort_values("timestamp").copy()
trend["attack_probability_pct"] = trend["attack_probability"] * 100
trend["confidence_pct"] = trend["attack_type_confidence"] * 100

fig = px.line(
    trend,
    x="timestamp",
    y=["attack_probability_pct", "confidence_pct"],
    template="plotly_dark",
    labels={
        "value": "Percentage",
        "variable": "AI Signal"
    }
)
fig.update_layout(
    height=380,
    margin=dict(l=10, r=10, t=25, b=10),
    xaxis_title="Time",
    yaxis_title="%"
)
st.plotly_chart(fig, use_container_width=True)

st.markdown("### 🔎 Filtered Results")

f1, f2, f3 = st.columns(3)
f1.metric("Matching Records", f"{len(filtered):,}")
f2.metric(
    "Matching Attacks",
    f"{int(filtered['attack_status'].str.upper().eq('ATTACK').sum()):,}"
)
f3.metric(
    "Latest Prediction",
    df.iloc[0]["attack_status"]
)

if not filtered.empty:
    table = filtered.sort_values("timestamp", ascending=False)[[
        "timestamp",
        "attack_status",
        "attack_probability",
        "predicted_attack_type",
        "attack_type_confidence",
        "src_port",
        "dst_port",
        "proto",
        "service",
        "conn_state"
    ]].head(150).copy()

    table["attack_probability"] = (
        table["attack_probability"] * 100
    ).round(2)
    table["attack_type_confidence"] = (
        table["attack_type_confidence"] * 100
    ).round(2)

    table = table.rename(columns={
        "timestamp": "Timestamp",
        "attack_status": "Status",
        "attack_probability": "Attack Probability (%)",
        "predicted_attack_type": "Predicted Attack",
        "attack_type_confidence": "Confidence (%)",
        "src_port": "Source Port",
        "dst_port": "Destination Port",
        "proto": "Protocol",
        "service": "Service",
        "conn_state": "Connection State"
    })

    st.dataframe(
        table,
        use_container_width=True,
        hide_index=True
    )
else:
    st.info("No prediction records match the selected filters.")

csv_data = filtered.to_csv(index=False).encode("utf-8")
st.download_button(
    "⬇️ Download Filtered History",
    data=csv_data,
    file_name="prediction_history_filtered.csv",
    mime="text/csv",
    use_container_width=True
)

st.caption(
    "🔄 Live prediction history refreshes every 5 seconds when Auto refresh is enabled."
)

if auto:
    time.sleep(5)
    st.cache_data.clear()
    st.rerun()

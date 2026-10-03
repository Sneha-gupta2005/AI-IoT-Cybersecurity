from ui import apply_theme, hero
apply_theme()

import streamlit as st
import pandas as pd
import os
import plotly.express as px

st.set_page_config(page_title="Dataset Explorer", page_icon="📊", layout="wide")

hero("Dataset Explorer", "Interactive exploration of the processed TON-IoT network cybersecurity dataset.", False)

DATASET_PATH = "datasets/processed/ton_iot_network_processed.csv"

if not os.path.exists(DATASET_PATH):
    st.error("Processed TON-IoT dataset was not found.")
    st.code(DATASET_PATH)
    st.stop()

@st.cache_data
def load_dataset():
    return pd.read_csv(DATASET_PATH)

try:
    df = load_dataset()
except Exception as e:
    st.error("Dataset loading failed.")
    st.code(str(e))
    st.stop()

with st.sidebar:
    st.markdown("### 🎛️ Explorer Controls")
    sample_size = st.slider("Sample rows", 5, 100, 20, 5)
    search = st.text_input("🔎 Search feature", placeholder="bytes, port, proto...")
    label_filter = st.selectbox("Binary Label", ["All", "Normal", "Attack"])
    attack_options = ["All"] + sorted(df["attack_type"].dropna().astype(str).unique().tolist()) if "attack_type" in df.columns else ["All"]
    attack_filter = st.selectbox("Attack Type", attack_options)

c1,c2,c3,c4 = st.columns(4)
c1.metric("📄 Records", f"{len(df):,}")
c2.metric("🧩 Columns", df.shape[1])
c3.metric("🤖 ML Features", max(df.shape[1]-2, 0))
c4.metric("⚠️ Missing Values", f"{int(df.isnull().sum().sum()):,}")

st.subheader("🎯 Target Distribution")
if "label" in df.columns:
    labels = df["label"].value_counts().sort_index().reset_index()
    labels.columns = ["label","count"]
    labels["name"] = labels["label"].map({0:"Normal",1:"Attack"}).fillna(labels["label"].astype(str))
    left,right = st.columns(2)
    with left:
        fig = px.pie(labels, names="name", values="count", hole=.55, template="plotly_dark")
        fig.update_layout(height=330, margin=dict(l=10,r=10,t=30,b=10))
        st.plotly_chart(fig, use_container_width=True)
    with right:
        fig = px.bar(labels, x="name", y="count", text_auto=True, template="plotly_dark")
        fig.update_layout(height=330, margin=dict(l=10,r=10,t=30,b=10), xaxis_title="")
        st.plotly_chart(fig, use_container_width=True)

st.subheader("🚨 Attack Classes")
if "attack_type" in df.columns:
    attacks = df["attack_type"].astype(str).value_counts().reset_index()
    attacks.columns = ["attack_type","count"]
    fig = px.bar(attacks, x="attack_type", y="count", text_auto=True,
                 template="plotly_dark", hover_data=["count"])
    fig.update_layout(height=360, margin=dict(l=10,r=10,t=30,b=10), xaxis_title="")
    st.plotly_chart(fig, use_container_width=True)

st.subheader("🧩 Feature Information")
feature_columns = [c for c in df.columns if c not in ["label","attack_type"]]
feature_info = pd.DataFrame({
    "Feature": feature_columns,
    "Data Type": [str(df[c].dtype) for c in feature_columns],
    "Missing Values": [int(df[c].isnull().sum()) for c in feature_columns],
    "Unique Values": [int(df[c].nunique()) for c in feature_columns]
})
if search:
    feature_info = feature_info[feature_info["Feature"].str.contains(search, case=False, na=False)]
st.dataframe(feature_info, use_container_width=True, hide_index=True)

st.subheader("🎛️ Filtered Dataset")
filtered = df.copy()
if label_filter == "Normal":
    filtered = filtered[filtered["label"] == 0]
elif label_filter == "Attack":
    filtered = filtered[filtered["label"] == 1]
if attack_filter != "All":
    filtered = filtered[filtered["attack_type"].astype(str) == attack_filter]

a,b = st.columns(2)
a.metric("Filtered Records", f"{len(filtered):,}")
b.metric("Filter Coverage", f"{(len(filtered)/len(df)*100 if len(df) else 0):.1f}%")

st.dataframe(filtered.head(100), use_container_width=True, hide_index=True)

st.subheader("📄 Dataset Sample")
st.dataframe(df.head(sample_size), use_container_width=True, hide_index=True)

csv_data = filtered.to_csv(index=False).encode("utf-8")
st.download_button("⬇️ Download Filtered Dataset", csv_data,
                   "ton_iot_filtered.csv", "text/csv", use_container_width=True)

st.divider()
st.info("📌 Dataset: processed TON-IoT network traffic • Use the filters and feature search to inspect the data before model training/evaluation.")

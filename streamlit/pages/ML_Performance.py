from ui import apply_theme, hero
apply_theme()

import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="ML Performance", page_icon="🤖", layout="wide")

hero("ML Performance", "Interactive evaluation view for the TON-IoT-trained cybersecurity models.", False)

st.sidebar.markdown("### 🤖 Model Controls")
model_view = st.sidebar.radio("View", ["Binary Detection", "Multi-Class Detection", "Both"], index=2)
st.sidebar.caption("Metrics shown here are the current experiment results.")

binary_metrics = pd.DataFrame({
    "Metric":["Accuracy","Precision","Recall","F1 Score","ROC-AUC","PR-AUC"],
    "Score":[0.9986,0.9993,0.9989,0.9991,1.0,1.0]
})

class_metrics = pd.DataFrame({
    "Attack Type":["backdoor","ddos","dos","injection","mitm","normal","password","ransomware","scanning","xss"],
    "Precision":[1.00,0.99,0.99,0.98,0.75,1.00,0.99,1.00,0.99,0.97],
    "Recall":[1.00,0.98,0.99,0.97,0.79,1.00,0.99,1.00,0.99,0.98],
    "F1 Score":[1.00,0.99,0.99,0.98,0.77,1.00,0.99,1.00,0.99,0.97]
})

labels = class_metrics["Attack Type"].tolist()
multi_cm = pd.DataFrame([
    [3741,0,1,0,0,0,0,0,0,0],
    [0,3937,0,20,0,8,1,1,0,32],
    [0,1,3744,4,25,1,5,0,19,0],
    [0,15,5,3883,4,2,1,0,12,71],
    [0,2,9,6,165,7,13,0,4,2],
    [0,8,3,0,6,8389,0,0,1,1],
    [0,2,6,1,17,1,3941,0,2,2],
    [0,0,0,0,0,0,0,2947,0,0],
    [0,0,13,2,1,2,2,0,3978,0],
    [0,4,0,40,1,2,0,0,0,2980]
], index=labels, columns=labels)

if model_view in ["Binary Detection", "Both"]:
    st.subheader("🛡️ Binary Cyber Attack Detection")
    st.info("XGBoost Binary Classifier • TON-IoT Network Traffic • 20% stratified test split")
    c1,c2,c3,c4,c5 = st.columns(5)
    c1.metric("Accuracy","99.86%")
    c2.metric("Precision","99.93%")
    c3.metric("Recall","99.89%")
    c4.metric("F1 Score","99.91%")
    c5.metric("ROC-AUC","1.0000")

    left,right = st.columns(2)
    with left:
        fig = px.bar(binary_metrics, x="Metric", y="Score", text="Score", template="plotly_dark")
        fig.update_yaxes(range=[0,1.05])
        fig.update_layout(height=360, margin=dict(l=10,r=10,t=30,b=10))
        st.plotly_chart(fig, use_container_width=True)
    with right:
        binary_cm = pd.DataFrame([[8387,21],[32,29655]],
                                 index=["Actual Normal","Actual Attack"],
                                 columns=["Predicted Normal","Predicted Attack"])
        fig = px.imshow(binary_cm, text_auto=True, template="plotly_dark",
                        labels={"x":"Predicted","y":"Actual","color":"Samples"})
        fig.update_layout(height=360, margin=dict(l=10,r=10,t=30,b=10))
        st.plotly_chart(fig, use_container_width=True)

if model_view in ["Multi-Class Detection", "Both"]:
    st.divider()
    st.subheader("🎯 Multi-Class Attack Type Detection")
    st.info("XGBoost Multi-Class Classifier • 10 classes • 20% stratified test split")
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Accuracy","98.98%")
    c2.metric("Precision","98.99%")
    c3.metric("Recall","98.98%")
    c4.metric("F1 Score","98.98%")

    st.subheader("📊 Class-wise Performance")
    st.dataframe(class_metrics, use_container_width=True, hide_index=True)

    left,right = st.columns(2)
    with left:
        fig = px.bar(class_metrics, x="Attack Type", y="F1 Score", text="F1 Score",
                     template="plotly_dark")
        fig.update_yaxes(range=[0,1.05])
        fig.update_layout(height=360, margin=dict(l=10,r=10,t=30,b=10))
        st.plotly_chart(fig, use_container_width=True)
    with right:
        fig = px.bar(class_metrics, x="Attack Type", y=["Precision","Recall"],
                     barmode="group", template="plotly_dark")
        fig.update_yaxes(range=[0,1.05])
        fig.update_layout(height=360, margin=dict(l=10,r=10,t=30,b=10))
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("🔢 Multi-Class Confusion Matrix")
    fig = px.imshow(multi_cm, text_auto=True, aspect="auto", template="plotly_dark",
                    labels={"x":"Predicted Attack Type","y":"Actual Attack Type","color":"Samples"})
    fig.update_layout(height=600, margin=dict(l=10,r=10,t=30,b=10))
    st.plotly_chart(fig, use_container_width=True)

st.divider()
st.subheader("ℹ️ Research Evaluation Note")
st.warning(
    "These are the current TON-IoT train/test experiment results. "
    "For final research claims, validate generalization with leakage checks, "
    "a training-only preprocessing pipeline, and preferably an independent or time-based validation split."
)
st.caption("MITM has fewer samples than most other attack classes, which affects its class-wise performance.")

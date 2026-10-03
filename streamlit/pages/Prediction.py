from ui import apply_theme, hero
apply_theme()

import streamlit as st
import requests

st.set_page_config(page_title="AI Prediction", page_icon="🔮", layout="wide")

API_URL = "http://127.0.0.1:8000/predict"

hero("AI Network Traffic Prediction",
     "Run an on-demand XGBoost security classification using network-flow features.",
     False)

with st.sidebar:
    st.markdown("### ⚙️ Prediction Controls")
    st.caption("Model: XGBoost • Dataset: TON-IoT")
    st.caption("API: FastAPI /predict")
    st.divider()
    st.info("Change the feature values, then click Analyze. No replay data is used.")

st.subheader("🌐 Network Flow")
c1, c2, c3 = st.columns(3)
with c1:
    src_port = st.number_input("Source Port", 0, 65535, 50000)
    dst_port = st.number_input("Destination Port", 0, 65535, 80)
    proto = st.selectbox("Protocol", ["tcp", "udp", "icmp"])
    service = st.selectbox("Service", ["http", "dns", "ssh", "ftp", "ssl", "other"])
with c2:
    duration = st.number_input("Duration", 0.0, value=1.0, step=0.1)
    src_bytes = st.number_input("Source Bytes", 0.0, value=500.0, step=10.0)
    dst_bytes = st.number_input("Destination Bytes", 0.0, value=1000.0, step=10.0)
    missed_bytes = st.number_input("Missed Bytes", 0.0, value=0.0, step=1.0)
with c3:
    src_pkts = st.number_input("Source Packets", 0.0, value=10.0, step=1.0)
    dst_pkts = st.number_input("Destination Packets", 0.0, value=15.0, step=1.0)
    src_ip_bytes = st.number_input("Source IP Bytes", 0.0, value=500.0, step=10.0)
    dst_ip_bytes = st.number_input("Destination IP Bytes", 0.0, value=1000.0, step=10.0)

st.subheader("🔗 Connection")
c1, c2, c3 = st.columns(3)
with c1:
    conn_state = st.selectbox("Connection State", ["SF", "S0", "REJ", "RSTO", "RSTR", "OTH"])
with c2:
    dns_qclass = st.number_input("DNS Query Class", 0, value=1)
    dns_qtype = st.number_input("DNS Query Type", 0, value=1)
with c3:
    dns_rcode = st.number_input("DNS Response Code", 0, value=0)

with st.expander("⚙️ Advanced DNS / SSL / HTTP Features"):
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("**DNS**")
        dns_AA = st.selectbox("DNS AA", [0, 1])
        dns_RD = st.selectbox("DNS RD", [0, 1])
        dns_RA = st.selectbox("DNS RA", [0, 1])
        dns_rejected = st.selectbox("DNS Rejected", [0, 1])
    with c2:
        st.markdown("**SSL**")
        ssl_version = st.selectbox("SSL Version", ["unknown", "TLSv10", "TLSv12", "TLSv13"])
        ssl_cipher = st.selectbox("SSL Cipher", ["unknown", "TLS_AES_128_GCM_SHA256", "TLS_AES_256_GCM_SHA384"])
        ssl_resumed = st.selectbox("SSL Resumed", [0, 1])
        ssl_established = st.selectbox("SSL Established", [0, 1])
    with c3:
        st.markdown("**HTTP**")
        http_trans_depth = st.number_input("HTTP Transaction Depth", 0, value=1)
        http_method = st.selectbox("HTTP Method", ["GET", "POST", "PUT", "DELETE", "unknown"])
        http_version = st.selectbox("HTTP Version", ["1.0", "1.1", "2.0", "unknown"])
        http_request_body_len = st.number_input("HTTP Request Body Length", 0.0, value=0.0, step=10.0)
        http_response_body_len = st.number_input("HTTP Response Body Length", 0.0, value=0.0, step=10.0)
        http_status_code = st.number_input("HTTP Status Code", 0, 599, 200)

st.divider()
st.subheader("🚀 Run AI Analysis")
predict_button = st.button("🚀 Analyze Network Traffic", type="primary", use_container_width=True)

if predict_button:
    payload = {"features": {
        "src_port": src_port, "dst_port": dst_port, "proto": proto, "service": service,
        "duration": duration, "src_bytes": src_bytes, "dst_bytes": dst_bytes, "missed_bytes": missed_bytes,
        "src_pkts": src_pkts, "dst_pkts": dst_pkts, "src_ip_bytes": src_ip_bytes, "dst_ip_bytes": dst_ip_bytes,
        "conn_state": conn_state, "dns_qclass": dns_qclass, "dns_qtype": dns_qtype,
        "dns_rcode": dns_rcode, "dns_AA": dns_AA, "dns_RD": dns_RD, "dns_RA": dns_RA,
        "dns_rejected": dns_rejected, "ssl_version": ssl_version, "ssl_cipher": ssl_cipher,
        "ssl_resumed": ssl_resumed, "ssl_established": ssl_established,
        "http_trans_depth": http_trans_depth, "http_method": http_method, "http_version": http_version,
        "http_request_body_len": http_request_body_len, "http_response_body_len": http_response_body_len,
        "http_status_code": http_status_code
    }}

    try:
        with st.spinner("🧠 XGBoost is analyzing the traffic..."):
            response = requests.post(API_URL, json=payload, timeout=10)

        if response.status_code == 200:
            result = response.json()
            attack_status = result.get("attack_status", "UNKNOWN")
            probability = float(result.get("attack_probability", 0))
            attack_type = result.get("predicted_attack_type", "unknown")
            confidence = float(result.get("attack_type_confidence", 0))

            st.success("✅ Prediction completed successfully.")
            st.subheader("🛡️ Security Decision")
            a, b, c = st.columns(3)
            a.metric("Security Status", attack_status)
            b.metric("Attack Probability", f"{probability * 100:.2f}%")
            c.metric("Predicted Attack", attack_type.upper())

            st.subheader("🎯 Classification Confidence")
            st.progress(max(0.0, min(confidence, 1.0)))
            st.caption(f"Confidence: {confidence * 100:.2f}%")

            st.subheader("📊 Model Information")
            a, b, c = st.columns(3)
            a.metric("Model", "XGBoost")
            b.metric("Training Dataset", "TON-IoT")
            c.metric("Features", result.get("feature_count", 72))

            if result.get("database_status") == "saved":
                st.success("💾 Prediction saved to PostgreSQL.")
            elif result.get("database_status") == "failed":
                st.warning("Prediction completed, but database storage failed.")

            with st.expander("📋 Complete API Response"):
                st.json(result)
        else:
            st.error(f"❌ API returned HTTP {response.status_code}")
            st.code(response.text)

    except requests.exceptions.ConnectionError:
        st.error("❌ FastAPI server is not running.")
        st.code("python -m uvicorn api.main:app --reload")
    except requests.exceptions.Timeout:
        st.error("⏱️ FastAPI request timed out.")
    except Exception as e:
        st.error("❌ Prediction failed.")
        st.code(str(e))

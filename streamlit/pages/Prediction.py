
import streamlit as st
import requests


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Network Traffic Prediction",
    page_icon="🔮",
    layout="wide"
)


# =========================================================
# PAGE HEADER
# =========================================================

st.title("🔮 Network Traffic Prediction")

st.caption(
    "On-demand cyber attack classification using "
    "user-provided network-flow features and a "
    "TON-IoT-trained XGBoost model."
)

st.info(
    "📌 Input Source: User-provided network-flow features. "
    "The model was trained and evaluated using the TON-IoT "
    "benchmark dataset."
)

st.divider()


# =========================================================
# API CONFIG
# =========================================================

API_URL = "http://127.0.0.1:8000/predict"


# =========================================================
# NETWORK TRAFFIC INPUT
# =========================================================

st.subheader("🌐 Network Traffic Features")

col1, col2, col3 = st.columns(3)


# =========================================================
# COLUMN 1
# =========================================================

with col1:

    src_port = st.number_input(
        "Source Port",
        min_value=0,
        max_value=65535,
        value=50000,
        step=1
    )

    dst_port = st.number_input(
        "Destination Port",
        min_value=0,
        max_value=65535,
        value=80,
        step=1
    )

    proto = st.selectbox(
        "Protocol",
        [
            "tcp",
            "udp",
            "icmp"
        ]
    )

    service = st.selectbox(
        "Service",
        [
            "http",
            "dns",
            "ssh",
            "ftp",
            "ssl",
            "other"
        ]
    )


# =========================================================
# COLUMN 2
# =========================================================

with col2:

    duration = st.number_input(
        "Duration",
        min_value=0.0,
        value=1.0,
        step=0.1
    )

    src_bytes = st.number_input(
        "Source Bytes",
        min_value=0.0,
        value=500.0,
        step=10.0
    )

    dst_bytes = st.number_input(
        "Destination Bytes",
        min_value=0.0,
        value=1000.0,
        step=10.0
    )

    missed_bytes = st.number_input(
        "Missed Bytes",
        min_value=0.0,
        value=0.0,
        step=1.0
    )


# =========================================================
# COLUMN 3
# =========================================================

with col3:

    src_pkts = st.number_input(
        "Source Packets",
        min_value=0.0,
        value=10.0,
        step=1.0
    )

    dst_pkts = st.number_input(
        "Destination Packets",
        min_value=0.0,
        value=15.0,
        step=1.0
    )

    src_ip_bytes = st.number_input(
        "Source IP Bytes",
        min_value=0.0,
        value=500.0,
        step=10.0
    )

    dst_ip_bytes = st.number_input(
        "Destination IP Bytes",
        min_value=0.0,
        value=1000.0,
        step=10.0
    )


# =========================================================
# CONNECTION INFORMATION
# =========================================================

st.divider()

st.subheader("🔗 Connection Information")

col1, col2, col3 = st.columns(3)


with col1:

    conn_state = st.selectbox(
        "Connection State",
        [
            "SF",
            "S0",
            "REJ",
            "RSTO",
            "RSTR",
            "OTH"
        ]
    )


with col2:

    dns_qclass = st.number_input(
        "DNS Query Class",
        min_value=0,
        value=1,
        step=1
    )


with col3:

    dns_qtype = st.number_input(
        "DNS Query Type",
        min_value=0,
        value=1,
        step=1
    )


# =========================================================
# ADVANCED NETWORK FEATURES
# =========================================================

st.divider()

with st.expander(
    "⚙️ Advanced Network Features"
):

    col1, col2, col3 = st.columns(3)


    # -----------------------------------------------------
    # DNS
    # -----------------------------------------------------

    with col1:

        st.markdown("### DNS")

        dns_rcode = st.number_input(
            "DNS Response Code",
            min_value=0,
            value=0,
            step=1
        )

        dns_AA = st.selectbox(
            "DNS AA",
            [0, 1]
        )

        dns_RD = st.selectbox(
            "DNS RD",
            [0, 1]
        )

        dns_RA = st.selectbox(
            "DNS RA",
            [0, 1]
        )

        dns_rejected = st.selectbox(
            "DNS Rejected",
            [0, 1]
        )


    # -----------------------------------------------------
    # SSL
    # -----------------------------------------------------

    with col2:

        st.markdown("### SSL")

        ssl_version = st.selectbox(
            "SSL Version",
            [
                "unknown",
                "TLSv10",
                "TLSv12",
                "TLSv13"
            ]
        )

        ssl_cipher = st.selectbox(
            "SSL Cipher",
            [
                "unknown",
                "TLS_AES_128_GCM_SHA256",
                "TLS_AES_256_GCM_SHA384"
            ]
        )

        ssl_resumed = st.selectbox(
            "SSL Resumed",
            [0, 1]
        )

        ssl_established = st.selectbox(
            "SSL Established",
            [0, 1]
        )


    # -----------------------------------------------------
    # HTTP
    # -----------------------------------------------------

    with col3:

        st.markdown("### HTTP")

        http_trans_depth = st.number_input(
            "HTTP Transaction Depth",
            min_value=0,
            value=1,
            step=1
        )

        http_method = st.selectbox(
            "HTTP Method",
            [
                "GET",
                "POST",
                "PUT",
                "DELETE",
                "unknown"
            ]
        )

        http_version = st.selectbox(
            "HTTP Version",
            [
                "1.0",
                "1.1",
                "2.0",
                "unknown"
            ]
        )

        http_request_body_len = st.number_input(
            "HTTP Request Body Length",
            min_value=0.0,
            value=0.0,
            step=10.0
        )

        http_response_body_len = st.number_input(
            "HTTP Response Body Length",
            min_value=0.0,
            value=0.0,
            step=10.0
        )

        http_status_code = st.number_input(
            "HTTP Status Code",
            min_value=0,
            max_value=599,
            value=200,
            step=1
        )


# =========================================================
# PREDICTION
# =========================================================

st.divider()

st.subheader("🚀 Run Prediction")

st.caption(
    "Prediction is performed only when you click the button."
)

predict_button = st.button(
    "🚀 Analyze Network Traffic",
    type="primary",
    use_container_width=True
)


# =========================================================
# PREDICTION REQUEST
# =========================================================

if predict_button:

    payload = {

        "features": {

            # Network
            "src_port": src_port,
            "dst_port": dst_port,
            "proto": proto,
            "service": service,

            # Traffic
            "duration": duration,
            "src_bytes": src_bytes,
            "dst_bytes": dst_bytes,
            "missed_bytes": missed_bytes,

            # Packets
            "src_pkts": src_pkts,
            "dst_pkts": dst_pkts,
            "src_ip_bytes": src_ip_bytes,
            "dst_ip_bytes": dst_ip_bytes,

            # Connection
            "conn_state": conn_state,

            # DNS
            "dns_qclass": dns_qclass,
            "dns_qtype": dns_qtype,
            "dns_rcode": dns_rcode,
            "dns_AA": dns_AA,
            "dns_RD": dns_RD,
            "dns_RA": dns_RA,
            "dns_rejected": dns_rejected,

            # SSL
            "ssl_version": ssl_version,
            "ssl_cipher": ssl_cipher,
            "ssl_resumed": ssl_resumed,
            "ssl_established": ssl_established,

            # HTTP
            "http_trans_depth": http_trans_depth,
            "http_method": http_method,
            "http_version": http_version,
            "http_request_body_len":
                http_request_body_len,
            "http_response_body_len":
                http_response_body_len,
            "http_status_code":
                http_status_code
        }
    }


    # =====================================================
    # API CALL
    # =====================================================

    try:

        with st.spinner(
            "🧠 XGBoost is analyzing the network traffic..."
        ):

            response = requests.post(
                API_URL,
                json=payload,
                timeout=10
            )


        # =================================================
        # SUCCESS
        # =================================================

        if response.status_code == 200:

            result = response.json()

            st.success(
                "✅ Prediction completed successfully."
            )

            st.divider()


            # =================================================
            # RESULT VALUES
            # =================================================

            attack_status = result.get(
                "attack_status",
                "UNKNOWN"
            )

            attack_probability = float(
                result.get(
                    "attack_probability",
                    0
                )
            )

            attack_type = result.get(
                "predicted_attack_type",
                "unknown"
            )

            confidence = float(
                result.get(
                    "attack_type_confidence",
                    0
                )
            )


            # =================================================
            # MAIN RESULT
            # =================================================

            st.subheader("🧠 AI Prediction Result")

            col1, col2, col3 = st.columns(3)


            col1.metric(
                "Security Status",
                attack_status
            )


            col2.metric(
                "Attack Probability",
                f"{attack_probability * 100:.2f}%"
            )


            col3.metric(
                "Predicted Attack Type",
                attack_type.upper()
            )


            # =================================================
            # CONFIDENCE
            # =================================================

            st.divider()

            st.subheader(
                "🎯 Attack Classification Confidence"
            )

            st.progress(
                min(
                    max(
                        confidence,
                        0.0
                    ),
                    1.0
                )
            )

            st.write(
                f"Confidence: **{confidence * 100:.2f}%**"
            )


            # =================================================
            # MODEL INFORMATION
            # =================================================

            st.divider()

            st.subheader(
                "📊 Model Information"
            )

            info_col1, info_col2, info_col3 = st.columns(3)

            info_col1.metric(
                "Model",
                "XGBoost"
            )

            info_col2.metric(
                "Training Dataset",
                "TON-IoT"
            )

            info_col3.metric(
                "Features Used",
                result.get(
                    "feature_count",
                    72
                )
            )


            # =================================================
            # DATABASE STATUS
            # =================================================

            database_status = result.get(
                "database_status"
            )

            if database_status == "saved":

                st.success(
                    "💾 Prediction saved to PostgreSQL."
                )

            elif database_status == "failed":

                st.warning(
                    "Prediction completed, but "
                    "database storage failed."
                )


            # =================================================
            # API RESPONSE
            # =================================================

            with st.expander(
                "📋 View Complete API Response"
            ):

                st.json(result)


        # =================================================
        # API ERROR
        # =================================================

        else:

            st.error(
                f"❌ API returned HTTP "
                f"{response.status_code}"
            )

            st.code(
                response.text
            )


    # =====================================================
    # CONNECTION ERROR
    # =====================================================

    except requests.exceptions.ConnectionError:

        st.error(
            "❌ FastAPI server is not running."
        )

        st.info(
            "Start FastAPI from the project root "
            "in another terminal:"
        )

        st.code(
            "python -m uvicorn api.main:app --reload"
        )


    # =====================================================
    # TIMEOUT
    # =====================================================

    except requests.exceptions.Timeout:

        st.error(
            "⏱️ FastAPI request timed out."
        )

        st.info(
            "Check whether the FastAPI server "
            "and PostgreSQL are running."
        )


    # =====================================================
    # OTHER ERROR
    # =====================================================

    except Exception as e:

        st.error(
            "❌ Prediction failed."
        )

        st.code(
            str(e)
        )

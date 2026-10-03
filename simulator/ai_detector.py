import json
import os
import joblib
import numpy as np
import paho.mqtt.client as mqtt
import psycopg2

from datetime import datetime
from dotenv import load_dotenv


# ============================================================
# PROJECT PATH
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_FILE = os.path.join(
    BASE_DIR,
    "anomaly_model.joblib"
)


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

ENV_FILE = os.path.join(
    BASE_DIR,
    ".env"
)

load_dotenv(ENV_FILE)


# ============================================================
# MQTT CONFIGURATION
# ============================================================

MQTT_BROKER = os.getenv("MQTT_BROKER")
MQTT_PORT = int(os.getenv("MQTT_PORT", "8883"))

MQTT_USERNAME = os.getenv("MQTT_USERNAME")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")

MQTT_TOPIC = "iot/devices/telemetry"
AI_TOPIC = "iot/devices/ai-anomaly"


# ============================================================
# POSTGRESQL CONFIGURATION
# ============================================================

POSTGRES_HOST = os.getenv(
    "POSTGRES_HOST",
    "localhost"
)

POSTGRES_PORT = os.getenv(
    "POSTGRES_PORT",
    "5432"
)

POSTGRES_DB = os.getenv(
    "POSTGRES_DB",
    "iot_cybersecurity"
)

POSTGRES_USER = os.getenv(
    "POSTGRES_USER",
    "postgres"
)

POSTGRES_PASSWORD = os.getenv(
    "POSTGRES_PASSWORD"
)


# ============================================================
# STARTUP INFORMATION
# ============================================================

print("=" * 60)
print("AI + IoT CYBERSECURITY DETECTOR")
print("=" * 60)

print("Project directory:", BASE_DIR)
print("Model file:", MODEL_FILE)
print("MQTT topic:", MQTT_TOPIC)
print("AI topic:", AI_TOPIC)
print("PostgreSQL database:", POSTGRES_DB)


# ============================================================
# LOAD AI MODEL
# ============================================================

print("\nLoading AI model...")

try:

    model_package = joblib.load(
        MODEL_FILE
    )

    if isinstance(model_package, dict):

        model = model_package.get("model")
        scaler = model_package.get("scaler")
        feature_columns = model_package.get("features")

        if model is None:
            raise ValueError(
                "Model package does not contain 'model'."
            )

    else:

        model = model_package
        scaler = None
        feature_columns = None

    print("AI model loaded successfully.")

except Exception as e:

    print("MODEL ERROR:", e)
    raise SystemExit(1)


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_db_connection():

    return psycopg2.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        database=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD
    )


# ============================================================
# TEST DATABASE CONNECTION
# ============================================================

print("\nTesting PostgreSQL connection...")

try:

    test_conn = get_db_connection()

    test_cursor = test_conn.cursor()

    test_cursor.execute(
        "SELECT current_database();"
    )

    database_name = test_cursor.fetchone()[0]

    print(
        "PostgreSQL connected successfully:",
        database_name
    )

    test_cursor.close()
    test_conn.close()

except Exception as e:

    print("PostgreSQL connection ERROR:", e)
    raise SystemExit(1)


# ============================================================
# CYBER ATTACK DETECTION
# ============================================================

def detect_cyber_attack(
    data,
    ai_status
):

    network_traffic = float(
        data.get("network_traffic", 0) or 0
    )

    packet_rate = float(
        data.get("packet_rate", 0) or 0
    )

    latency = float(
        data.get("latency", 0) or 0
    )

    cpu_usage = float(
        data.get("cpu_usage", 0) or 0
    )

    memory_usage = float(
        data.get("memory_usage", 0) or 0
    )


    # ========================================================
    # NETWORK FLOOD
    # ========================================================

    if (
        network_traffic > 900
        and packet_rate > 180
        and latency > 100
    ):

        return (
            "SUSPICIOUS",
            "NETWORK_FLOOD",
            "HIGH",
            "High network traffic, packet rate and latency"
        )


    # ========================================================
    # PACKET FLOOD
    # ========================================================

    elif (
        packet_rate > 180
        and latency > 100
    ):

        return (
            "SUSPICIOUS",
            "PACKET_FLOOD",
            "HIGH",
            "Abnormally high packet rate and latency"
        )


    # ========================================================
    # RESOURCE EXHAUSTION
    # ========================================================

    elif (
        cpu_usage > 90
        and memory_usage > 90
        and ai_status == "ANOMALY"
    ):

        return (
            "SUSPICIOUS",
            "RESOURCE_EXHAUSTION",
            "HIGH",
            "High CPU and memory utilization with AI anomaly"
        )


    # ========================================================
    # NETWORK ANOMALY
    # ========================================================

    elif (
        network_traffic > 700
        and ai_status == "ANOMALY"
    ):

        return (
            "SUSPICIOUS",
            "NETWORK_ANOMALY",
            "MEDIUM",
            "High network traffic with AI anomaly"
        )


    # ========================================================
    # LATENCY ATTACK
    # ========================================================

    elif (
        latency > 150
        and ai_status == "ANOMALY"
    ):

        return (
            "SUSPICIOUS",
            "LATENCY_ATTACK",
            "MEDIUM",
            "Abnormally high latency with AI anomaly"
        )


    # ========================================================
    # AI ANOMALY ONLY
    # ========================================================

    elif ai_status == "ANOMALY":

        return (
            "ANOMALY_ONLY",
            "DEVICE_ANOMALY",
            "LOW",
            "AI model detected abnormal device behavior"
        )


    # ========================================================
    # NORMAL
    # ========================================================

    else:

        return (
            "NO_ATTACK",
            "NONE",
            "LOW",
            "Normal telemetry"
        )


# ============================================================
# SAVE RESULTS TO POSTGRESQL
# ============================================================

def save_to_database(
    data,
    ai_status,
    anomaly_score
):

    conn = None
    cursor = None

    try:

        # ----------------------------------------------------
        # OPEN CONNECTION
        # ----------------------------------------------------

        conn = get_db_connection()

        cursor = conn.cursor()


        # ----------------------------------------------------
        # TIMESTAMP
        # ----------------------------------------------------

        timestamp = data.get(
            "timestamp"
        )

        if not timestamp:

            timestamp = datetime.now()


        # ====================================================
        # 1. SAVE AI ANOMALY RESULT
        # ====================================================

        ai_query = """
        INSERT INTO ai_anomaly_results (
            device_id,
            timestamp,
            ai_anomaly_status,
            anomaly_score,
            temperature,
            voltage,
            current,
            power,
            cpu_usage,
            memory_usage,
            network_traffic,
            packet_rate,
            latency,
            processed_at
        )
        VALUES (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            CURRENT_TIMESTAMP
        )
        """

        ai_values = (

            data.get("device_id"),

            timestamp,

            ai_status,

            float(anomaly_score),

            data.get("temperature"),

            data.get("voltage"),

            data.get("current"),

            data.get("power"),

            data.get("cpu_usage"),

            data.get("memory_usage"),

            data.get("network_traffic"),

            data.get("packet_rate"),

            data.get("latency")
        )

        cursor.execute(
            ai_query,
            ai_values
        )

        print(
            "Saved to PostgreSQL: ai_anomaly_results"
        )


        # ====================================================
        # 2. CYBER ATTACK DETECTION
        # ====================================================

        (
            attack_status,
            attack_type,
            severity,
            detection_reason

        ) = detect_cyber_attack(
            data,
            ai_status
        )


        # ====================================================
        # 3. SAVE CYBER ATTACK RESULT
        # ====================================================

        cyber_query = """
        INSERT INTO cyber_attack_results (
            device_id,
            timestamp,
            ai_anomaly_status,
            anomaly_score,
            attack_status,
            attack_type,
            severity,
            temperature,
            cpu_usage,
            memory_usage,
            network_traffic,
            packet_rate,
            latency,
            detection_reason,
            processed_at
        )
        VALUES (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            CURRENT_TIMESTAMP
        )
        """

        cyber_values = (

            data.get("device_id"),

            timestamp,

            ai_status,

            float(anomaly_score),

            attack_status,

            attack_type,

            severity,

            data.get("temperature"),

            data.get("cpu_usage"),

            data.get("memory_usage"),

            data.get("network_traffic"),

            data.get("packet_rate"),

            data.get("latency"),

            detection_reason
        )

        cursor.execute(
            cyber_query,
            cyber_values
        )


        # ====================================================
        # COMMIT BOTH INSERTS
        # ====================================================

        conn.commit()


        print(
            "Saved to PostgreSQL: cyber_attack_results"
        )

        print(
            "Attack Status:",
            attack_status
        )

        print(
            "Attack Type:",
            attack_type
        )

        print(
            "Severity:",
            severity
        )


        return True


    except Exception as e:

        print(
            "PostgreSQL ERROR:",
            repr(e)
        )

        if conn:

            conn.rollback()

        return False


    finally:

        if cursor:

            cursor.close()

        if conn:

            conn.close()


# ============================================================
# MQTT CONNECT CALLBACK
# ============================================================

def on_connect(
    client,
    userdata,
    flags,
    rc
):

    if rc == 0:

        print("\nConnected to MQTT broker.")

        print(
            "Subscribing to:",
            MQTT_TOPIC
        )

        result = client.subscribe(
            MQTT_TOPIC
        )

        print(
            "MQTT subscription result:",
            result
        )

    else:

        print(
            "MQTT connection failed. Code:",
            rc
        )


# ============================================================
# MQTT MESSAGE CALLBACK
# ============================================================

def on_message(
    client,
    userdata,
    msg
):

    try:

        # ----------------------------------------------------
        # DECODE MESSAGE
        # ----------------------------------------------------

        payload = msg.payload.decode()

        data = json.loads(
            payload
        )


        # ----------------------------------------------------
        # DISPLAY TELEMETRY
        # ----------------------------------------------------

        print("\n")
        print("-" * 60)
        print("Received telemetry")
        print("-" * 60)


        device_id = data.get(
            "device_id",
            "UNKNOWN"
        )

        print(
            "Device:",
            device_id
        )


        # ====================================================
        # CREATE AI FEATURES
        # ====================================================

        features = [

            data.get(
                "temperature",
                0
            ),

            data.get(
                "voltage",
                0
            ),

            data.get(
                "current",
                0
            ),

            data.get(
                "power",
                0
            ),

            data.get(
                "cpu_usage",
                0
            ),

            data.get(
                "memory_usage",
                0
            ),

            data.get(
                "network_traffic",
                0
            ),

            data.get(
                "packet_rate",
                0
            ),

            data.get(
                "latency",
                0
            )
        ]


        # ----------------------------------------------------
        # NUMPY ARRAY
        # ----------------------------------------------------

        X = np.array(
            features,
            dtype=float
        ).reshape(
            1,
            -1
        )


        # ====================================================
        # SCALE FEATURES
        # ====================================================

        if scaler is not None:

            X = scaler.transform(
                X
            )


        # ====================================================
        # AI PREDICTION
        # ====================================================

        prediction = model.predict(
            X
        )[0]


        # ----------------------------------------------------
        # ANOMALY SCORE
        # ----------------------------------------------------

        try:

            anomaly_score = (
                model.decision_function(X)[0]
            )

        except Exception:

            anomaly_score = float(
                prediction
            )


        # ----------------------------------------------------
        # AI STATUS
        # ----------------------------------------------------

        if int(prediction) == -1:

            ai_status = "ANOMALY"

        else:

            ai_status = "NORMAL"


        print(
            "AI Status:",
            ai_status
        )

        print(
            "Anomaly Score:",
            round(
                float(anomaly_score),
                4
            )
        )


        # ====================================================
        # SAVE TO DATABASE
        # ====================================================

        database_saved = save_to_database(
            data,
            ai_status,
            anomaly_score
        )


        # ====================================================
        # PUBLISH AI RESULT
        # ====================================================

        result = {

            "device_id": device_id,

            "timestamp": data.get(
                "timestamp",
                datetime.now().isoformat()
            ),

            "ai_anomaly_status": ai_status,

            "anomaly_score": float(
                anomaly_score
            ),

            "temperature": data.get(
                "temperature"
            ),

            "voltage": data.get(
                "voltage"
            ),

            "current": data.get(
                "current"
            ),

            "power": data.get(
                "power"
            ),

            "cpu_usage": data.get(
                "cpu_usage"
            ),

            "memory_usage": data.get(
                "memory_usage"
            ),

            "network_traffic": data.get(
                "network_traffic"
            ),

            "packet_rate": data.get(
                "packet_rate"
            ),

            "latency": data.get(
                "latency"
            ),

            "attack_status": (
                "DATABASE_SAVED"
                if database_saved
                else "DATABASE_ERROR"
            )
        }


        publish_result = client.publish(
            AI_TOPIC,
            json.dumps(result)
        )


        print(
            "AI result published to:",
            AI_TOPIC
        )

        print(
            "MQTT publish status:",
            publish_result.rc
        )


    except json.JSONDecodeError as e:

        print(
            "JSON ERROR:",
            e
        )


    except Exception as e:

        print(
            "Processing ERROR:",
            repr(e)
        )


# ============================================================
# CREATE MQTT CLIENT
# ============================================================

client = mqtt.Client()

client.username_pw_set(
    MQTT_USERNAME,
    MQTT_PASSWORD
)

client.tls_set()


# ============================================================
# REGISTER CALLBACKS
# ============================================================

client.on_connect = on_connect
client.on_message = on_message


# ============================================================
# CONNECT TO MQTT
# ============================================================

print("\nConnecting to MQTT broker...")


try:

    client.connect(
        MQTT_BROKER,
        MQTT_PORT,
        60
    )

except Exception as e:

    print(
        "MQTT connection ERROR:",
        e
    )

    raise SystemExit(1)


# ============================================================
# START DETECTOR
# ============================================================

print(
    "\nAI Detector started."
)

print(
    "Waiting for telemetry..."
)

print("=" * 60)


client.loop_forever()
import os
from dotenv import load_dotenv

load_dotenv()

# ==========================================
# MQTT CONFIGURATION
# ==========================================

MQTT_BROKER = os.getenv("MQTT_BROKER")
MQTT_PORT = int(os.getenv("MQTT_PORT", 8883))

MQTT_USERNAME = os.getenv("MQTT_USERNAME")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")

MQTT_TOPIC = "iot/devices/telemetry"

# Topic for AI predictions
AI_ANOMALY_TOPIC = "iot/devices/ai-anomaly"


# ==========================================
# POSTGRESQL CONFIGURATION
# ==========================================

POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", 5432))

POSTGRES_DB = os.getenv(
    "POSTGRES_DB",
    "iot_cybersecurity"
)

POSTGRES_USER = os.getenv(
    "POSTGRES_USER",
    "postgres"
)

POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
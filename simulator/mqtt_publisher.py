import json
import random
import time
import ssl
from datetime import datetime

import paho.mqtt.client as mqtt

from config import (
    MQTT_BROKER,
    MQTT_PORT,
    MQTT_USERNAME,
    MQTT_PASSWORD,
    MQTT_TOPIC
)


# =========================================================
# MODE
# =========================================================

# False = Normal IoT data
# True  = Simulated cyberattack data

ATTACK_MODE = False


# =========================================================
# GENERATE IoT DEVICE DATA
# =========================================================

def generate_device_data(device_id):

    # -----------------------------------------------------
    # NORMAL IoT TELEMETRY
    # -----------------------------------------------------

    temperature = round(
        random.uniform(30, 45), 2
    )

    voltage = round(
        random.uniform(220, 240), 2
    )

    current = round(
        random.uniform(1, 5), 2
    )

    power = round(
        voltage * current, 2
    )

    cpu_usage = round(
        random.uniform(20, 60), 2
    )

    memory_usage = round(
        random.uniform(30, 70), 2
    )

    network_traffic = round(
        random.uniform(50, 500), 2
    )

    packet_rate = round(
        random.uniform(20, 100), 2
    )

    latency = round(
        random.uniform(10, 50), 2
    )


    # =====================================================
    # OPTIONAL ATTACK MODE
    # =====================================================

    if ATTACK_MODE:

        network_traffic = round(
            random.uniform(1000, 2000), 2
        )

        packet_rate = round(
            random.uniform(200, 500), 2
        )

        latency = round(
            random.uniform(150, 500), 2
        )

        cpu_usage = round(
            random.uniform(85, 99), 2
        )

        memory_usage = round(
            random.uniform(85, 99), 2
        )


    # -----------------------------------------------------
    # TIMESTAMP
    # -----------------------------------------------------

    timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )


    # -----------------------------------------------------
    # CREATE TELEMETRY OBJECT
    # -----------------------------------------------------

    data = {
        "device_id": device_id,
        "timestamp": timestamp,
        "temperature": temperature,
        "voltage": voltage,
        "current": current,
        "power": power,
        "cpu_usage": cpu_usage,
        "memory_usage": memory_usage,
        "network_traffic": network_traffic,
        "packet_rate": packet_rate,
        "latency": latency
    }

    return data


# =========================================================
# MQTT CONNECT CALLBACK
# =========================================================

def on_connect(
    client,
    userdata,
    flags,
    reason_code,
    properties=None
):

    if reason_code == 0:

        print(
            "SUCCESS: Connected to HiveMQ Cloud"
        )

    else:

        print(
            f"Connection failed. Reason code: {reason_code}"
        )


# =========================================================
# CREATE MQTT CLIENT
# =========================================================

client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2,
    client_id="virtual-iot-publisher"
)


# =========================================================
# MQTT USERNAME & PASSWORD
# =========================================================

client.username_pw_set(
    MQTT_USERNAME,
    MQTT_PASSWORD
)


# =========================================================
# TLS / SSL
# =========================================================

client.tls_set(
    cert_reqs=ssl.CERT_REQUIRED
)


# =========================================================
# CALLBACK
# =========================================================

client.on_connect = on_connect


# =========================================================
# CONNECT TO HIVEMQ CLOUD
# =========================================================

print(
    "Connecting to HiveMQ Cloud..."
)

client.connect(
    MQTT_BROKER,
    MQTT_PORT,
    keepalive=60
)


# =========================================================
# START MQTT LOOP
# =========================================================

client.loop_start()


# =========================================================
# START PUBLISHING
# =========================================================

print(
    "\nStarting Virtual IoT Data Publisher..."
)


if ATTACK_MODE:

    print(
        "=========================================="
    )

    print(
        "        ATTACK MODE: ON"
    )

    print(
        "Simulated abnormal telemetry is active"
    )

    print(
        "=========================================="
    )

else:

    print(
        "=========================================="
    )

    print(
        "        NORMAL MODE: ON"
    )

    print(
        "Normal IoT telemetry is active"
    )

    print(
        "=========================================="
    )


print(
    "Press Ctrl + C to stop.\n"
)


# =========================================================
# MAIN PUBLISHING LOOP
# =========================================================

try:

    while True:

        # Three virtual IoT devices

        for device_id in [
            "SE-001",
            "SE-002",
            "SE-003"
        ]:

            # Generate data

            device_data = generate_device_data(
                device_id
            )


            # Convert dictionary to JSON

            payload = json.dumps(
                device_data
            )


            # Publish to MQTT

            result = client.publish(
                MQTT_TOPIC,
                payload,
                qos=1
            )


            # Check result

            if result.rc == mqtt.MQTT_ERR_SUCCESS:

                print(
                    f"Published [{device_id}]: "
                    f"{payload}"
                )

            else:

                print(
                    f"Failed to publish "
                    f"[{device_id}]"
                )


        # Publish every 1 second

        time.sleep(1)


# =========================================================
# STOP PROGRAM
# =========================================================

except KeyboardInterrupt:

    print(
        "\nStopping publisher..."
    )

    client.loop_stop()

    client.disconnect()

    print(
        "Disconnected from HiveMQ."
    )
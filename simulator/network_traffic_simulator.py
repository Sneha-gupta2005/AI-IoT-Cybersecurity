import random
import time
import json
import paho.mqtt.client as mqtt

from config import (
    MQTT_BROKER,
    MQTT_PORT,
    MQTT_USERNAME,
    MQTT_PASSWORD
)


MQTT_TOPIC = "iot/network/telemetry"

ATTACK_MODE = False


def generate_network_data():

    if ATTACK_MODE:

        src_port = random.randint(1024, 65535)
        dst_port = random.choice([80, 443, 22])

        duration = random.uniform(0.001, 2)

        src_bytes = random.randint(5000, 100000)
        dst_bytes = random.randint(100, 5000)

        src_pkts = random.randint(200, 1000)
        dst_pkts = random.randint(10, 100)

        conn_state = random.choice([
            "REJ",
            "S0",
            "RSTO",
            "RSTR"
        ])

    else:

        src_port = random.randint(1024, 65535)
        dst_port = random.choice([80, 443, 53, 22])

        duration = random.uniform(0.1, 10)

        src_bytes = random.randint(100, 5000)
        dst_bytes = random.randint(100, 10000)

        src_pkts = random.randint(5, 100)
        dst_pkts = random.randint(5, 100)

        conn_state = random.choice([
            "SF",
            "S1",
            "S2"
        ])


    return {

        "src_port": src_port,
        "dst_port": dst_port,

        "proto": random.choice([
            "tcp",
            "udp",
            "icmp"
        ]),

        "service": random.choice([
            "http",
            "https",
            "dns",
            "ssh"
        ]),

        "duration": duration,

        "src_bytes": src_bytes,
        "dst_bytes": dst_bytes,

        "conn_state": conn_state,

        "missed_bytes": random.randint(0, 100),

        "src_pkts": src_pkts,

        "src_ip_bytes": src_bytes + random.randint(20, 500),

        "dst_pkts": dst_pkts,

        "dst_ip_bytes": dst_bytes + random.randint(20, 500),

        "dns_qclass": random.choice([0, 1, 2]),

        "dns_qtype": random.choice([0, 1, 2, 28]),

        "dns_rcode": random.choice([0, 0, 0, 3]),

        "dns_AA": random.choice([True, False]),

        "dns_RD": random.choice([True, False]),

        "dns_RA": random.choice([True, False]),

        "dns_rejected": False,

        "ssl_version": random.choice([
            "TLSv12",
            "TLSv13",
            "unknown"
        ]),

        "ssl_cipher": random.choice([
            "TLS_AES_128_GCM_SHA256",
            "TLS_AES_256_GCM_SHA384",
            "unknown"
        ]),

        "ssl_resumed": random.choice([True, False]),

        "ssl_established": random.choice([True, False]),

        "http_trans_depth": random.randint(0, 3),

        "http_method": random.choice([
            "GET",
            "POST",
            "PUT"
        ]),

        "http_version": random.choice([
            "1.0",
            "1.1",
            "2"
        ]),

        "http_request_body_len": random.randint(0, 1000),

        "http_response_body_len": random.randint(0, 5000),

        "http_status_code": random.choice([
            200,
            200,
            200,
            404,
            500
        ])
    }


# ============================================================
# MQTT
# ============================================================

client = mqtt.Client()

client.username_pw_set(
    MQTT_USERNAME,
    MQTT_PASSWORD
)

client.tls_set()

client.connect(
    MQTT_BROKER,
    MQTT_PORT
)

print("Network simulator connected.")
print("Attack mode:", ATTACK_MODE)


while True:

    data = generate_network_data()

    data["timestamp"] = time.strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    payload = json.dumps(data)

    client.publish(
        MQTT_TOPIC,
        payload,
        qos=1
    )

    print(payload)

    time.sleep(2)
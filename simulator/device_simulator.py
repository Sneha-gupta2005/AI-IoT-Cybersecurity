import random
import time
import json
from datetime import datetime


def generate_device_data(device_id):

    temperature = round(random.uniform(30, 45), 2)

    voltage = round(random.uniform(220, 240), 2)

    current = round(random.uniform(1, 5), 2)

    # Power = Voltage × Current
    power = round(voltage * current, 2)

    cpu_usage = round(random.uniform(20, 60), 2)

    memory_usage = round(random.uniform(30, 70), 2)

    network_traffic = round(random.uniform(50, 500), 2)

    packet_rate = round(random.uniform(20, 100), 2)

    latency = round(random.uniform(10, 50), 2)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

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


while True:

    for device_id in ["SE-001", "SE-002", "SE-003"]:

        device_data = generate_device_data(device_id)

        print("\n--- IoT Device Telemetry ---")

        print(json.dumps(device_data, indent=2))

    time.sleep(1)
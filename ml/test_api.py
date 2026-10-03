import requests
import pandas as pd

DATASET = "datasets/processed/ton_iot_network_processed.csv"

df = pd.read_csv(DATASET)

# Take one known attack sample
sample = df[df["attack_type"] == "normal"].iloc[0]

features = df.drop(
    columns=["label", "attack_type"]
).columns

payload = {
    "features": {
        feature: float(sample[feature])
        for feature in features
    }
}

response = requests.post(
    "http://127.0.0.1:8000/predict",
    json=payload
)

print("HTTP STATUS:", response.status_code)

print("\nAPI RESPONSE:")
print(response.json())

print("\nACTUAL ATTACK TYPE:")
print(sample["attack_type"])
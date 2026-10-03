import pandas as pd
import os
DATASET_PATH = "datasets/raw/ton-IOT/train_test_network.csv"

print("=" * 60)
print("DATASET INSPECTION STARTED")
print("=" * 60)

print("\nCurrent working directory:")
print(os.getcwd())

print("\nChecking dataset path:")
print(DATASET_PATH)

if not os.path.exists(DATASET_PATH):
    print("\nERROR: Dataset file not found!")
    print("\nFiles available inside dataset/raw:")
    
    raw_path = "dataset/raw"
    
    if os.path.exists(raw_path):
        for root, dirs, files in os.walk(raw_path):
            for file in files:
                print(os.path.join(root, file))
    else:
        print("dataset/raw folder does not exist.")

    raise SystemExit

print("\nDataset found!")
print("Loading dataset...")

df = pd.read_csv(DATASET_PATH)

print("\n" + "=" * 60)
print("DATASET INFORMATION")
print("=" * 60)

print("\nShape:")
print(df.shape)

print("\nColumns:")
for i, column in enumerate(df.columns, start=1):
    print(f"{i}. {column}")

print("\nData Types:")
print(df.dtypes)

print("\nFirst 5 rows:")
print(df.head())

print("\nMissing values:")
print(df.isnull().sum())

print("\nDuplicate rows:")
print(df.duplicated().sum())

print("\nUnique values:")
for column in df.columns:
    unique_count = df[column].nunique()

    if unique_count <= 30:
        print(f"\n{column}")
        print("Unique values:", unique_count)
        print(df[column].value_counts().head(20))

print("\n" + "=" * 60)
print("DATASET INSPECTION COMPLETED")
print("=" * 60)
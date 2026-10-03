import pandas as pd
import os

# ============================================================
# PATHS
# ============================================================

INPUT_PATH = "datasets/raw/ton-IOT/train_test_network.csv"
OUTPUT_PATH = "datasets/processed/ton_iot_network_processed.csv"


# ============================================================
# START
# ============================================================

print("=" * 70)
print("TON-IOT NETWORK DATA PREPROCESSING")
print("=" * 70)


# ============================================================
# LOAD DATASET
# ============================================================

print("\nLoading dataset...")

df = pd.read_csv(INPUT_PATH)

print("Original shape:", df.shape)


# ============================================================
# REMOVE DUPLICATES
# ============================================================

before = len(df)

df = df.drop_duplicates()

after = len(df)

print("\nDuplicate rows removed:", before - after)
print("Shape after duplicate removal:", df.shape)


# ============================================================
# SAVE TARGETS
# ============================================================

y_binary = df["label"].copy()

y_attack_type = df["type"].copy()


# ============================================================
# REMOVE TARGET COLUMNS
# ============================================================

df = df.drop(
    columns=["label", "type"]
)


# ============================================================
# REMOVE IDENTIFIER / HIGH-CARDINALITY TEXT COLUMNS
# ============================================================

columns_to_remove = [
    "src_ip",
    "dst_ip",
    "dns_query",
    "ssl_subject",
    "ssl_issuer",
    "http_uri",
    "http_user_agent",
    "http_orig_mime_types",
    "http_resp_mime_types",
    "weird_name",
    "weird_addl",
    "weird_notice"
]

existing_columns_to_remove = [
    col
    for col in columns_to_remove
    if col in df.columns
]

df = df.drop(
    columns=existing_columns_to_remove
)

print("\nRemoved identifier/text-heavy columns:")
print(existing_columns_to_remove)


# ============================================================
# DETECT CATEGORICAL COLUMNS
# ============================================================

categorical_columns = df.select_dtypes(
    include=["object", "string", "category"]
).columns.tolist()

print("\nCategorical columns:")
print(categorical_columns)


# ============================================================
# HANDLE CATEGORICAL MISSING VALUES
# ============================================================

for column in categorical_columns:

    df[column] = df[column].fillna("unknown")


# ============================================================
# HANDLE NUMERIC COLUMNS
# ============================================================

numeric_columns = [
    column
    for column in df.columns
    if column not in categorical_columns
]

print("\nNumeric columns:")
print(numeric_columns)


for column in numeric_columns:

    df[column] = pd.to_numeric(
        df[column],
        errors="coerce"
    )

    median_value = df[column].median()

    df[column] = df[column].fillna(
        median_value
    )


# ============================================================
# ONE-HOT ENCODING
# ============================================================

print("\nApplying one-hot encoding...")

df = pd.get_dummies(
    df,
    columns=categorical_columns,
    drop_first=True
)


# ============================================================
# CONVERT BOOLEAN COLUMNS
# ============================================================

boolean_columns = df.select_dtypes(
    include=["bool"]
).columns

for column in boolean_columns:

    df[column] = df[column].astype(int)


# ============================================================
# FINAL NUMERIC SAFETY CHECK
# ============================================================

print("\nChecking final data types...")

df = df.apply(
    pd.to_numeric,
    errors="coerce"
)

df = df.fillna(0)


# ============================================================
# ADD TARGET COLUMNS BACK
# ============================================================

df["label"] = y_binary.values
df["attack_type"] = y_attack_type.values


# ============================================================
# CREATE OUTPUT DIRECTORY
# ============================================================

os.makedirs(
    os.path.dirname(OUTPUT_PATH),
    exist_ok=True
)


# ============================================================
# SAVE PROCESSED DATASET
# ============================================================

df.to_csv(
    OUTPUT_PATH,
    index=False
)


# ============================================================
# FINAL SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("PREPROCESSING COMPLETED SUCCESSFULLY")
print("=" * 70)

print("\nOriginal shape:")
print((before, 44))

print("\nProcessed shape:")
print(df.shape)

print("\nNumber of ML features:")
print(len(df.columns) - 2)

print("\nLabel distribution:")
print(df["label"].value_counts())

print("\nAttack type distribution:")
print(df["attack_type"].value_counts())

print("\nMissing values remaining:")
print(df.isnull().sum().sum())

print("\nOutput file:")
print(OUTPUT_PATH)

print("=" * 70)
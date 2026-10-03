from ui import apply_theme
apply_theme()

import streamlit as st
import pandas as pd
import os


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Dataset Explorer",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Dataset Explorer")

st.caption(
    "Explore the processed TON-IoT network cybersecurity dataset"
)

st.divider()


# =========================================================
# DATASET PATH
# =========================================================

DATASET_PATH = (
    "datasets/processed/ton_iot_network_processed.csv"
)


# =========================================================
# CHECK DATASET
# =========================================================

if not os.path.exists(DATASET_PATH):

    st.error(
        "Processed TON-IoT dataset was not found."
    )

    st.code(DATASET_PATH)

    st.stop()


# =========================================================
# LOAD DATA
# =========================================================

@st.cache_data
def load_dataset():

    df = pd.read_csv(DATASET_PATH)

    return df


try:

    df = load_dataset()

except Exception as e:

    st.error("Dataset loading failed.")

    st.code(str(e))

    st.stop()


# =========================================================
# DATASET INFORMATION
# =========================================================

st.subheader("📌 Dataset Information")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Records",
    f"{len(df):,}"
)

col2.metric(
    "Total Columns",
    df.shape[1]
)

col3.metric(
    "ML Features",
    df.shape[1] - 2
)

col4.metric(
    "Missing Values",
    int(df.isnull().sum().sum())
)

st.divider()


# =========================================================
# TARGET DISTRIBUTION
# =========================================================

st.subheader("🎯 Binary Attack Label")

if "label" in df.columns:

    label_counts = (
        df["label"]
        .value_counts()
        .sort_index()
        .reset_index()
    )

    label_counts.columns = [
        "label",
        "count"
    ]

    label_counts["label_name"] = (
        label_counts["label"]
        .map({
            0: "Normal",
            1: "Attack"
        })
    )

    col1, col2 = st.columns(2)

    with col1:

        st.dataframe(
            label_counts[
                [
                    "label_name",
                    "count"
                ]
            ],
            use_container_width=True,
            hide_index=True
        )

    with col2:

        import plotly.express as px

        fig_label = px.pie(
            label_counts,
            names="label_name",
            values="count",
            title="Normal vs Attack"
        )

        st.plotly_chart(
            fig_label,
            use_container_width=True
        )


# =========================================================
# ATTACK TYPE DISTRIBUTION
# =========================================================

st.divider()

st.subheader("🚨 Attack Type Distribution")

if "attack_type" in df.columns:

    attack_counts = (
        df["attack_type"]
        .value_counts()
        .reset_index()
    )

    attack_counts.columns = [
        "attack_type",
        "count"
    ]

    col1, col2 = st.columns([1, 2])

    with col1:

        st.dataframe(
            attack_counts,
            use_container_width=True,
            hide_index=True
        )

    with col2:

        fig_attack = px.bar(
            attack_counts,
            x="attack_type",
            y="count",
            text="count",
            title="TON-IoT Attack Classes"
        )

        fig_attack.update_layout(
            xaxis_title="Attack Type",
            yaxis_title="Records"
        )

        st.plotly_chart(
            fig_attack,
            use_container_width=True
        )


# =========================================================
# FEATURE INFORMATION
# =========================================================

st.divider()

st.subheader("🧩 Feature Information")

feature_columns = [
    column
    for column in df.columns
    if column not in [
        "label",
        "attack_type"
    ]
]

feature_info = pd.DataFrame(
    {
        "Feature": feature_columns,

        "Data Type": [
            str(df[column].dtype)
            for column in feature_columns
        ],

        "Missing Values": [
            int(df[column].isnull().sum())
            for column in feature_columns
        ],

        "Unique Values": [
            int(df[column].nunique())
            for column in feature_columns
        ]
    }
)

st.dataframe(
    feature_info,
    use_container_width=True,
    hide_index=True
)


# =========================================================
# FEATURE SEARCH
# =========================================================

st.subheader("🔎 Search Features")

search_text = st.text_input(
    "Search for a feature name",
    placeholder="Example: bytes, port, proto..."
)

if search_text:

    filtered_features = feature_info[
        feature_info["Feature"]
        .str.contains(
            search_text,
            case=False,
            na=False
        )
    ]

    st.dataframe(
        filtered_features,
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# DATA SAMPLE
# =========================================================

st.divider()

st.subheader("📄 Dataset Sample")

sample_size = st.slider(
    "Number of rows to display",
    min_value=5,
    max_value=100,
    value=20,
    step=5
)

st.dataframe(
    df.head(sample_size),
    use_container_width=True,
    hide_index=True
)


# =========================================================
# FILTER DATA
# =========================================================

st.divider()

st.subheader("🎛️ Dataset Filters")

col1, col2 = st.columns(2)

with col1:

    if "label" in df.columns:

        selected_label = st.selectbox(
            "Filter by Label",
            ["All", "Normal", "Attack"]
        )

    else:

        selected_label = "All"


with col2:

    if "attack_type" in df.columns:

        attack_options = [
            "All"
        ] + sorted(
            df["attack_type"]
            .dropna()
            .unique()
            .tolist()
        )

        selected_attack = st.selectbox(
            "Filter by Attack Type",
            attack_options
        )

    else:

        selected_attack = "All"


filtered_df = df.copy()


# Label filter

if selected_label == "Normal":

    filtered_df = filtered_df[
        filtered_df["label"] == 0
    ]

elif selected_label == "Attack":

    filtered_df = filtered_df[
        filtered_df["label"] == 1
    ]


# Attack type filter

if selected_attack != "All":

    filtered_df = filtered_df[
        filtered_df["attack_type"]
        == selected_attack
    ]


st.write(
    f"Filtered records: **{len(filtered_df):,}**"
)

st.dataframe(
    filtered_df.head(100),
    use_container_width=True,
    hide_index=True
)


# =========================================================
# DOWNLOAD FILTERED DATA
# =========================================================

st.divider()

csv_data = filtered_df.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    label="⬇️ Download Filtered Dataset",
    data=csv_data,
    file_name="ton_iot_filtered.csv",
    mime="text/csv"
)
import streamlit as st

def apply_theme():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background: linear-gradient(135deg, #07111f 0%, #0b1628 48%, #101827 100%);
    }

    [data-testid="stHeader"] {
        background: rgba(0,0,0,0);
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #081321 0%, #0d1b2f 100%);
        border-right: 1px solid rgba(255,255,255,.08);
    }

    [data-testid="stSidebar"] * {
        font-family: 'Inter', sans-serif;
    }

    [data-testid="stSidebarNav"] {
        padding-top: 1rem;
    }

    [data-testid="stMetric"] {
        background: linear-gradient(145deg, rgba(18,34,57,.95), rgba(12,25,43,.95));
        border: 1px solid rgba(255,255,255,.09);
        border-radius: 18px;
        padding: 18px 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,.20);
    }

    [data-testid="stMetricLabel"] {
        color: #9fb0c7;
        font-weight: 600;
    }

    [data-testid="stMetricValue"] {
        color: #f5f8fc;
        font-weight: 800;
    }

    div[data-testid="stPlotlyChart"], div[data-testid="stDataFrame"] {
        background: rgba(13,27,47,.72);
        border: 1px solid rgba(255,255,255,.07);
        border-radius: 18px;
        padding: 8px;
        box-shadow: 0 10px 30px rgba(0,0,0,.16);
    }

    .block-container {
        max-width: 1500px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    h1 {
        font-weight: 800 !important;
        letter-spacing: -0.03em;
    }

    h2, h3 {
        font-weight: 700 !important;
    }

    .hero-card {
        padding: 26px 30px;
        border-radius: 22px;
        margin-bottom: 24px;
        background: linear-gradient(135deg, rgba(22,52,82,.92), rgba(11,29,51,.92));
        border: 1px solid rgba(120,190,255,.16);
        box-shadow: 0 18px 45px rgba(0,0,0,.22);
    }

    .hero-title {
        font-size: 30px;
        font-weight: 800;
        margin: 0;
        color: #f5f8fc;
    }

    .hero-subtitle {
        margin: 8px 0 0;
        color: #a9bad0;
        font-size: 15px;
    }

    .live-pill {
        display: inline-block;
        margin-top: 15px;
        padding: 7px 12px;
        border-radius: 999px;
        background: rgba(30,190,120,.12);
        border: 1px solid rgba(30,190,120,.28);
        color: #7ce7b6;
        font-size: 13px;
        font-weight: 700;
    }

    .section-label {
        color: #8fa6c0;
        text-transform: uppercase;
        letter-spacing: .12em;
        font-size: 11px;
        font-weight: 800;
        margin: 22px 0 8px;
    }

    .stButton > button {
        border-radius: 12px;
        font-weight: 700;
        border: 1px solid rgba(255,255,255,.10);
        min-height: 42px;
    }

    .stSelectbox > div > div,
    .stTextInput > div > div,
    .stNumberInput > div > div {
        border-radius: 12px;
    }

    [data-testid="stAlert"] {
        border-radius: 14px;
    }
    </style>
    """, unsafe_allow_html=True)

def hero(title, subtitle, live=False):
    pill = '<div class="live-pill">● LIVE MONITORING</div>' if live else ''
    st.markdown(
        f'<div class="hero-card"><div class="hero-title">{title}</div>'
        f'<div class="hero-subtitle">{subtitle}</div>{pill}</div>',
        unsafe_allow_html=True
    )

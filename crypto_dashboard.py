import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Crypto Risk Dashboard", layout="wide")


# 🔄 Auto-refresh every 60 seconds
st_autorefresh(interval=60 * 1000, key="auto_refresh")

# --- Load and clean data ---
df = pd.read_csv("output/crypto_prices.csv")

df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
df['btc'] = pd.to_numeric(df['btc'], errors='coerce')
df['eth'] = pd.to_numeric(df['eth'], errors='coerce')
df = df.dropna(subset=['timestamp', 'btc', 'eth'])
df = df.sort_values('timestamp')

# --- Calculate % change ---
df['btc_pct_change'] = df['btc'].pct_change() * 100
df['eth_pct_change'] = df['eth'].pct_change() * 100

# --- Define risk thresholds ---
btc_threshold = 5  # ±5% for BTC
eth_threshold = 3  # ±3% for ETH

latest_time = df['timestamp'].iloc[-1].strftime('%Y-%m-%d %H:%M')
btc_change = df['btc_pct_change'].iloc[-1]
eth_change = df['eth_pct_change'].iloc[-1]

btc_risk = abs(btc_change) > btc_threshold
eth_risk = abs(eth_change) > eth_threshold

# --- Streamlit UI setup ---
st.title("🛡️ Crypto Risk Dashboard")

# --- Alert banner ---
if btc_risk or eth_risk:
    st.error(f"🚨 RISK ALERT @ {latest_time}")
    if btc_risk:
        st.markdown(f"- BTC moved **{btc_change:.2f}%** (Threshold: ±{btc_threshold}%)")
    if eth_risk:
        st.markdown(f"- ETH moved **{eth_change:.2f}%** (Threshold: ±{eth_threshold}%)")
else:
    st.success(f"No high-risk movements. Last check: {latest_time}")

# --- Color-coded summary cards ---
st.subheader("🔍 Latest Crypto % Movement")
col1, col2 = st.columns(2)

def display_card(col, label, change, threshold):
    if abs(change) > threshold:
        risk_label = "🔴 High Risk"
    elif abs(change) > threshold * 0.6:
        risk_label = "🟡 Medium Risk"
    else:
        risk_label = "🟢 Low Risk"
    col.metric(label=f"{label} ({risk_label})", value=f"{change:.2f}%", delta=f"{threshold}%")

display_card(col1, "Bitcoin", btc_change, btc_threshold)
display_card(col2, "Ethereum", eth_change, eth_threshold)

# --- Filter for high-risk periods ---
risk_df = df[
    (df['btc_pct_change'].abs() > btc_threshold) |
    (df['eth_pct_change'].abs() > eth_threshold)
]

# --- Trend charts ---
st.subheader("📈 Bitcoin & Ethereum Price Trends")

if not risk_df.empty:
    st.markdown("🔴 Showing only high-risk periods")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Bitcoin (BTC) – High-Risk Only**")
        st.line_chart(risk_df.set_index('timestamp')[['btc']])

    with col2:
        st.markdown("**Ethereum (ETH) – High-Risk Only**")
        st.line_chart(risk_df.set_index('timestamp')[['eth']])
else:
    st.markdown("🟢 No high-risk detected. Showing full price trends")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Bitcoin (BTC) – Full Data**")
        st.line_chart(df.set_index('timestamp')[['btc']])

    with col2:
        st.markdown("**Ethereum (ETH) – Full Data**")
        st.line_chart(df.set_index('timestamp')[['eth']])

# --- Historical High-Risk Events ---
st.subheader("📋 Historical High-Risk Events")
st.dataframe(risk_df[['timestamp', 'btc_pct_change', 'eth_pct_change']], use_container_width=True)

# Footer
st.caption("Powered by Airflow + Streamlit + CoinGecko")

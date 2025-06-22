import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh
import os 
import pytz

st.set_page_config(page_title="Crypto Risk Dashboard", layout="wide")

# 🔄 Auto-refresh every 60 seconds
st_autorefresh(interval=60 * 1000, key="auto_refresh")

# --- Load and clean data ---
if not os.path.exists("output/crypto_prices.csv"):
    st.warning("⚠️ No data available yet. Please add `output/crypto_prices.csv` to your repo.")
    st.stop()

df = pd.read_csv("output/crypto_prices.csv")

df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
eastern = pytz.timezone("US/Eastern")
df['timestamp'] = df['timestamp'].dt.tz_localize('UTC').dt.tz_convert(eastern)

df['btc'] = pd.to_numeric(df['btc'], errors='coerce')
df['eth'] = pd.to_numeric(df['eth'], errors='coerce')
df = df.dropna(subset=['timestamp', 'btc', 'eth'])
df = df.sort_values('timestamp')

# --- Calculate % change ---
df['btc_pct_change'] = df['btc'].pct_change() * 100
df['eth_pct_change'] = df['eth'].pct_change() * 100

# --- Define risk thresholds ---
st.sidebar.header("⚙️ Risk Settings")
btc_threshold = st.sidebar.slider("BTC Risk Threshold (%)", 1, 20, 5)
eth_threshold = st.sidebar.slider("ETH Risk Threshold (%)", 1, 20, 3)

min_date = df['timestamp'].min().date()
max_date = df['timestamp'].max().date()
start_date, end_date = st.sidebar.date_input(
    "Filter by date range", [min_date, max_date],
    min_value=min_date, max_value=max_date
)

# Filter data by selected date range
df = df[(df['timestamp'].dt.date >= start_date) & (df['timestamp'].dt.date <= end_date)]

if df.empty:
    st.warning("⚠️ No data available for the selected date range.")
    st.stop()

st.caption(f"📅 Showing data from **{start_date}** to **{end_date}**")

# --- Risk evaluation ---
btc_change = df['btc_pct_change'].iloc[-1]
eth_change = df['eth_pct_change'].iloc[-1]

btc_risk = abs(btc_change) > btc_threshold
eth_risk = abs(eth_change) > eth_threshold

# --- Streamlit UI setup ---
st.title("🛡️ Crypto Risk Dashboard")

# --- Live Snapshot with Timestamp ---
latest_row = df.iloc[-1]
btc_price = latest_row["btc"]
eth_price = latest_row["eth"]
latest_time = latest_row["timestamp"].strftime('%Y-%m-%d %I:%M %p %Z')

st.subheader("📊 Live Price Snapshot")
st.write(f"🕒 **Latest Data Timestamp:** `{latest_time}`")
st.write(f"🪙 **Bitcoin**: ${btc_price:,.2f}")
st.write(f"🪙 **Ethereum**: ${eth_price:,.2f}")

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

show_all = st.checkbox("🔍 Show full trend (instead of just high-risk)", value=risk_df.empty)

if not risk_df.empty and not show_all:
    st.markdown("🔴 Showing only high-risk periods")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Bitcoin (BTC) – High-Risk Only**")
        st.line_chart(risk_df.set_index('timestamp')[['btc']])
    with col2:
        st.markdown("**Ethereum (ETH) – High-Risk Only**")
        st.line_chart(risk_df.set_index('timestamp')[['eth']])
else:
    st.markdown("📊 Showing full price trends")

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

# --- Download & Raw Data ---
st.download_button(
    label="📥 Download Full Data as CSV",
    data=df.to_csv(index=False).encode('utf-8'),
    file_name='crypto_price_data.csv',
    mime='text/csv',
)

if st.checkbox("Show raw data"):
    st.subheader("📄 Raw Data Table")
    st.dataframe(df, use_container_width=True)

# Footer
st.caption("Powered by Airflow + Streamlit + CoinGecko")

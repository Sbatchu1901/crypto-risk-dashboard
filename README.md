# 🛡️ Crypto Risk Dashboard

A real-time dashboard to monitor **Bitcoin (BTC)** and **Ethereum (ETH)** price volatility using:

- 📊 Streamlit for interactive visualization
- 🔁 Airflow DAGs for automated data collection
- 🧠 Custom logic for risk thresholds and alerts

## 🚀 Live Demo

🔗 [Click here to try it out](https://crypto-risk-dashboard-ah8rpe28awhstjuw4zxnan.streamlit.app/) 
_(hosted on Streamlit Cloud, refreshes every 60s)_

## 📦 Features

- Auto-refreshing crypto price dashboard
- Risk alerts with color-coded thresholds:
  - 🔴 High Risk: >5% (BTC), >3% (ETH)
  - 🟡 Medium Risk
  - 🟢 Low Risk
- High-risk trend charts + historical logs
- Robust error handling for missing files

## 🛠️ Tech Stack

- **Streamlit** (UI)
- **Airflow** (ETL pipeline)
- **Python + Pandas**
- **CoinGecko API**
- **GitHub + Streamlit Cloud** (deployment)

## 🧠 Coming Soon

- Slack/email alerts
- SQLite backend
- ML-based forecasting

## 📂 Repo Structure
crypto-risk-dashboard/
├── crypto_dashboard.py
├── dags/crypto_price_dag.py
├── requirements.txt
├── output/crypto_prices.csv
└── README.md

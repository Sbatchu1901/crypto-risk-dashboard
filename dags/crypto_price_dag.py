from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import requests
import pandas as pd
import os
import json
import logging

# 1. Extract prices and save to JSON
def extract_prices():
    url = 'https://api.coingecko.com/api/v3/simple/price'
    params = {
        'ids': 'bitcoin,ethereum',
        'vs_currencies': 'usd'
    }
    response = requests.get(url, params=params)
    data = response.json()
    if 'bitcoin' in data and 'ethereum' in data:
        with open('/opt/airflow/crypto_prices.json', 'w') as f:
            json.dump(data, f)
        logging.info("Data extracted and saved to JSON: %s", data)
    else:
        raise ValueError("Received invalid or empty data from API")

# 2. Save data to CSV with timestamp
def save_to_csv(**kwargs):
    execution_time = kwargs['ts']  # Get execution timestamp

    with open('/opt/airflow/crypto_prices.json', 'r') as f:
        data = json.load(f)

    df = pd.DataFrame({
        'btc': [data['bitcoin']['usd']],
        'eth': [data['ethereum']['usd']],
        'timestamp': [execution_time]
    })

    output_path = '/opt/airflow/output/crypto_prices.csv'
    df.to_csv(output_path, mode='a', header=not os.path.exists(output_path), index=False)

    logging.info("Data written to CSV:\n%s", df)


# DAG configuration
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='crypto_price_dag',
    default_args=default_args,
    schedule_interval='*/5 * * * *',  # Every 5 minutes
    catchup=False,
    max_active_runs=1,
    tags=['crypto', 'price']
) as dag:

    # Task 1: Extract data from API
    task_extract = PythonOperator(
        task_id='extract_prices',
        python_callable=extract_prices
    )

    # Task 2: Save extracted data to CSV
    task_save = PythonOperator(
        task_id='save_to_csv',
        python_callable=save_to_csv,
        provide_context=True  # ✅ Required to access context like 'ts'
    )

    # Set task order
    task_extract >> task_save

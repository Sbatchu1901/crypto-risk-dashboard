from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import requests
import pandas as pd
import os 

# 1. Extract prices
def extract_prices():
    url = 'https://api.coingecko.com/api/v3/simple/price'
    params = {
        'ids': 'bitcoin,ethereum',
        'vs_currencies': 'usd'
    }
    response = requests.get(url, params=params)
    data = response.json()
    # Save to file temporarily so the next task can use it
    with open('/opt/airflow/crypto_prices.json', 'w') as f:
        f.write(str(data))

# 2. Save to CSV
def save_to_csv():
    import json
    with open('/opt/airflow/crypto_prices.json', 'r') as f:
        raw = f.read()
        data = json.loads(raw.replace("'", '"'))  # safely parse to dict

    # Extract prices into structured DataFrame
    df = pd.DataFrame({
        'btc': [data['bitcoin']['usd']],
        'eth': [data['ethereum']['usd']],
        'timestamp': [datetime.now().isoformat()]
    })

    df.to_csv('/opt/airflow/output/crypto_prices.csv', mode='a', header=not os.path.exists('/opt/airflow/output/crypto_prices.csv'), index=False)



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
    max_active_runs=1
) as dag:

    task_extract = PythonOperator(
        task_id='extract_prices',
        python_callable=extract_prices
    )

    task_save = PythonOperator(
        task_id='save_to_csv',
        python_callable=save_to_csv
    )

    task_extract >> task_save

    

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import os
import subprocess

BASE_PATH = os.path.expanduser("~/airflow/project/src")

def run_script(script_name):
    subprocess.run(["python3", os.path.join(BASE_PATH, script_name)], check=True)

with DAG(
    dag_id="chocolife_etl",
    start_date=datetime(2025, 1, 1),
    schedule_interval="@daily",
    catchup=False,
    tags=["chocolife", "etl"],
) as dag:

    scrape = PythonOperator(
        task_id="scrape",
        python_callable=lambda: run_script("scraper.py"),
    )

    clean = PythonOperator(
        task_id="clean",
        python_callable=lambda: run_script("clean.py"),
    )

    analyze = PythonOperator(
        task_id="analyze",
        python_callable=lambda: run_script("analyze.py"),
    )

    final_csv = PythonOperator(
        task_id="final_csv",
        python_callable=lambda: run_script("final_csv.py"),
    )

    save_sqlite = PythonOperator(
        task_id="save_sqlite",
        python_callable=lambda: run_script("save_sqlite.py"),
    )

    scrape >> clean >> analyze >> final_csv >> save_sqlite

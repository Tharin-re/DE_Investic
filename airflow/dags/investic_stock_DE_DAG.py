from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta

# Define default arguments
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Create the DAG object
with DAG(
    'investic_stock_DE',  # DAG ID
    default_args=default_args,
    description='DAG to run investic_stock_DE.py hourly',
    schedule_interval='@hourly',  # Runs every hour
    start_date=datetime(2025, 4, 5),
    catchup=False,
    is_paused_upon_creation=True  # Starts paused
) as dag:

    # Define the Python function to execute
    def run_investic_stock():
        import subprocess
        subprocess.run(['python', '../../investic_stock_DE.py'])

    # Create a PythonOperator task
    run_task = PythonOperator(
        task_id='run_investic_stock_DE',
        python_callable=run_investic_stock
    )

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from datetime import datetime
import psycopg2


# -----------------------------
# Data Quality Check Function
# -----------------------------
def check_postgres_data():
    conn = psycopg2.connect(
        host="postgres",
        database="airflow",
        user="airflow",
        password="airflow"
    )


    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM daily_metrics;")
    count = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    if count == 0:
        raise ValueError("❌ Data quality check failed: No records in daily_metrics")

    print(f"✅ Data quality passed: {count} rows found.")


# -----------------------------
# DAG Definition
# -----------------------------
default_args = {
    "start_date": datetime(2024, 1, 1),
}

with DAG(
    dag_id="batch_etl_pipeline",
    default_args=default_args,
    schedule_interval="@daily",
    catchup=False,
) as dag:

    # -----------------------------------
    # Step 1: Spark ETL (Bronze → Silver → Gold)
    # -----------------------------------
    run_spark_etl = BashOperator(
        task_id="run_spark_etl",
        bash_command="""
        spark-submit \
        --master spark://spark:7077 \
        --packages org.apache.hadoop:hadoop-aws:3.3.4 \
        --conf spark.hadoop.fs.s3a.endpoint=http://minio:9000 \
        --conf spark.hadoop.fs.s3a.access.key=minioadmin \
        --conf spark.hadoop.fs.s3a.secret.key=minioadmin \
        --conf spark.hadoop.fs.s3a.path.style.access=true \
        /opt/airflow/spark/etl_job.py
        """
    )

    # -----------------------------------
    # Step 2: Load Gold → Postgres
    # -----------------------------------
    load_gold_to_postgres = BashOperator(
        task_id="load_gold_to_postgres",
        bash_command="python /opt/airflow/scripts/load_gold.py"
    )

    # -----------------------------------
    # Step 3: Data Quality Check
    # -----------------------------------
    data_quality_check = PythonOperator(
        task_id="data_quality_check",
        python_callable=check_postgres_data
    )

    run_spark_etl >> load_gold_to_postgres >> data_quality_check

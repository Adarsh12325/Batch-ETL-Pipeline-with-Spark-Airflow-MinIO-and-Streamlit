# Batch ETL Pipeline with Spark, Airflow, MinIO and Streamlit
## Overview

This repository implements a Medallion Architecture-based ETL pipeline for ecommerce analytics. It extracts raw event data, processes it into Bronze → Silver → Gold layers using Spark, stores the Gold layer in PostgreSQL, and visualizes analytics in Streamlit.

The pipeline also uses Airflow for orchestration and MinIO for S3-compatible storage.

## Architecture Diagram
```
                     ┌───────────────┐
                     │  Event Source │
                     │ (CSV / Logs)  │
                     └───────┬───────┘
                             │
                             ▼
                     ┌───────────────┐
                     │   MinIO S3    │
                     │  Bronze Layer │
                     │ bronze/events │
                     └───────┬───────┘
                             │
                             ▼
                     ┌───────────────┐
                     │ Apache Spark  │
                     │ Silver Layer  │
                     │   Cleans &    │
                     │ Transforms    │
                     │ Adds Partitions│
                     │ silver/events │
                     └───────┬───────┘
                             │
                             ▼
                     ┌───────────────┐
                     │ Apache Spark  │
                     │  Gold Layer   │
                     │ Aggregations  │
                     │ gold/aggregations │
                     └───────┬───────┘
                             │
          ┌──────────────────┴──────────────────┐
          │                                     │
          ▼                                     ▼
  ┌───────────────┐                     ┌───────────────┐
  │ PostgreSQL DB │                     │ Airflow DAG   │
  │ daily_metrics │                     │ Orchestrator │
  └───────────────┘                     └───────────────┘
          │                                     │
          ▼                                     │
  ┌───────────────┐                             │
  │ Streamlit     │ <───────────────────────────┘
  │ Dashboard     │
  │ Visualization │
  └───────────────┘
```

### Explanation of Data Flow:

#### Bronze Layer (Raw Data)

- CSV event logs are ingested from the source into MinIO’s bronze/events/ bucket.

#### Silver Layer (Clean & Transform)

- Spark reads Bronze data.

- Cleans and transforms the dataset.

- Adds partition columns (year, month, day).

- Writes Parquet files into silver/events/ bucket.

#### Gold Layer (Aggregated Metrics)

- Spark aggregates Silver data (daily metrics, event counts).

- Writes aggregated Parquet files to gold/daily_metrics/.

- PostgreSQL (Analytics Database)

- Airflow DAG reads Gold Parquet data from MinIO.

- Loads data into PostgreSQL (daily_metrics table) for reporting.

#### Streamlit Dashboard

- Connects to PostgreSQL to visualize metrics:
```
      Daily events trend

      Daily active users

      Other KPIs
```

### Technologies Used 
```
Docker Compose – Container orchestration

Apache Spark 3.5 – ETL processing

Airflow – DAG orchestration

PostgreSQL 15 – Analytics database

MinIO – S3-compatible object storage

Streamlit – Interactive dashboard

Python & Pandas – Data handling
```
### Setup Instructions
1. Clone the Repository
```
git clone https://github.com/Adarsh12325/Batch-ETL-Pipeline-with-Spark-Airflow-MinIO-and-Streamlit
cd Batch-ETL-Pipeline-with-Spark-Airflow-MinIO-and-Streamlit
```

2. Build and Start Services Using Docker Compose
```
docker-compose up --build -d
```

- This will start the following containers:
```
Service         	Port(s)	             Purpose
------------------------------------------------------------------
postgres	        5432	               Analytics database
spark	            7077 / 8080	          Spark master for ETL
spark-worker	    N/A	                  Spark worker
airflow	            8081	               DAG orchestration
streamlit	        8501	               Dashboard
minio	            9000 / 9001           S3-compatible storage
```

Note: MinIO console is at http://localhost:9001. Default credentials are:
```
Username: minioadmin

Password: minioadmin
```

3. Airflow Setup
```
Initialize Airflow DB and create Admin user

docker-compose run airflow airflow db init
docker-compose run airflow airflow users create \
    --username admin \
    --password admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com
```
```
Access Airflow UI
Open: http://localhost:8081
```

4. Trigger the DAG
```
Go to DAGs → batch_etl_pipeline → Trigger DAG.

Monitor the DAG run and verify all tasks succeed.
```

5. Verify Data in MinIO
```
Open MinIO Console: http://localhost:9001

Buckets to check:

bronze/events/

silver/events/

gold/daily_metrics/
```

6. Verify Data in PostgreSQL

Connect to Postgres container:
```
docker exec -it postgres psql -U airflow -d airflow
```

Check daily_metrics table:
```
SELECT * FROM daily_metrics LIMIT 5;
```

You should see data like:
```
event_date	 daily_active_users	  total_events
2026-02-13	 10000	               763823
2026-02-12	 10000	               236177
```
7. Access Streamlit Dashboard
```
Open Streamlit app: http://localhost:8501
```
The dashboard will display:
```
Total events

Average daily active users

Trend charts for events and active users

```

8. Stopping the Pipeline
```
docker-compose down
```

<!-- This stops all containers while preserving volumes (postgres_data and minio_data) for persistent storage. -->

#### Notes / Troubleshooting

- Database Connection Issues:
Make sure the POSTGRES_DB, POSTGRES_USER, and POSTGRES_PASSWORD in docker-compose.yml match your Streamlit environment variables.

- Missing Tables in Postgres:
Check the DAG load_gold_to_postgres ran successfully and Gold data was written to Postgres.

- Spark-submit Errors:
Ensure you use the correct path inside the container, e.g., /opt/spark-apps/etl_job.py.

- Streamlit KeyError (e.g., total_revenue):
Verify the column exists in Postgres. Otherwise, modify app.py to use available columns.

### Folder Structure
```
Batch-ETL-Pipeline-with-Spark-Airflow-MinIO-and-Streamlit/
├─ dags/               # Airflow DAG scripts
├─ scripts/            # ETL Python scripts (load_gold.py, etc.)
├─ spark/              # Spark jobs & configs
├─ streamlit/          # Streamlit dashboard code (app.py)
├─ docker-compose.yml
├─ Dockerfile          # Dockerfile
├─ README.md
└─ Demo_Video/         # pipeline demo
```

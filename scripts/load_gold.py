from pyspark.sql import SparkSession
import psycopg2

# ==============================
# Spark Session WITH S3 Support
# ==============================

spark = SparkSession.builder \
    .appName("Load Gold To Postgres") \
    .config("spark.jars.packages", "org.apache.hadoop:hadoop-aws:3.3.4") \
    .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000") \
    .config("spark.hadoop.fs.s3a.access.key", "minioadmin") \
    .config("spark.hadoop.fs.s3a.secret.key", "minioadmin") \
    .config("spark.hadoop.fs.s3a.path.style.access", "true") \
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
    .getOrCreate()

GOLD_PATH = "s3a://gold/daily_metrics/"

print("Reading Gold Layer from MinIO...")

df = spark.read.parquet(GOLD_PATH)

pdf = df.toPandas()

spark.stop()

print("Connecting to Postgres...")

conn = psycopg2.connect(
    host="postgres",
    database="airflow",
    user="airflow",
    password="airflow"
)

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS daily_metrics (
    event_date DATE,
    daily_active_users BIGINT,
    total_events BIGINT
)
""")

cursor.execute("TRUNCATE TABLE daily_metrics")

for _, row in pdf.iterrows():
    cursor.execute(
        "INSERT INTO daily_metrics VALUES (%s, %s, %s)",
        (row["event_date"], row["daily_active_users"], row["total_events"])
    )

conn.commit()
cursor.close()
conn.close()

print("Gold data successfully loaded into Postgres.")

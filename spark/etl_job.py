from pyspark.sql import SparkSession
from pyspark.sql.functions import col, year, month, dayofmonth, to_date, countDistinct, count

spark = SparkSession.builder \
    .appName("Medallion ETL") \
    .getOrCreate()

# -----------------------
# Bronze Layer
# -----------------------
bronze_df = spark.read.csv(
    "s3a://bronze/events/events.csv",
    header=True,
    inferSchema=True
)

# -----------------------
# Silver Layer
# -----------------------
silver_df = bronze_df \
    .withColumn("event_time", col("event_time").cast("timestamp")) \
    .filter(col("user_id").isNotNull())

silver_df = silver_df \
    .withColumn("year", year("event_time")) \
    .withColumn("month", month("event_time")) \
    .withColumn("day", dayofmonth("event_time"))

silver_df.write \
    .mode("overwrite") \
    .partitionBy("year", "month", "day") \
    .parquet("s3a://silver/events/")

# -----------------------
# Gold Layer (Daily Metrics)
# -----------------------

gold_df = silver_df \
    .withColumn("event_date", to_date("event_time")) \
    .groupBy("event_date") \
    .agg(
        countDistinct("user_id").alias("daily_active_users"),
        count("*").alias("total_events")
    )

gold_df.write \
    .mode("overwrite") \
    .parquet("s3a://gold/daily_metrics/")

spark.stop()

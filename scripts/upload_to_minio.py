from minio import Minio
from minio.error import S3Error

client = Minio(
    "minio:9000",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False
)

bucket_name = "bronze"

if not client.bucket_exists(bucket_name):
    client.make_bucket(bucket_name)

client.fput_object(
    bucket_name,
    "events/events.csv",
    "events.csv"
)

print("Uploaded to Bronze layer.")

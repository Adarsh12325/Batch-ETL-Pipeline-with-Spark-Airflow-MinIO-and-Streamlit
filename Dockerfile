FROM apache/airflow:2.8.1

USER root

# Install system dependencies
RUN apt-get update && \
    apt-get install -y openjdk-17-jdk curl wget && \
    apt-get clean

# -----------------------------
# Install Spark
# -----------------------------
ENV SPARK_VERSION=3.5.0
ENV HADOOP_VERSION=3

RUN curl -L https://archive.apache.org/dist/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz \
    | tar -xz -C /opt/ && \
    ln -s /opt/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION} /opt/spark

ENV PATH="/opt/spark/bin:${PATH}"

# -----------------------------
# Install MinIO Client (mc)
# -----------------------------
RUN curl https://dl.min.io/client/mc/release/linux-amd64/mc \
    --output /usr/bin/mc && \
    chmod +x /usr/bin/mc

USER airflow

# -----------------------------
# Install Python dependencies
# -----------------------------
RUN pip install --no-cache-dir \
    pyspark \
    minio \
    boto3 \
    psycopg2-binary \
    pandas

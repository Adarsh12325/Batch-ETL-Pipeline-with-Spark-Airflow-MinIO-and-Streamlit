FROM python:3.10

WORKDIR /app

# Copy requirements first (better Docker caching)
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY app.py .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501"]

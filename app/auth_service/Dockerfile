FROM python:3.12-slim
WORKDIR /app

RUN apt-get update && apt-get install -y \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

COPY app/auth_service /app/app/auth_service
COPY app/auth_util /app/app/auth_util
COPY app/db_util /app/app/db_util
COPY main.py /app

RUN pip install --no-cache-dir -r /app/app/auth_service/requirements.txt

CMD ["python3", "main.py", "--service", "auth", "--port", "8000"]




# -----------------------------
# Stage 1: Build stage
# -----------------------------
FROM python:3.12-slim AS builder

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for cache
COPY auth_service/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy auth_service code and shared utils
COPY auth_service ./auth_service
COPY ../util ./util  # adjust if Docker build context is root folder

# -----------------------------
# Stage 2: Final runtime image
# -----------------------------
FROM python:3.12-slim AS runtime

WORKDIR /app

# Copy dependencies
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages

# Copy code
COPY --from=builder /app /app

# Expose port
EXPOSE 8000

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    UVICORN_WORKERS=4

# Start the auth_service FastAPI app
CMD ["uvicorn", "auth_service.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4", "--loop", "asyncio"]

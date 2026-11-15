# Ironory — Backend & ML Inference Dockerfile
# Base Python 3.11 slim runtime
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

# Install system dependencies (including graphics libraries required by OpenCV headless)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libgl1 \
    libglib2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python backend and deep learning dependencies
COPY backend/requirements.txt /app/backend_requirements.txt
COPY ml/requirements.txt /app/ml_requirements.txt

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /app/backend_requirements.txt && \
    pip install --no-cache-dir -r /app/ml_requirements.txt

# Copy application, ML engine, and database migration scripts
COPY backend/ /app/backend/
COPY ml/ /app/ml/
COPY pytest.ini /app/pytest.ini

# Expose backend port
EXPOSE 8000

# Health check using FastAPI health endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Start Uvicorn server
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Use official lightweight Python image
FROM python:3.11-slim

# Set environment variables to optimize Python runtime in containers
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HF_HOME=/app/cache/huggingface

# Set working directory inside container
WORKDIR /app

# Install system dependencies needed for compiling C-extensions or handling network requests
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy and install python dependencies first to take advantage of Docker layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create directories for persistent storage and models
RUN mkdir -p /app/data /app/chroma_db /app/cache/huggingface

# Copy application code into container
COPY . .

# Expose FastAPI default port
EXPOSE 8000

# Health check to ensure the container is healthy
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Start Uvicorn production server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
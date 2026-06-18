# Multi-stage build for FastAPI Checkout Service
FROM python:3.11-slim AS builder
RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt && pip install --no-cache-dir --upgrade pip wheel setuptools

# Production stage
FROM python:3.11-slim
RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

WORKDIR /app

# Install gunicorn for production
RUN pip install --no-cache-dir gunicorn

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY src/ ./src/
COPY requirements.txt .

# Create non-root user
RUN useradd -m -u 1000 fastapi
RUN chown -R fastapi:fastapi /app
USER fastapi

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Run with gunicorn
CMD ["gunicorn", "src.main:app", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000", "-w", "4"]

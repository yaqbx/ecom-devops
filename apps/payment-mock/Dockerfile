FROM python:3.11-slim
RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

WORKDIR /app

RUN pip install --no-cache-dir fastapi uvicorn[standard] pydantic gunicorn

RUN pip install --no-cache-dir gunicorn

COPY src/ ./src/

RUN useradd -m -u 1000 fastapi
RUN chown -R fastapi:fastapi /app
USER fastapi

EXPOSE 8100

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8100/health')" || exit 1

CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8100"]

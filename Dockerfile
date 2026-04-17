FROM python:3.11-slim

WORKDIR /app

# System deps for pymupdf and postgres
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libffi-dev libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

# Create data directories
RUN mkdir -p /app/data/uploads /app/data/resumes /app/data/exports /app/data/db

ENV PYTHONUNBUFFERED=1
ENV DATA_DIR=/app/data
ENV DB_PATH=/app/data/db/copilot.db

# Render provides the PORT environment variable
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --timeout-keep-alive 120"]

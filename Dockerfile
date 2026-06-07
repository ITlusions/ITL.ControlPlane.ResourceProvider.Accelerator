FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY pyproject.toml .

# Install Python dependencies
RUN pip install --no-cache-dir -e ".[postgres,redis,monitoring]"

# Copy source code
COPY src/ src/
COPY alembic/ alembic/
COPY alembic.ini .

# Expose port
EXPOSE 8003

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8003/health')" || exit 1

# Run provider
CMD ["uvicorn", "src.itl_accelerator_provider.main:app", "--host", "0.0.0.0", "--port", "8003"]

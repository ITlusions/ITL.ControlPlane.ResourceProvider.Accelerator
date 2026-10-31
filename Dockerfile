# syntax=docker/dockerfile:1
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
COPY src/ src/

# docker build --secret id=forgejo_token,env=FORGEJO_PACKAGE_TOKEN .
RUN --mount=type=secret,id=forgejo_token \
    pip install --no-cache-dir \
      --index-url "https://itladmin:$(cat /run/secrets/forgejo_token)@git.itlusions.com/api/packages/ITlusions/pypi/simple/" \
      --extra-index-url https://pypi.org/simple/ \
      -e ".[postgres,redis,monitoring]"

COPY alembic/ alembic/
COPY alembic.ini .

# Expose port
EXPOSE 8003

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8003/health')" || exit 1

# Run provider
CMD ["uvicorn", "src.itl_accelerator_provider.main:app", "--host", "0.0.0.0", "--port", "8003"]

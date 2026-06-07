# Quick Start Checklist

Complete these steps to finalize the SDK migration:

##  1. Update Dependencies

Edit `pyproject.toml`:

```toml
dependencies = [
    "fastapi>=0.104",
    "uvicorn[standard]>=0.24",
    "sqlalchemy[asyncio]>=2.0",
    "pydantic>=2.0",
    "pydantic-settings>=2.0",
    "asyncpg>=0.29",
    "alembic>=1.13",
    "httpx>=0.25",
    "structlog>=24.1",
    "python-dotenv>=1.0",
    "itl-controlplane-sdk>=1.0.0",  # ADD THIS LINE
]
```

##  2. Update Package Init

Edit `src/itl_accelerator_provider/__init__.py`:

```python
"""
ITL Accelerator Provider
"""
from .accelerator import AcceleratorProvider

__version__ = "0.1.0"
__all__ = ["AcceleratorProvider", "__version__"]
```

##  3. Replace Main Entry Point

```bash
cd src/itl_accelerator_provider
mv main.py main_old.py
mv main_new.py main.py
```

Or manually update `main.py` to:

```python
"""
Accelerator Provider Entry Point
"""
import os
import logging
from .initialization import AcceleratorProviderServer

logger = logging.getLogger(__name__)

def main():
    logging.basicConfig(level=logging.INFO)
    host = os.getenv("PROVIDER_HOST", "0.0.0.0")
    port = int(os.getenv("PROVIDER_PORT", "8003"))
    
    server = AcceleratorProviderServer()
    server.run(host=host, port=port, log_level="info")

if __name__ == "__main__":
    main()
```

##  4. Remove Old Provider File

```bash
rm src/itl_accelerator_provider/provider.py
```

(Replaced by `accelerator.py`)

##  5. Install and Run

```bash
# Install dependencies
pip install -e ".[dev]"

# Verify SDK is installed
pip list | grep itl-controlplane-sdk

# Start infrastructure
docker compose up -d

# Run provider
python -m itl_accelerator_provider.main
```

##  6. Test Endpoints

```bash
# Root
curl http://localhost:8003/

# Health
curl http://localhost:8003/health

# Docs
curl http://localhost:8003/docs

# List nodes
curl http://localhost:8003/subscriptions/sub-123/resourceGroups/rg-test/providers/ITL.Accelerator/sparkNodes
```

##  7. Update Dockerfile (Optional)

If using Docker, update `Dockerfile`:

```dockerfile
# Old
CMD ["uvicorn", "itl_accelerator_provider.main:app", "--host", "0.0.0.0", "--port", "8003"]

# New
CMD ["python", "-m", "itl_accelerator_provider.main"]
```

## Expected Output

When you run the provider, you should see:

```
================================================================================
ITL Accelerator Provider Configuration
================================================================================
Mode: API
Host: 0.0.0.0:8003
Provider: ITL.Accelerator v2024-01-01
Resource Types: sparkNodes, sparkOllamaInstances, sparkJobs
================================================================================
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
================================================================================
Accelerator Provider Startup
================================================================================
 Storage engine initialized
 Database schema ready
 Provider ITL.Accelerator ready
 Resource types: sparkNodes, sparkOllamaInstances, sparkJobs
================================================================================
Accelerator Provider is READY
================================================================================
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8003 (Press CTRL+C to quit)
```

## Troubleshooting

### SDK Not Found
```bash
pip install itl-controlplane-sdk
# Or check your private package index
```

### Import Errors
- Verify `__init__.py` exports `AcceleratorProvider`
- Check `from .accelerator import AcceleratorProvider`
- Ensure old `provider.py` is removed

### Route Errors
- All routes should use setup functions
- Check `routes/__init__.py` exports
- Verify app_factory.py includes routers

## Next Steps

After the provider runs successfully:

1. **Implement Repositories** (`repositories/spark_node_repo.py`)
2. **Implement Services** (`services/spark_node_service.py`)
3. **Connect Routes to Services** (replace TODO comments)
4. **Add RBAC** (use `@rbac_protected` decorator)
5. **Add Audit Logging** (use `@audit_event` decorator)
6. **Create Migrations** (Alembic for database schema)
7. **Write Tests** (unit and integration)

## Documentation

- **Full Migration Guide**: `docs/SDK_MIGRATION_GUIDE.md`
- **Architecture Details**: `docs/ARCHITECTURE.md`
- **Implementation Summary**: `IMPLEMENTATION_SUMMARY.md`

## Status

-  Initialization package created
-  Provider class implemented
-  Routes converted to setup functions
-  Models updated with SDK base
-  Awaiting: Dependencies update, file replacements, testing

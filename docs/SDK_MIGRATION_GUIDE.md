# SDK Migration Guide

## Overview

The Accelerator Resource Provider has been refactored to follow the **Core provider pattern** with full `itl-controlplane-sdk` integration. This guide documents the changes and provides instructions for completing the migration.

## Architecture Changes

### Before: Standalone FastAPI Application

```
src/itl_accelerator_provider/
 __init__.py (exports app)
 main.py (creates FastAPI app directly)
 config.py
 provider.py (simple base class)
 routes/
    spark_nodes.py (router = APIRouter())
    spark_instances.py (router = APIRouter())
    spark_jobs.py (router = APIRouter())
 models/
     spark_node.py (standalone Pydantic models)
```

### After: SDK-Integrated Provider

```
src/itl_accelerator_provider/
 __init__.py (exports AcceleratorProvider)
 main.py (uses AcceleratorProviderServer)
 accelerator.py (extends ResourceProvider from SDK)
 config.py
 initialization/
    __init__.py (exports AcceleratorProviderServer)
    server.py (AcceleratorProviderServer extends BaseProviderServer)
    app_factory.py (create_app function)
    lifecycle.py (app_lifespan context manager)
 routes/
    spark_nodes.py (setup_spark_nodes_routes function)
    spark_instances.py (setup_spark_instances_routes function)
    spark_jobs.py (setup_spark_jobs_routes function)
 models/
     spark_node.py (extends GenericResourceBase from SDK)
```

## Completed Changes

###  1. Provider Class (`accelerator.py`)

**Old** (`provider.py`):
```python
class ResourceProvider(ABC):
    @abstractmethod
    def name(self) -> str:
        pass
```

**New** (`accelerator.py`):
```python
from itl_controlplane_sdk.providers import ResourceProvider

class AcceleratorProvider(ResourceProvider):
    def __init__(self, engine: StorageEngine):
        self.engine = engine
    
    @property
    def namespace(self) -> str:
        return "ITL.Accelerator"
    
    @property
    def version(self) -> str:
        return "2024-01-01"
    
    def get_resource_types(self) -> List[str]:
        return ["sparkNodes", "sparkOllamaInstances", "sparkJobs"]
```

###  2. Models (`models/spark_node.py`)

**Old**:
```python
class SparkNodeRequest(BaseModel):
    name: str
    location: str
    properties: dict
```

**New**:
```python
from itl_controlplane_sdk.api.base.models import GenericResourceBase

class SparkNodeRequest(GenericResourceBase):
    name: str = Field(...)
    location: str = Field(...)
    properties: Dict[str, Any] = Field(default_factory=dict)
    # Inherits: tags, location validation, ARM-style fields
```

###  3. Routes (Setup Function Pattern)

**Old** (`routes/spark_nodes.py`):
```python
router = APIRouter(tags=["sparkNodes"])

@router.post("/subscriptions/{sub}/...")
async def create_spark_node(...):
    pass
```

**New** (`routes/spark_nodes.py`):
```python
def setup_spark_nodes_routes(app, engine, provider) -> APIRouter:
    router = APIRouter(tags=["sparkNodes"])
    
    @router.post("/subscriptions/{sub}/...")
    async def create_spark_node(...):
        # Can access engine and provider
        pass
    
    return router
```

###  4. Initialization Package

Created new `initialization/` package with:
- `server.py`: `AcceleratorProviderServer` (extends `BaseProviderServer`)
- `app_factory.py`: `create_app()` function
- `lifecycle.py`: `app_lifespan()` context manager

###  5. Route Updates

All routes now:
- Use setup functions that receive `app`, `engine`, `provider`
- Follow ARM-style URL patterns
- Return proper response models
- Include proper HTTP status codes (201, 202, 204, etc.)

## Required Actions

### 1. Update Dependencies (`pyproject.toml`)

Add SDK dependency:

```toml
dependencies = [
    # ... existing dependencies ...
    "itl-controlplane-sdk>=1.0.0",
]
```

### 2. Update `__init__.py`

```python
"""
ITL Accelerator Provider
"""
from .accelerator import AcceleratorProvider

__version__ = "0.1.0"
__all__ = ["AcceleratorProvider", "__version__"]
```

### 3. Replace `main.py`

Replace current `main.py` with `main_new.py`:

```bash
cd src/itl_accelerator_provider
mv main.py main_old.py
mv main_new.py main.py
```

Or manually update to:

```python
from .initialization import AcceleratorProviderServer

def main():
    server = AcceleratorProviderServer()
    server.run(host="0.0.0.0", port=8003)
```

### 4. Remove Old `provider.py`

The old `provider.py` is replaced by `accelerator.py`:

```bash
rm src/itl_accelerator_provider/provider.py
```

### 5. Create Model Files for Other Resources

Create `models/spark_instance.py` and `models/spark_job.py` following the same pattern as `spark_node.py`:

```python
from itl_controlplane_sdk.api.base.models import GenericResourceBase

class SparkOllamaInstanceRequest(GenericResourceBase):
    name: str = Field(...)
    model: str = Field(...)
    gpus: int = Field(default=1)
    memory_gb: int = Field(default=80)

class SparkOllamaInstanceResponse(GenericResourceBase):
    id: str = Field(...)
    name: str = Field(...)
    type: str = Field(default="ITL.Accelerator/sparkOllamaInstances")
    phase: str = Field(...)
    # ... etc
```

### 6. Update Dockerfile Entry Point

Update `Dockerfile` if it references the old main:

```dockerfile
CMD ["uvicorn", "itl_accelerator_provider.main:app", "--host", "0.0.0.0", "--port", "8003"]
```

Change to:

```dockerfile
CMD ["python", "-m", "itl_accelerator_provider.main"]
```

### 7. Install and Test

```bash
# Install with SDK
pip install -e ".[dev]"

# Verify SDK is installed
pip list | grep itl-controlplane-sdk

# Run provider
python -m itl_accelerator_provider.main

# Test endpoints
curl http://localhost:8003/
curl http://localhost:8003/health
curl http://localhost:8003/docs
```

## Benefits of SDK Integration

### 1. **Consistency**
- All providers follow the same architecture
- Standard middleware (audit, observability)
- Consistent error handling

### 2. **Reduced Boilerplate**
- No need to implement audit logging manually
- Standard observability endpoints (/health, /metrics)
- Generic resource endpoints from SDK

### 3. **Storage Engine Abstraction**
- Async SQLAlchemy integration
- Connection pooling handled by SDK
- Multi-tenant query filtering utilities

### 4. **RBAC Integration**
- Decorator-based role protection
- Token validation
- Automatic permission checks

### 5. **ServiceBus Support**
- Event-driven architecture support
- Message consumer mode
- Hybrid API + messaging mode

### 6. **Testing Utilities**
- SDK provides test fixtures
- Mock storage engine
- Test client helpers

## Migration Checklist

- [x] Create `accelerator.py` (provider class)
- [x] Create `initialization/` package
  - [x] `server.py` (AcceleratorProviderServer)
  - [x] `app_factory.py` (create_app)
  - [x] `lifecycle.py` (app_lifespan)
- [x] Update models to extend `GenericResourceBase`
- [x] Convert routes to setup functions
- [ ] Update `__init__.py` exports
- [ ] Add SDK to `pyproject.toml` dependencies
- [ ] Replace `main.py` with new version
- [ ] Remove old `provider.py`
- [ ] Create remaining model files
- [ ] Update Dockerfile CMD
- [ ] Test with `docker compose up`
- [ ] Verify all endpoints work
- [ ] Run integration tests

## Troubleshooting

### Import Error: `itl_controlplane_sdk`

**Problem**: `ModuleNotFoundError: No module named 'itl_controlplane_sdk'`

**Solution**: Install the SDK:
```bash
pip install itl-controlplane-sdk
# or add to pyproject.toml and reinstall
pip install -e ".[dev]"
```

### Import Error: Cannot import `AcceleratorProvider`

**Problem**: `ImportError: cannot import name 'AcceleratorProvider'`

**Solution**: Update `__init__.py` to export `AcceleratorProvider` from `accelerator.py`

### Route Setup Functions Not Working

**Problem**: Routes not registered or 404 errors

**Solution**: Verify routes return `APIRouter` and app_factory.py includes them:
```python
router = setup_spark_nodes_routes(app, engine, provider)
app.include_router(router)
```

### Storage Engine Errors

**Problem**: Database connection errors

**Solution**: 
1. Ensure PostgreSQL is running: `docker compose up -d postgres`
2. Check `DATABASE_URL` in environment
3. Verify engine initialization in lifecycle.py

## Next Steps After Migration

1. **Implement Repositories**
   - Create `repositories/spark_node_repo.py`
   - Implement multi-tenant filtering
   - Add CRUD operations with SQLAlchemy

2. **Implement Services**
   - Create `services/spark_node_service.py`
   - Business logic and validation
   - Integration with DGX Platform API

3. **Add RBAC**
   - Use `@rbac_protected` decorator from SDK
   - Define roles: consumer, admin, supplier
   - Configure Keycloak integration

4. **Add Audit Logging**
   - Use `@audit_event` decorator from SDK
   - Log all CRUD operations
   - Configure audit storage

5. **Create Database Migrations**
   - Alembic migrations for schema
   - sparkNodes, sparkOllamaInstances, sparkJobs tables
   - Indexes for multi-tenant queries

6. **Write Tests**
   - Unit tests with SDK test utilities
   - Integration tests
   - End-to-end scenarios

## References

- **Core Provider**: `d:\repos\ITL.ControlPlane.ResourceProvider.Core\core-provider\`
- **SDK Documentation**: `itl-controlplane-sdk` package docs
- **Architecture Guide**: `docs/ARCHITECTURE.md`
- **Control Plane Integration Guide**: `CONTROL_PLANE_INTEGRATION_GUIDE.md`

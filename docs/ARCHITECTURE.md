# Architecture

## Overview

ITL Accelerator Resource Provider follows the **Core provider pattern** with full SDK integration.

### SDK-Based Architecture

```
 itl_controlplane_sdk (dependency)
    providers.ResourceProvider (base class)
    persistence.SQLAlchemyStorageEngine
    api.base.models.GenericResourceBase
    audit, messaging, RBAC modules

 AcceleratorProvider (extends ResourceProvider)
    namespace: "ITL.Accelerator"
    version: "2024-01-01"
    resource_types: [sparkNodes, sparkOllamaInstances, sparkJobs]

 Routes (setup functions)
    setup_spark_nodes_routes(app, engine, provider)  APIRouter
    setup_spark_instances_routes(app, engine, provider)  APIRouter
    setup_spark_jobs_routes(app, engine, provider)  APIRouter

 Models (Pydantic, extends GenericResourceBase)
    SparkNodeRequest / SparkNodeResponse
    SparkOllamaInstanceRequest / SparkOllamaInstanceResponse
    SparkJobRequest / SparkJobResponse

 Initialization (to be created)
     AcceleratorProviderServer (extends BaseProviderServer)
     app_factory.create_app()
     lifecycle.app_lifespan()
```

## Implementation Status

###  Completed

1. **Provider Class** ([provider.py](../src/itl_accelerator_provider/provider.py))
   - Extends `itl_controlplane_sdk.providers.ResourceProvider`
   - Defines namespace `ITL.Accelerator`
   - Returns resource types: sparkNodes, sparkOllamaInstances, sparkJobs

2. **Models** ([models/spark_node.py](../src/itl_accelerator_provider/models/spark_node.py))
   - `SparkNodeRequest` extends `GenericResourceBase` from SDK
   - `SparkNodeResponse` extends `GenericResourceBase` from SDK
   - Proper Pydantic v2 configuration with examples

3. **Routes** ([routes/](../src/itl_accelerator_provider/routes/))
   - All routes converted to **setup functions** pattern
   - `setup_spark_nodes_routes(app, engine, provider)`  returns APIRouter
   - `setup_spark_instances_routes(app, engine, provider)`  returns APIRouter  
   - `setup_spark_jobs_routes(app, engine, provider)`  returns APIRouter
   - ARM-style paths: `/subscriptions/{sub}/resourceGroups/{rg}/providers/ITL.Accelerator/...`

4. **Package Structure**
   - Proper `__init__.py` exports with SDK imports
   - Models, routes, services, repositories, auth, audit, integrations packages ready

###  To Be Created

#### 1. Initialization Package (`src/itl_accelerator_provider/initialization/`)

Following Core provider pattern, create:

**`__init__.py`**
```python
from .server import AcceleratorProviderServer

__all__ = ["AcceleratorProviderServer"]
```

**`server.py`**
```python
from itl_controlplane_sdk.api import BaseProviderServer
from itl_controlplane_sdk.persistence import SQLAlchemyStorageEngine
from ..accelerator import AcceleratorProvider
from .app_factory import create_app

class AcceleratorProviderServer(BaseProviderServer):
    def __init__(self):
        self.engine = SQLAlchemyStorageEngine()
        self.provider = AcceleratorProvider(engine=self.engine)
        self.app = None
    
    def create_app(self) -> FastAPI:
        return create_app(self, self.engine, self.provider)
    
    def run(self, host: str = "0.0.0.0", port: int = 8003, **kwargs):
        provider_mode = os.getenv("PROVIDER_MODE", "api").lower()
        # ... mode handling (api/servicebus/hybrid)
```

**`app_factory.py`**
```python
from fastapi import FastAPI
from itl_controlplane_sdk.api import (
    setup_generic_routes,
    setup_observability_routes,
    add_audit_middleware,
)
from ..routes import (
    setup_spark_nodes_routes,
    setup_spark_instances_routes,
    setup_spark_jobs_routes,
)

def create_app(server, engine, provider) -> FastAPI:
    app = FastAPI(
        title="ITL Accelerator Resource Provider",
        version="0.1.0",
    )
    
    # SDK standard routes
    setup_generic_routes(app)
    setup_observability_routes(app)
    add_audit_middleware(app, engine)
    
    # Provider-specific routes
    spark_nodes_router = setup_spark_nodes_routes(app, engine, provider)
    spark_instances_router = setup_spark_instances_routes(app, engine, provider)
    spark_jobs_router = setup_spark_jobs_routes(app, engine, provider)
    
    app.include_router(spark_nodes_router)
    app.include_router(spark_instances_router)
    app.include_router(spark_jobs_router)
    
    return app
```

**`lifecycle.py`**
```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def app_lifespan(app: FastAPI):
    # Startup
    await engine.initialize()
    logger.info("Accelerator provider started")
    
    yield
    
    # Shutdown
    await engine.close()
    logger.info("Accelerator provider stopped")
```

#### 2. Update `main.py`

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
    
    logger.info("=" * 80)
    logger.info("ITL Accelerator Provider")
    logger.info(f"Host: {host}:{port}")
    logger.info("=" * 80)
    
    server = AcceleratorProviderServer()
    server.run(host=host, port=port, log_level="info")

if __name__ == "__main__":
    main()
```

#### 3. Update `pyproject.toml` Dependencies

Add `itl-controlplane-sdk>=1.0.0` to dependencies:

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
    "itl-controlplane-sdk>=1.0.0",  # <-- ADD THIS
]
```

#### 4. Update `__init__.py`

```python
"""
ITL Accelerator Provider
"""
from .accelerator import AcceleratorProvider

__version__ = "0.1.0"
__all__ = ["AcceleratorProvider", "__version__"]
```

## Resource Types

### SparkNode
- **Purpose**: Physical accelerator hardware (GPU, TPU, NPU)
- **Path**: `/subscriptions/{sub}/resourceGroups/{rg}/providers/ITL.Accelerator/sparkNodes/{name}`
- **Lifecycle**: Active  Maintenance  Retired
- **Model**: `SparkNodeRequest` / `SparkNodeResponse` (extends `GenericResourceBase`)

### SparkOllamaInstance
- **Purpose**: Provisioned LLM inference instance
- **Path**: `/subscriptions/{sub}/resourceGroups/{rg}/providers/ITL.Accelerator/sparkNodes/{nodeId}/sparkOllamaInstances/{name}`
- **Lifecycle**: Provisioning  Running  Stopping  Stopped
- **Model**: To be implemented (should extend `GenericResourceBase`)

### SparkJob
- **Purpose**: User-submitted compute job
- **Path**: `/subscriptions/{sub}/resourceGroups/{rg}/providers/ITL.Accelerator/sparkJobs/{jobId}`
- **Lifecycle**: Pending  Running  Completed/Failed
- **Model**: To be implemented (should extend `GenericResourceBase`)

## Key Design Patterns (from Core Provider)

### 1. Provider Class Pattern

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

### 2. Setup Function Pattern (Routes)

Instead of standalone routers, routes are created via setup functions:

```python
def setup_spark_nodes_routes(app, engine, provider) -> APIRouter:
    router = APIRouter(tags=["sparkNodes"])
    
    @router.post("/subscriptions/{sub}/resourceGroups/{rg}/...")
    async def create_spark_node(...):
        # Implementation with access to engine and provider
        pass
    
    return router
```

**Benefits:**
- Routes can access storage engine and provider instance
- Consistent initialization across all providers
- Easier testing with dependency injection

### 3. Model Pattern (Pydantic)

All models extend `GenericResourceBase` from SDK:

```python
from itl_controlplane_sdk.api.base.models import GenericResourceBase

class SparkNodeRequest(GenericResourceBase):
    name: str = Field(...)
    location: str = Field(...)
    properties: Dict[str, Any] = Field(default_factory=dict)
```

**Benefits:**
- Automatic ARM-style fields (tags, location, etc.)
- Consistent validation and serialization
- OpenAPI schema generation

### 4. Multi-Tenant Isolation

- All queries enforced with `subscription_id` + `resource_group` filtering
- Tenant context injected into every request
- Query-level WHERE clauses prevent cross-tenant data leakage

**Implementation in repositories (to be created):**

```python
async def list_spark_nodes(
    self, 
    subscription_id: str, 
    resource_group: str
) -> List[SparkNode]:
    stmt = select(SparkNode).where(
        SparkNode.subscription_id == subscription_id,
        SparkNode.resource_group == resource_group,
        SparkNode.deleted_at == None,
    )
    result = await self.session.execute(stmt)
    return result.scalars().all()
```

### 5. RBAC (To Be Implemented)

- Three roles: `itl-accelerator-consumer`, `itl-accelerator-admin`, `itl-accelerator-supplier`
- Decorator-based route protection from SDK
- Role checks before business logic execution

```python
from itl_controlplane_sdk.auth import rbac_protected

@router.post("/...")
@rbac_protected(required_roles=["itl-accelerator-admin"])
async def create_spark_node(...):
    pass
```

### 6. Async Provisioning (202 Accepted Pattern)

Long-running operations return 202 Accepted with status URL:

```python
@router.post("/.../sparkOllamaInstances/{name}", status_code=202)
async def provision_instance(...) -> dict:
    # Start async provisioning
    return {
        "id": instance_id,
        "status": "Provisioning",
        "status_url": f"/.../{instance_id}"
    }
```

### 7. Audit Trail (To Be Implemented)

All CRUD operations logged via SDK audit system:

```python
from itl_controlplane_sdk.audit import audit_event

@audit_event(action="spark_node.create")
async def create_spark_node(...):
    # Operation
    pass
```

Logs: actor_id, action, resource_type, resource_id, timestamp, changes

## Next Steps

1. **Create initialization package** (server.py, app_factory.py, lifecycle.py)
2. **Update main.py** to use `AcceleratorProviderServer`
3. **Update pyproject.toml** to add SDK dependency
4. **Create model files** for SparkOllamaInstance and SparkJob
5. **Implement repositories** with multi-tenant filtering
6. **Implement services** with business logic
7. **Add RBAC decorators** to routes
8. **Add audit logging** to all operations
9. **Create Alembic migrations** for database schema
10. **Write integration tests** with SDK test utilities

## Migration from Standalone to SDK Pattern

### Before (Standalone FastAPI)
```python
# main.py
app = FastAPI(...)

@app.get("/health")
async def health():
    return {"status": "healthy"}

# routes/spark_nodes.py
router = APIRouter()

@router.post("/...")
async def create_node():
    pass

app.include_router(router)
```

### After (SDK Integration)
```python
# initialization/server.py
class AcceleratorProviderServer(BaseProviderServer):
    def __init__(self):
        self.engine = SQLAlchemyStorageEngine()
        self.provider = AcceleratorProvider(engine=self.engine)

# initialization/app_factory.py
def create_app(server, engine, provider):
    app = FastAPI(...)
    setup_generic_routes(app)  # From SDK
    setup_observability_routes(app)  # From SDK
    
    router = setup_spark_nodes_routes(app, engine, provider)
    app.include_router(router)
    
    return app

# routes/spark_nodes.py
def setup_spark_nodes_routes(app, engine, provider):
    router = APIRouter()
    
    @router.post("/...")
    async def create_node():
        # Can use engine and provider
        pass
    
    return router
```

## References

- Core provider: `d:\repos\ITL.ControlPlane.ResourceProvider.Core\core-provider\`
- SDK documentation: `itl-controlplane-sdk` package
- ARM resource conventions: Azure Resource Manager patterns

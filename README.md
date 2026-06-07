# ITL.ControlPlane.ResourceProvider.Accelerator

**Accelerator Resource Provider** for ITL Control Plane  manages GPU, TPU, NPU, and other accelerator hardware.

Enables provisioning, lifecycle management, and billing for accelerated compute resources (Ollama instances, training jobs, batch inference) with full RBAC, multi-tenancy, and audit logging.

---

## Quick Start

### Local Development

```bash
# Clone and install
git clone https://github.com/itlusions/ITL.ControlPlane.ResourceProvider.Accelerator.git
cd ITL.ControlPlane.ResourceProvider.Accelerator
pip install -e ".[dev]"

# Start local dev environment
docker-compose up -d
pytest tests/ -v

# Run provider
python -m src.itl_accelerator_provider.main
```

### Docker

```bash
docker build -t itl-accelerator-provider:latest .
docker run -e DATABASE_URL="..." -p 8003:8000 itl-accelerator-provider:latest
```

---

## Architecture

**Three-tier layered architecture:**

```
API Routes (FastAPI)
    
Services (Business Logic)
    
Repositories (Data Access)
    
Database (PostgreSQL)
```

**Resource Types:**

| Resource | Path | Purpose |
|----------|------|---------|
| **SparkNode** | `/providers/ITL.Accelerator/sparkNodes/{name}` | Physical accelerator hardware |
| **SparkOllamaInstance** | `/sparkNodes/{nodeId}/sparkOllamaInstances/{name}` | Provisioned LLM instance |
| **SparkJob** | `/providers/ITL.Accelerator/sparkJobs/{jobId}` | User-submitted job (training, inference) |

**RBAC Roles:**

- `itl-accelerator-consumer`  Submit and monitor jobs
- `itl-accelerator-admin`  Manage nodes and instances
- `itl-accelerator-supplier`  Node owner (manage pricing/availability)

---

## Key Features

 **Multi-tenant isolation**  Subscription + ResourceGroup filtering at DB layer  
 **Full RBAC**  Role-based access control enforced on all routes  
 **Audit trail**  All operations logged with actor, action, timestamp  
 **Async provisioning**  202 Accepted pattern for long-running operations  
 **Usage tracking**  Real-time metrics aggregation for billing  
 **DGX Platform integration**  Provisioning orchestration via REST API  

---

## Project Structure

```
src/itl_accelerator_provider/
 __init__.py
 main.py                    # FastAPI app entry point
 provider.py                # ResourceProvider base implementation
 config.py                  # Configuration (Control Plane SDK setup)

 models/                    # SQLAlchemy ORM models
    spark_node.py
    spark_instance.py
    spark_job.py

 repositories/              # Data access layer
    spark_node_repo.py
    spark_instance_repo.py
    spark_job_repo.py

 services/                  # Business logic
    spark_node_service.py
    spark_instance_service.py
    spark_job_service.py
    usage_service.py

 routes/                    # FastAPI routes
    spark_nodes.py
    spark_instances.py
    spark_jobs.py

 auth/                      # RBAC & multi-tenancy
    rbac.py
    tenant_context.py

 audit/                     # Audit logging
    audit_logger.py

 integrations/              # External clients
     dgx_platform_client.py
     control_plane_sdk.py
```

---

## Environment Variables

```bash
# Control Plane Integration
CONTROL_PLANE_API_URL=http://controlplane-api:8000
CONTROL_PLANE_AUTH_URL=https://auth.itlusions.com

# DGX Platform Integration
DGX_PLATFORM_API_URL=http://dgx-platform:9504
DGX_PLATFORM_API_KEY=sk-xxx

# Database
DATABASE_URL=postgresql://admin:password@postgres:5432/accelerator_provider

# Service
SERVICE_PORT=8003
SERVICE_NAME=accelerator-provider
LOG_LEVEL=INFO
```

---

## API Endpoints

### SparkNodes (Hardware)

```bash
# List nodes in resource group
GET /subscriptions/{sub}/resourceGroups/{rg}/providers/ITL.Accelerator/sparkNodes

# Create node
POST /subscriptions/{sub}/resourceGroups/{rg}/providers/ITL.Accelerator/sparkNodes
{
  "name": "dgx-1",
  "location": "us-east-1",
  "sku": {"name": "DGX-H100-8GPU", "capacity": 8},
  "properties": {
    "owner": "owner-123",
    "hardwareSpecs": {...},
    "pricing": {...}
  }
}

# Get node
GET /subscriptions/{sub}/resourceGroups/{rg}/providers/ITL.Accelerator/sparkNodes/dgx-1

# Update node pricing
PUT /subscriptions/{sub}/resourceGroups/{rg}/providers/ITL.Accelerator/sparkNodes/dgx-1

# Delete node
DELETE /subscriptions/{sub}/resourceGroups/{rg}/providers/ITL.Accelerator/sparkNodes/dgx-1
```

### SparkOllamaInstances (Provisioned LLM)

```bash
# Provision instance on node
POST /subscriptions/{sub}/resourceGroups/{rg}/providers/ITL.Accelerator/sparkNodes/dgx-1/sparkOllamaInstances
{
  "name": "instance-1",
  "model": "mistral:7b",
  "gpus": 2,
  "memory_gb": 160
}

# Returns 202 Accepted with status_url

# Check provisioning status
GET /subscriptions/{sub}/resourceGroups/{rg}/providers/ITL.Accelerator/sparkNodes/dgx-1/sparkOllamaInstances/instance-1

# Get usage stats
GET /subscriptions/{sub}/resourceGroups/{rg}/providers/ITL.Accelerator/sparkNodes/dgx-1/sparkOllamaInstances/instance-1/stats?hours=24
```

### SparkJobs (User Jobs)

```bash
# Submit job
POST /subscriptions/{sub}/resourceGroups/{rg}/providers/ITL.Accelerator/sparkJobs
{
  "name": "job-1",
  "status": "Pending",
  "requested_gpus": 4,
  "requested_memory_gb": 320
}

# List user's jobs
GET /subscriptions/{sub}/resourceGroups/{rg}/providers/ITL.Accelerator/sparkJobs?submitted_by={userId}

# Get job details
GET /subscriptions/{sub}/resourceGroups/{rg}/providers/ITL.Accelerator/sparkJobs/job-1
```

---

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_spark_node_crud.py -v

# Run with coverage
pytest tests/ --cov=src/itl_accelerator_provider --cov-report=html

# Integration tests (requires docker-compose running)
pytest tests/integration/ -v
```

---

## Deployment

### Kubernetes (Helm)

```bash
# Install
helm install accelerator-provider ./helm \
  --namespace control-plane \
  --values helm/values-prod.yaml

# Upgrade
helm upgrade accelerator-provider ./helm \
  --namespace control-plane \
  --values helm/values-prod.yaml

# Uninstall
helm uninstall accelerator-provider --namespace control-plane
```

### Docker Compose (Dev)

```bash
docker-compose up -d
# Provider running at http://localhost:8003
# PostgreSQL at localhost:5432
```

---

## Documentation

- [ARCHITECTURE.md](docs/ARCHITECTURE.md)  Detailed design and patterns
- [API_REFERENCE.md](docs/API_REFERENCE.md)  Full endpoint documentation
- [INTEGRATION.md](docs/INTEGRATION.md)  DGX Platform integration details
- [RBAC.md](docs/RBAC.md)  Role-based access control setup

---

## Integration Checklist

- [ ] Phase 1: Foundations (Week 1-2)
  - [ ] Repository scaffold
  - [ ] ORM models created
  - [ ] Basic CRUD endpoints
  - [ ] 50+ unit tests passing

- [ ] Phase 2: RBAC & Audit (Week 2-3)
  - [ ] Role-based access control
  - [ ] Audit logging
  - [ ] Multi-tenant filtering
  - [ ] Compliance queries

- [ ] Phase 3: DGX Integration (Week 3-4)
  - [ ] DGXPlatformClient
  - [ ] Full provisioning workflow
  - [ ] Usage metrics syncing
  - [ ] State transitions

- [ ] Phase 4: Portal & CLI (Week 4-5)
  - [ ] Control Plane Portal UI
  - [ ] `itlc accelerator` commands
  - [ ] Copilot Chat integration

- [ ] Phase 5: Production (Week 5-6)
  - [ ] Performance optimization
  - [ ] Redis caching
  - [ ] Monitoring & alerting
  - [ ] 99.9% SLA compliance

---

## Support

- **Issues:** https://github.com/itlusions/ITL.ControlPlane.ResourceProvider.Accelerator/issues
- **Docs:** https://docs.itlusions.com/control-plane/accelerator
- **Slack:** #accelerator-provider

---

## License

MIT  See [LICENSE](LICENSE)

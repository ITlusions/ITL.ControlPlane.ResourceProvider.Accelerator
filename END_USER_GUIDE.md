# End User Guide: ITL DGX Platform (Accelerator Resource Provider)

## User Personas & Workflows

The ITL DGX Platform serves three main user personas with distinct workflows:

---

## 1. GPU Suppliers (Hardware Owners)

### Who They Are
- Companies with spare GPU capacity (NVIDIA DGX H100s, RTX GPUs, etc.)
- Data centers with underutilized infrastructure
- Research institutions wanting to monetize idle hardware

### How They Use the Platform

### Step 1: Register as Supplier

**Via Portal UI** (`ITL.ControlPlane.Portal`):
```
1. Navigate to https://accelerator.itlusions.com/supplier/register
2. Sign in with Keycloak (corporate identity)
3. Complete supplier onboarding:
   - Company details
   - Tax information
   - Bank account for payouts
   - Hardware inventory
```

**Via CLI** (`itlc accelerator`):
```bash
itlc accelerator supplier register \
  --company "TechCorp Inc" \
  --tax-id "NL123456789B01" \
  --bank-account "NL91ABNA0417164300"
```

**Via API** (Direct REST):
```bash
POST /subscriptions/{subscription}/resourceGroups/{rg}/providers/ITL.Accelerator/suppliers/register
Content-Type: application/json

{
  "name": "TechCorp Inc",
  "tax_id": "NL123456789B01",
  "contact": {
    "email": "ops@techcorp.nl",
    "phone": "+31-20-555-0100"
  }
}
```

### Step 2: Register Hardware Nodes

Register each GPU node in the platform:

**Via Portal UI**:
```
1. Dashboard  My Hardware  Add Node
2. Enter node details:
   - Node name: "dgx-amsterdam-01"
   - Hardware: NVIDIA DGX H100 (8H100 80GB, 640GB RAM)
   - Location: Amsterdam, Netherlands
   - Network: Tailscale VPN endpoint
   - Pricing: $12/hour per GPU = $96/hour total
3. Verify node connectivity (Tailscale ping test)
4. Submit for approval
```

**Via CLI**:
```bash
itlc accelerator node register \
  --name "dgx-amsterdam-01" \
  --sku "DGX-H100-8GPU" \
  --location "westeurope" \
  --gpus 8 \
  --memory 640 \
  --pricing 12.00 \
  --tailscale-ip "100.64.1.50"
```

**Via API**:
```bash
POST /subscriptions/{sub}/resourceGroups/{rg}/providers/ITL.Accelerator/sparkNodes

{
  "name": "dgx-amsterdam-01",
  "location": "westeurope",
  "properties": {
    "sku_name": "DGX-H100-8GPU",
    "gpu_count": 8,
    "gpu_model": "H100",
    "total_memory_gb": 640,
    "cpu_count": 128,
    "storage_gb": 7680,
    "tailscale_ip": "100.64.1.50"
  },
  "pricing": {
    "hourly_rate_per_gpu": 12.00,
    "hourly_rate_per_gb": 0.01
  }
}
```

### Step 3: Monitor Node Health

**Via Dashboard**:
```
1. Dashboard  My Nodes  dgx-amsterdam-01
2. View:
   - Status: Active/Maintenance/Offline
   - Current utilization: 87% (7/8 GPUs in use)
   - Connected instances:
     * instance-ai-training-1 (Llama2-70B, 4 GPUs)
     * instance-inference-prod (Mistral-7B, 3 GPUs)
   - Revenue today: $287.50
   - Revenue this month: $8,650.00
   - Uptime: 99.7%
```

**Via CLI**:
```bash
itlc accelerator node status dgx-amsterdam-01
```

**Via API**:
```bash
GET /subscriptions/{sub}/resourceGroups/{rg}/providers/ITL.Accelerator/sparkNodes/dgx-amsterdam-01
```

### Step 4: Earn Revenue

**Automatic Billing** (happens in background):
```
Every instance running on your node generates hourly revenue:

Instance 1 (4 GPUs): 4  $12.00  1 hour = $48.00
Instance 2 (3 GPUs): 3  $12.00  1 hour = $36.00
Instance 3 (640GB): 640  $0.01  1 hour = $6.40

Total per hour: $90.40
```

**Earnings Dashboard**:
- Real-time earnings counter
- Revenue by instance
- Historical charts
- Monthly earnings report
- Payout status

**Monthly Payouts**:
```
Automatic ACH transfer on the 1st of each month:
May earnings: $6,512.00
Payout date: June 1, 2024
Status: Pending verification
```

---

## 2. GPU Consumers (End Users)

### Who They Are
- AI/ML researchers needing GPU compute
- Companies fine-tuning LLMs (Llama, Mistral, Phi)
- Data science teams running inference workloads
- DeFi/trading platforms needing low-latency compute

### How They Use the Platform

### Step 1: Browse Available Hardware

**Via Portal UI** (`ITL.ControlPlane.Portal`):
```
1. Dashboard  Marketplace  Browse Nodes
2. Filter by:
   - GPU type: H100, A100, L40S
   - Location: Europe, US, Asia
   - GPU count: 1-8 GPUs
   - Price range: $5-20/hour per GPU
3. Sort by: Price, Rating, Availability
4. View details on each node
```

**Via API**:
```bash
GET /subscriptions/{sub}/resourceGroups/{rg}/providers/ITL.Accelerator/sparkNodes?filter=available&location=westeurope

Response:
{
  "value": [
    {
      "id": "/.../sparkNodes/dgx-amsterdam-01",
      "name": "dgx-amsterdam-01",
      "location": "westeurope",
      "properties": {
        "gpu_count": 8,
        "gpu_model": "H100",
        "status": "Active",
        "available_gpus": 5,
        "pricing": {
          "hourly_rate_per_gpu": 12.00,
          "hourly_rate_per_gb": 0.01
        },
        "rating": 4.8,
        "uptime_sla": "99.7%"
      }
    },
    ...more nodes...
  ]
}
```

### Step 2: Request to Provision an Instance

Reserve GPU capacity for your workload:

**Via Portal UI**:
```
1. Click on node  "Provision Instance"
2. Configure:
   - Instance name: "llama-finetune-prod"
   - Model: Llama2-70B (requires 280GB VRAM)
   - GPUs needed: 4  H100 = 280GB VRAM 
   - Duration: 168 hours (1 week)
   - Estimated cost: 4  $12  168 = $8,064
3. Review terms
4. Click "Provision"
```

**Via CLI**:
```bash
itlc accelerator provision \
  --node "dgx-amsterdam-01" \
  --model "llama2-70b" \
  --gpus 4 \
  --duration 168 \
  --name "llama-finetune-prod"
```

**Via API** (2-phase: Request  Provision):
```bash
# Phase 1: Submit provision request
POST /subscriptions/{sub}/resourceGroups/{rg}/providers/ITL.Accelerator/sparkNodes/{nodeId}/sparkOllamaInstances

{
  "name": "llama-finetune-prod",
  "model": "llama2-70b-hf",
  "gpus": 4,
  "memory_gb": 280,
  "duration_minutes": 10080
}

# Response (202 Accepted - async provisioning)
{
  "id": "instance-llama-finetune-prod",
  "status": "Provisioning",
  "status_url": "/subscriptions/{sub}/resourceGroups/{rg}/providers/ITL.Accelerator/sparkNodes/{nodeId}/sparkOllamaInstances/llama-finetune-prod",
  "estimated_ready_time": "2024-06-07T14:35:00Z"
}

# Phase 2: Poll status
GET /subscriptions/{sub}/resourceGroups/{rg}/providers/ITL.Accelerator/sparkNodes/{nodeId}/sparkOllamaInstances/llama-finetune-prod

# Response after ~2-3 minutes
{
  "id": "instance-llama-finetune-prod",
  "name": "llama-finetune-prod",
  "model": "llama2-70b-hf",
  "phase": "Running",
  "endpoint": "https://llama-finetune-prod.inference.accelerator.itlusions.com",
  "gpus_allocated": 4,
  "memory_allocated_gb": 280,
  "created_at": "2024-06-07T12:35:00Z"
}
```

### Step 3: Connect and Submit Jobs

Once instance is `Running`, you can submit inference/training jobs:

**Via Python Client** (Ollama API compatible):
```python
import requests

# Connect to your provisioned instance
base_url = "https://llama-finetune-prod.inference.accelerator.itlusions.com"
headers = {"Authorization": "Bearer YOUR_API_KEY"}

# Generate text
response = requests.post(
    f"{base_url}/api/generate",
    json={
        "model": "llama2-70b",
        "prompt": "Explain quantum computing in simple terms.",
        "stream": False
    },
    headers=headers
)

print(response.json()["response"])
# Output: Quantum computing is a revolutionary approach...
```

**Via cURL**:
```bash
curl -X POST https://llama-finetune-prod.inference.accelerator.itlusions.com/api/generate \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama2-70b",
    "prompt": "What is machine learning?",
    "stream": false
  }'
```

**Via CLI Job Submission**:
```bash
itlc accelerator job submit \
  --instance "llama-finetune-prod" \
  --script "finetune.py" \
  --data "training_data.jsonl" \
  --output "s3://my-bucket/models/"
```

### Step 4: Monitor Usage

**Via Dashboard**:
```
Instance: llama-finetune-prod
Status: Running (4/4 GPUs active)

Usage Statistics (Last 24 hours):
 Total requests: 1,247
 Total tokens processed: 2,341,892
 Average response time: 245ms
 Success rate: 99.8%
 Uptime: 100%

 Cost Breakdown:
    GPU compute: 4 GPUs  24 hours  $12 = $1,152.00
    Memory: 280GB  24 hours  $0.01 = $67.20
    Network: 145GB outbound  $0.10 = $14.50
    Total: $1,233.70
```

**Via API**:
```bash
GET /subscriptions/{sub}/resourceGroups/{rg}/providers/ITL.Accelerator/sparkNodes/{nodeId}/sparkOllamaInstances/{instanceId}/stats?hours=24

{
  "instance_id": "instance-llama-finetune-prod",
  "period_hours": 24,
  "total_requests": 1247,
  "total_tokens": 2341892,
  "avg_response_time_ms": 245,
  "success_rate": 0.998,
  "cost": {
    "compute": 1152.00,
    "memory": 67.20,
    "network": 14.50,
    "total": 1233.70
  }
}
```

### Step 5: Stop & Release

When done, deprovision to stop billing:

**Via Portal UI**:
```
1. Dashboard  Active Instances
2. Select "llama-finetune-prod"
3. Click "Deprovision"
4. Confirm
5. Instance stopped, billing ends immediately
```

**Via CLI**:
```bash
itlc accelerator deprovision llama-finetune-prod
```

**Via API**:
```bash
DELETE /subscriptions/{sub}/resourceGroups/{rg}/providers/ITL.Accelerator/sparkNodes/{nodeId}/sparkOllamaInstances/llama-finetune-prod
```

---

## 3. Platform Administrators (ITL Ops)

### Who They Are
- ITL platform operators
- Marketplace managers
- Support team
- Financial/billing staff

### How They Use the Platform

### Step 1: Monitor Marketplace Health

**Via Admin Dashboard** (`ITL.ControlPlane.Admin`):
```
Marketplace Overview:
 Total nodes: 1,247 (Active: 1,089, Maintenance: 158)
 Total GPUs: 8,956 (In use: 6,234, Available: 2,722)
 Active instances: 4,567
 Monthly revenue: $2.3M (supplier payouts: $1.8M)
 Platform uptime: 99.96%
 Average node utilization: 69.6%
```

### Step 2: Manage Suppliers

```
Supplier Management:
 Review supplier applications
 Approve/reject hardware registrations
 Handle disputes (slow nodes, payment issues)
 Monitor supplier ratings
 Manage payouts
```

**Via API** (Admin operations):
```bash
# Get all suppliers
GET /subscriptions/{admin-sub}/resourceGroups/{admin-rg}/providers/ITL.Accelerator/suppliers

# Review pending nodes
GET /subscriptions/{admin-sub}/resourceGroups/{admin-rg}/providers/ITL.Accelerator/sparkNodes?status=pending_verification

# Approve a node
POST /subscriptions/{admin-sub}/resourceGroups/{admin-rg}/providers/ITL.Accelerator/sparkNodes/{nodeId}/approve

# Suspend a node (if issues detected)
POST /subscriptions/{admin-sub}/resourceGroups/{admin-rg}/providers/ITL.Accelerator/sparkNodes/{nodeId}/suspend
```

### Step 3: Manage Compliance

- Verify supplier tax information
- Process payouts via ACH
- Generate financial reports
- Handle chargebacks
- Monitor SLA compliance

```bash
itlc accelerator admin payouts --month 2024-06 --status pending
itlc accelerator admin reports --type financial --output payouts-june-2024.csv
```

---

## 4. Integration Points

### Command Line Interface (CLI)

```bash
# Login
itlc login

# Supplier workflow
itlc accelerator supplier register ...
itlc accelerator node register --name "dgx-1" --sku "DGX-H100-8GPU"
itlc accelerator node list --my-nodes
itlc accelerator earnings --month 2024-06

# Consumer workflow
itlc accelerator browse
itlc accelerator provision --node "dgx-amsterdam-01" --model "llama2-70b"
itlc accelerator job submit --instance "llama-prod" --script train.py
itlc accelerator instances --active

# Admin workflow
itlc accelerator admin suppliers --pending
itlc accelerator admin approve-node --node-id "dgx-amsterdam-01"
itlc accelerator admin payouts --process
```

### Portal UI

- Supplier dashboard: earnings, nodes, payouts
- Consumer dashboard: marketplace, instances, costs
- Admin panel: marketplace health, suppliers, compliance

### REST API

All operations available via ARM-style REST endpoints:
```
POST   /providers/ITL.Accelerator/sparkNodes
GET    /providers/ITL.Accelerator/sparkNodes
PUT    /providers/ITL.Accelerator/sparkNodes/{nodeId}
DELETE /providers/ITL.Accelerator/sparkNodes/{nodeId}

POST   /sparkNodes/{nodeId}/sparkOllamaInstances
GET    /sparkNodes/{nodeId}/sparkOllamaInstances
DELETE /sparkNodes/{nodeId}/sparkOllamaInstances/{instanceId}

POST   /sparkJobs
GET    /sparkJobs
POST   /sparkJobs/{jobId}/cancel
```

### GitHub Copilot Chat Integration

Via GitHub Copilot Chat:
```
@copilot: "I need 4 H100 GPUs in Europe for 1 week to fine-tune Llama2"

Copilot: 
I can help you provision those GPUs. Here's what I found:
- dgx-amsterdam-01: 4 available H100s, $12/GPU/hour
- dgx-paris-02: 6 available H100s, $11.50/GPU/hour

Would you like me to provision the Amsterdam node? Cost: ~$8,064 for 1 week
```

---

## 5. Typical User Journeys

### Supplier Journey (First Week)

```
Day 1:
 Sign up via Portal
 Complete KYC verification
 Register DGX H100 node

Day 2-3:
 Node undergoes verification (performance tests)
 Node approved  Live on marketplace

Day 4-7:
 First customers provision instances
 Node generating $200-300/day revenue
 Monitor via dashboard
```

### Consumer Journey (One-Time Project)

```
Day 1:
 Browse marketplace
 Find suitable node (4H100 in Amsterdam, $12/GPU/hr)
 Provision instance

Day 2:
 Instance becomes ready (2-3 min after provision)
 Connect via Ollama API
 Start inference/training jobs

Day 3-8:
 Run continuous workload
 Monitor usage & costs via dashboard
 Check real-time inference metrics

Day 9:
 Deprovision instance (billing stops immediately)
 Download results
 Receive final invoice
```

### Consumer Journey (Ongoing Service)

```
Setup:
 Provision 2-3 permanent instances
 Configure auto-scaling by load
 Set up monitoring/alerts

Daily:
 Monitor latency, success rates
 Track costs (hourly alerts if exceeding budget)
 View earnings/ROI calculations

Monthly:
 Receive invoice with detailed breakdown
 Analyze cost trends
 Adjust capacity based on demand patterns
```

---

## 6. Pricing Models

### Pay-Per-GPU (Standard)

Suppliers set hourly rates per GPU:

```
H100 GPU (80GB VRAM):
 Standard tier: $10-15/hour
 Premium tier (SLA): $15-20/hour
 Bulk discount: $8-12/hour (1000+ hours/month)
```

### Pay-Per-Memory

Alternative for memory-intensive workloads:

```
Pricing per GB/hour: $0.01-0.02
For 640GB node: $6.40-12.80/hour + GPU fees
```

### Reserved Capacity

For predictable, ongoing workloads:

```
Example: Reserve 2H100 for 12 months
 On-demand: 2  $12  24  365 = $210,240
 1-month commitment: 15% discount = $178,704
 12-month commitment: 35% discount = $136,656
 Monthly: $11,388 (vs $17,520 on-demand)
```

---

## 7. Getting Started

### For Suppliers

1. Sign up at https://accelerator.itlusions.com/supplier
2. Complete KYC verification (tax ID, bank account)
3. Register your first DGX node
4. Wait for verification (24-48 hours)
5. Start earning!

### For Consumers

1. Sign up at https://accelerator.itlusions.com/consumer
2. Browse marketplace
3. Provision first instance
4. Connect via Ollama API
5. Start running workloads

### For Developers

1. Get API key: https://accelerator.itlusions.com/api-keys
2. Read API docs: https://docs.accelerator.itlusions.com/api
3. Clone example repos: https://github.com/ITlusions/accelerator-examples
4. Start integrating!

```python
# Example: Minimal client
from accelerator_sdk import Client

client = Client(api_key="YOUR_API_KEY")

# Find available nodes
nodes = client.nodes.list(location="westeurope", status="available")

# Provision instance
instance = client.instances.provision(
    node_id=nodes[0]["id"],
    model="llama2-70b",
    gpus=4,
    duration_hours=168
)

# Wait for provisioning
instance.wait_until_ready()

# Run inference
response = instance.generate(
    prompt="What is AI?",
    max_tokens=200
)
print(response)
```

---

## Support & SLAs

### For Suppliers
- Node uptime SLA: 99.5%
- Response time to support: < 1 hour
- Payment processing: 1st of month

### For Consumers
- Instance availability: 99.9%
- Support response: < 30 minutes
- Billing accuracy guarantee: 0.1%

---

## FAQs

**Q: How quickly does provisioning take?**
A: 2-3 minutes from request to "Running" state. Instance is ready to accept jobs immediately.

**Q: What happens if a node goes offline?**
A: Running instances migrate to backup nodes automatically (no data loss). Billing continues at same rate.

**Q: Can I move data between nodes?**
A: Yes, via shared S3 bucket or direct transfer. No additional charges for inter-node transfers.

**Q: What models are pre-loaded?**
A: Mistral-7B, Llama2-7B/13B/70B, Phi-2.8B. Custom models via upload (add 5-10 min to provisioning).

**Q: Is GPU time billed by the second?**
A: Yes, billing is per-second. Provision 1 hour = pay only for time used.

**Q: Can I scale instances up/down?**
A: Yes, provision additional instances or deprovision unused ones instantly.

---

## Next Steps

- **Suppliers**: Register your first node
- **Consumers**: Browse marketplace and provision a test instance
- **Developers**: Check out API documentation and examples

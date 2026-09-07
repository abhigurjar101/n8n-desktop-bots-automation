# n8n Desktop Bots - Complete Setup Guide (NVIDIA Nemotron 3 Ultra Only)

This guide sets up **9 powerful AI bots** running locally on your desktop via n8n, **using exclusively NVIDIA's Nemotron 3 Ultra 550B model** with your NVIDIA API key.

## Core Development Bots (5)
1. **Coding Assistant** - Code generation, review, refactoring, debugging, test generation
2. **RAG Bot** - Local document ingestion & Q&A with vector search
3. **System Design Bot** - Architecture design, tech selection, capacity planning, ADRs
4. **High Thinking Bot** - Deep reasoning, debate, mental models, decision analysis
5. **Testing Bot** - Test generation, execution, coverage, debugging, review

## Advanced Production Bots (4) - NEW
6. **Advanced RAG Bot** - Hybrid search (BM25 + dense), cross-encoder reranking, agentic multi-step, evaluation
7. **Cloud Deployment Bot** - Terraform, K8s manifests, Helm charts, CI/CD, cost estimation, validation
8. **AI/ML Pipeline Bot** - Full ML lifecycle: data prep, training, evaluation, deployment, monitoring, HPO
9. **n8n Manager Bot** - Production n8n ops: deploy, backup, scale, monitor, migrate

---

## Prerequisites

### Required Software
```bash
# macOS (Homebrew)
brew install node@20 docker qdrant kubectl helm terraform

# Or download directly:
# - Node.js 20+: https://nodejs.org/
# - Docker Desktop: https://docker.com/products/docker-desktop
# - Qdrant: https://qdrant.tech/documentation/quick-start/
# - kubectl: https://kubernetes.io/docs/tasks/tools/
# - helm: https://helm.sh/docs/intro/install/
# - terraform: https://developer.hashicorp.com/terraform/downloads
```

### API Keys Needed
- **NVIDIA API Key** - Required for ALL bots (get from https://build.nvidia.com/)
  - Model: `nvidia/nemotron-3-ultra-550b-a55b` (chat/completion)
  - Embeddings: `nvidia/nv-embedqa-e5-v5` (for RAG)
- **Cloud Provider Credentials** - AWS/GCP/Azure for deployment bot (optional)

**No OpenAI, Anthropic, HuggingFace, or Ollama needed.** Everything runs on NVIDIA's API.

---

## Quick Start (5 minutes)

### 1. Start Infrastructure
```bash
# Start Qdrant (vector database)
docker run -d -p 6333:6333 -p 6334:6334 \
  -v $(pwd)/qdrant_data:/qdrant/storage \
  qdrant/qdrant
```

### 2. Install & Start n8n
```bash
# Global install
npm install -g n8n

# Or use npx (no install)
npx n8n

# n8n starts at http://localhost:5678
```

### 3. Import Workflows
1. Open http://localhost:5678
2. Go to **Workflows → Import from File**
3. Import all 9 JSON files from `workflows/`:
   - `01-coding-assistant.json`
   - `02-rag-bot.json`
   - `03-system-design-bot.json`
   - `04-high-thinking-bot.json`
   - `05-testing-bot.json`
   - `06-advanced-rag-bot.json`
   - `07-cloud-deployment-bot.json`
   - `08-ml-pipeline-bot.json`
   - `09-n8n-manager-bot.json`

### 4. Configure Credentials
In n8n → **Credentials → New Credential**:

**NVIDIA API** (for ALL bots)
- Type: OpenAI API
- Name: `nvidiaApi`
- API Key: `nvapi-...` (your NVIDIA API key)
- **Base URL**: `https://integrate.api.nvidia.com/v1` (already configured in workflows)

**Qdrant** (for RAG bots)
- Type: HTTP Header Auth
- Name: `qdrantAuth`
- Header: `api-key`
- Value: (leave empty for local Qdrant, or add your Qdrant Cloud key)

**n8n API** (for n8n Manager bot)
- Type: HTTP Header Auth
- Name: `n8nApiAuth`
- Header: `X-N8N-API-KEY`
- Value: (get from n8n Settings → API)

### 5. Activate Workflows
Click **Activate** on each imported workflow.

---

## Model Configuration

All workflows are pre-configured to use:
- **Chat/Completion**: `nvidia/nemotron-3-ultra-550b-a55b`
- **Embeddings**: `nvidia/nv-embedqa-e5-v5`
- **Base URL**: `https://integrate.api.nvidia.com/v1`

These are already set in the workflow JSON files. No additional configuration needed.

---

## Bot Usage Examples

### 1. Coding Assistant
```bash
# Generate code
curl -X POST http://localhost:5678/webhook/coding-assistant \
  -H "Content-Type: application/json" \
  -d '{
    "task": "generate a REST API for user management with Express and TypeScript",
    "language": "typescript"
  }'

# Review code
curl -X POST http://localhost:5678/webhook/coding-assistant \
  -H "Content-Type: application/json" \
  -d '{
    "task": "review this code for bugs and security issues",
    "code": "function getUser(id) { return db.query(`SELECT * FROM users WHERE id = ${id}`) }",
    "language": "javascript"
  }'

# Generate tests
curl -X POST http://localhost:5678/webhook/coding-assistant \
  -H "Content-Type: application/json" \
  -d '{
    "task": "test generate comprehensive tests for this function",
    "code": "export function calculateTotal(items) { return items.reduce((sum, i) => sum + i.price * i.qty, 0) }",
    "language": "typescript",
    "testFramework": "vitest"
  }'
```

### 2. RAG Bot (Basic)
```bash
# Create collection (run once)
curl -X POST http://localhost:5678/webhook/rag-ingest \
  -H "Content-Type: application/json" \
  -d '{"collectionName": "my_docs"}'

# Ingest documents
curl -X POST http://localhost:5678/webhook/rag-ingest \
  -H "Content-Type: application/json" \
  -d '{
    "directory": "/Users/you/projects/my-docs",
    "chunkSize": 1000,
    "chunkOverlap": 200
  }'

# Query
curl -X POST http://localhost:5678/webhook/rag-query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How does the authentication system work?",
    "topK": 5
  }'
```

### 3. System Design Bot
```bash
curl -X POST http://localhost:5678/webhook/system-design \
  -H "Content-Type: application/json" \
  -d '{
    "task": "design",
    "requirements": "Real-time chat app for 1M users with message history, presence, and push notifications",
    "scale": "1M concurrent users, 10M messages/day",
    "techStack": "TypeScript, PostgreSQL, Redis, Kubernetes",
    "constraints": "Sub-100ms latency, 99.99% uptime, GDPR compliance"
  }'
```

### 4. High Thinking Bot
```bash
# Deep reasoning
curl -X POST http://localhost:5678/webhook/high-thinking \
  -H "Content-Type: application/json" \
  -d '{
    "problem": "Should we rewrite our monolith in microservices or modular monolith?",
    "mode": "deep",
    "context": "Team of 20, 5 year old codebase, scaling issues emerging"
  }'

# Six Thinking Hats
curl -X POST http://localhost:5678/webhook/high-thinking \
  -H "Content-Type: application/json" \
  -d '{
    "problem": "Adopt AI coding assistants team-wide",
    "mode": "debate"
  }'

# Decision Analysis
curl -X POST http://localhost:5678/webhook/high-thinking \
  -H "Content-Type: application/json" \
  -d '{
    "problem": "Choose primary database for new project",
    "mode": "decision",
    "options": ["PostgreSQL", "MongoDB", "DynamoDB", "CockroachDB"],
    "criteria": ["Consistency", "Scalability", "Team Familiarity", "Cost", "Operational Burden"]
  }'
```

### 5. Testing Bot
```bash
# Generate tests
curl -X POST http://localhost:5678/webhook/testing/generate \
  -H "Content-Type: application/json" \
  -d '{
    "code": "export class UserService { constructor(private db) {} async getUser(id) { return this.db.users.find(id) } }",
    "language": "typescript",
    "framework": "vitest",
    "testTypes": ["unit", "edge", "integration"]
  }'

# Execute tests
curl -X POST http://localhost:5678/webhook/testing/execute \
  -H "Content-Type: application/json" \
  -d '{
    "projectPath": "/Users/you/my-project",
    "framework": "vitest",
    "coverage": true
  }'

# Coverage analysis
curl -X POST http://localhost:5678/webhook/testing/coverage \
  -H "Content-Type: application/json" \
  -d '{
    "projectPath": "/Users/you/my-project",
    "framework": "vitest"
  }'
```

### 6. Advanced RAG Bot (Production-Grade)
```bash
# Ingest with advanced chunking
curl -X POST http://localhost:5678/webhook/rag/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "directory": "/Users/you/projects/my-docs",
    "chunkStrategy": "semantic",
    "chunkSize": 1000,
    "chunkOverlap": 200,
    "extractImages": true,
    "extractTables": true
  }'

# Hybrid search with reranking (uses Nemotron for reranking too)
curl -X POST http://localhost:5678/webhook/rag/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Explain the authentication flow",
    "topK": 10,
    "hybridWeight": 0.5,
    "rerank": true,
    "searchMode": "hybrid"
  }'

# Agentic multi-step reasoning
curl -X POST http://localhost:5678/webhook/rag/agentic \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Compare authentication methods across all docs and recommend best for our stack",
    "maxSteps": 5,
    "tools": ["search_hybrid", "fetch_document"]
  }'

# Evaluate RAG quality
curl -X POST http://localhost:5678/webhook/rag/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "testCases": [
      {"query": "What is OAuth?", "expected": "OAuth is an authorization framework...", "actual": "..."},
      {"query": "How to implement JWT?", "expected": "Use HS256 or RS256...", "actual": "..."}
    ]
  }'
```

### 7. Cloud Deployment Bot
```bash
# Generate Terraform for AWS EKS
curl -X POST http://localhost:5678/webhook/cloud/terraform/generate \
  -H "Content-Type: application/json" \
  -d '{
    "requirements": "EKS cluster with RDS PostgreSQL, ElastiCache Redis, ALB for microservices",
    "cloudProvider": "aws",
    "environment": "production",
    "modules": ["vpc", "eks", "rds", "elasticache", "alb", "s3", "cloudfront"]
  }'

# Generate K8s manifests
curl -X POST http://localhost:5678/webhook/cloud/k8s/generate \
  -H "Content-Type: application/json" \
  -d '{
    "appName": "my-api",
    "image": "myorg/my-api:v1.2.3",
    "replicas": 5,
    "resources": {"requests": {"cpu": "250m", "memory": "256Mi"}, "limits": {"cpu": "1000m", "memory": "1Gi"}},
    "autoscaling": {"enabled": true, "minReplicas": 3, "maxReplicas": 20, "targetCPU": 70},
    "ingress": {"enabled": true, "host": "api.myapp.com", "tls": true}
  }'

# Generate Helm chart
curl -X POST http://localhost:5678/webhook/cloud/helm/generate \
  -H "Content-Type: application/json" \
  -d '{
    "chartName": "my-microservice",
    "appVersion": "1.2.3",
    "dependencies": [{"name": "postgresql", "repository": "https://charts.bitnami.com/bitnami", "version": "12.x"}],
    "values": {"replicaCount": 3, "autoscaling": {"enabled": true}}
  }'

# Deploy infrastructure
curl -X POST http://localhost:5678/webhook/cloud/deploy \
  -H "Content-Type: application/json" \
  -d '{
    "action": "terraform_apply",
    "workingDir": "/tmp/n8n-cloud/terraform/aws/production"
  }'

# Cost estimation
curl -X POST http://localhost:5678/webhook/cloud/cost-estimate \
  -H "Content-Type: application/json" \
  -d '{
    "terraformPlan": "...plan output...",
    "cloudProvider": "aws",
    "region": "us-east-1"
  }'

# Validate configs
curl -X POST http://localhost:5678/webhook/cloud/validate \
  -H "Content-Type: application/json" \
  -d '{
    "terraformDir": "/tmp/n8n-cloud/terraform/aws/production",
    "k8sDir": "/tmp/n8n-cloud/k8s/my-api",
    "policies": ["CIS Benchmarks", "AWS Well-Architected", "PCI-DSS"]
  }'

# Generate CI/CD pipeline
curl -X POST http://localhost:5678/webhook/cloud/cicd \
  -H "Content-Type: application/json" \
  -d '{
    "appName": "my-api",
    "cloudProvider": "aws",
    "cicdPlatform": "github-actions",
    "environments": ["dev", "staging", "prod"]
  }'
```

### 8. AI/ML Pipeline Bot
```bash
# Prepare data
curl -X POST http://localhost:5678/webhook/ml/data/prepare \
  -H "Content-Type: application/json" \
  -d '{
    "source": "s3://my-bucket/raw-data/",
    "format": "parquet",
    "splits": {"train": 0.7, "val": 0.15, "test": 0.15},
    "preprocessing": ["clean", "normalize", "encode"],
    "validation": {"check_nulls": true, "check_ranges": true}
  }'

# Train model (Nemotron generates PyTorch Lightning code)
curl -X POST http://localhost:5678/webhook/ml/train \
  -H "Content-Type: application/json" \
  -d '{
    "task": "classification",
    "framework": "lightning",
    "modelArch": "TransformerEncoder",
    "hyperparameters": {"lr": 3e-4, "batch_size": 64, "epochs": 50, "weight_decay": 1e-2},
    "dataConfig": {"train_path": "/data/train.parquet", "val_path": "/data/val.parquet"},
    "compute": {"gpus": 2, "precision": "16-mixed", "strategy": "ddp"},
    "tracking": "mlflow"
  }'

# Evaluate model
curl -X POST http://localhost:5678/webhook/ml/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "modelPath": "s3://my-bucket/models/best.ckpt",
    "testData": "/data/test.parquet",
    "metrics": ["accuracy", "precision", "recall", "f1", "roc_auc", "pr_auc"],
    "slicing": ["overall", "by_class", "by_feature_quartile"],
    "fairness": true,
    "robustness": true,
    "explainability": true
  }'

# Deploy to K8s (KServe)
curl -X POST http://localhost:5678/webhook/ml/deploy \
  -H "Content-Type: application/json" \
  -d '{
    "modelPath": "s3://my-bucket/models/best.ckpt",
    "targetPlatform": "k8s",
    "servingFramework": "fastapi",
    "optimization": "onnx",
    "scaling": {"minReplicas": 2, "maxReplicas": 20, "targetLatency": 100}
  }'

# Generate monitoring stack
curl -X POST http://localhost:5678/webhook/ml/monitor \
  -H "Content-Type: application/json" \
  -d '{
    "modelEndpoint": "http://my-model.default.svc.cluster.local",
    "metrics": ["latency_p50", "latency_p99", "throughput", "error_rate", "prediction_drift", "feature_drift"],
    "alerting": "pagerduty+slack",
    "driftDetection": true
  }'

# Run hyperparameter optimization
curl -X POST http://localhost:5678/webhook/ml/experiment \
  -H "Content-Type: application/json" \
  -d '{
    "experimentName": "transformer-hpo",
    "searchSpace": {
      "lr": {"type": "loguniform", "low": 1e-5, "high": 1e-2},
      "batch_size": {"type": "choice", "values": [32, 64, 128, 256]},
      "hidden_dim": {"type": "choice", "values": [256, 512, 1024, 2048]},
      "num_layers": {"type": "choice", "values": [3, 6, 9, 12]},
      "dropout": {"type": "uniform", "low": 0.1, "high": 0.4}
    },
    "algorithm": "tpe",
    "maxTrials": 100,
    "objective": "val_f1",
    "framework": "optuna"
  }'
```

### 9. n8n Manager Bot (Production Operations)
```bash
# Deploy n8n to Kubernetes
curl -X POST http://localhost:5678/webhook/n8n/deploy \
  -H "Content-Type: application/json" \
  -d '{
    "mode": "kubernetes",
    "version": "latest",
    "domain": "n8n.mycompany.com",
    "email": "admin@mycompany.com",
    "replicas": 3,
    "resources": {"requests": {"cpu": "500m", "memory": "1Gi"}, "limits": {"cpu": "2000m", "memory": "4Gi"}},
    "database": {"type": "postgresql", "host": "postgres", "pool": 20},
    "queue": {"type": "redis", "mode": "cluster"},
    "storage": {"type": "nfs", "size": "50Gi"},
    "ingress": {"class": "nginx", "tls": true},
    "auth": {"type": "basic", "sso": false},
    "monitoring": "prometheus+grafana+loki"
  }'

# Backup configuration
curl -X POST http://localhost:5678/webhook/n8n/backup \
  -H "Content-Type: application/json" \
  -d '{
    "schedule": "0 2 * * *",
    "retention": "daily:30,weekly:12,monthly:12",
    "destinations": ["s3", "gcs", "local"],
    "encryption": true,
    "include": ["database", "workflows", "credentials", "binary_data", "config", "logs"]
  }'

# Restore from backup
curl -X POST http://localhost:5678/webhook/n8n/restore \
  -H "Content-Type: application/json" \
  -d '{
    "backupSource": "s3://my-backups/n8n/2024-01-15/",
    "targetEnvironment": "staging",
    "pointInTime": "latest",
    "verifyOnly": false
  }'

# Auto-scaling with KEDA
curl -X POST http://localhost:5678/webhook/n8n/scale \
  -H "Content-Type: application/json" \
  -d '{
    "currentReplicas": 3,
    "targetReplicas": "auto",
    "trigger": "queue_depth",
    "hpaConfig": {"minReplicas": 3, "maxReplicas": 20, "targetCPU": 70, "targetMemory": 80},
    "kedaConfig": {"scaler": "redis", "queueName": "bull:default", "targetItemsPerPod": 50}
  }'

# Monitoring stack
curl -X POST http://localhost:5678/webhook/n8n/monitor \
  -H "Content-Type: application/json" \
  -d '{
    "metricsPort": 5678,
    "grafanaDashboards": true,
    "alertRules": true,
    "logAggregation": "loki",
    "tracing": "jaeger"
  }'

# Migration plan
curl -X POST http://localhost:5678/webhook/n8n/migrate \
  -H "Content-Type: application/json" \
  -d '{
    "sourceVersion": "1.40.0",
    "targetVersion": "1.50.0",
    "sourceEnv": "production",
    "targetEnv": "staging",
    "migrationStrategy": "blue-green"
  }'

# n8n API operations
curl -X POST http://localhost:5678/webhook/n8n/api \
  -H "Content-Type: application/json" \
  -d '{
    "action": "listWorkflows"
  }'
```

---

## Advanced Configuration

### Custom Qdrant Collection
```bash
# For different embedding dimensions (nv-embedqa-e5-v5 uses 1024)
curl -X PUT http://localhost:6333/collections/my_collection \
  -H "Content-Type: application/json" \
  -d '{"vectors": {"size": 1024, "distance": "Cosine"}}'
```

### Persistent n8n Data
```bash
# Run n8n with persistent data
docker run -d -p 5678:5678 \
  -v $(pwd)/n8n_data:/home/node/.n8n \
  -e N8N_BASIC_AUTH_ACTIVE=true \
  -e N8N_BASIC_AUTH_USER=admin \
  -e N8N_BASIC_AUTH_PASSWORD=yourpassword \
  n8nio/n8n
```

### n8n API Key Setup
```bash
# In n8n UI: Settings → API → Create API Key
# Then set env var for n8n Manager bot:
export N8N_API_URL=http://localhost:5678/api/v1
export N8N_API_KEY=your-api-key
```

---

## Directory Structure
```
n8n-desktop-bots/
├── workflows/
│   ├── 01-coding-assistant.json
│   ├── 02-rag-bot.json
│   ├── 03-system-design-bot.json
│   ├── 04-high-thinking-bot.json
│   ├── 05-testing-bot.json
│   ├── 06-advanced-rag-bot.json
│   ├── 07-cloud-deployment-bot.json
│   ├── 08-ml-pipeline-bot.json
│   └── 09-n8n-manager-bot.json
├── DESKTOP_SETUP_GUIDE.md
├── README.md
└── start-all.sh
```

---

## Start All Script
```bash
#!/bin/bash
# n8n Desktop Bots - Start All Infrastructure (NVIDIA Nemotron 3 Ultra)

docker start qdrant 2>/dev/null || docker run -d --name qdrant -p 6333:6333 -p 6334:6334 -v $(pwd)/qdrant_data:/qdrant/storage qdrant/qdrant
npx n8n
```
```bash
chmod +x start-all.sh
./start-all.sh
```

---

## Troubleshooting

### Qdrant Connection Failed
```bash
curl http://localhost:6333/health
# Should return {"status":"ok"}
```

### NVIDIA API Rate Limits / Errors
- Check your NVIDIA API key is valid at https://build.nvidia.com/
- Nemotron 3 Ultra has rate limits - add delays between requests
- For high volume, consider NVIDIA's dedicated endpoints

### n8n Webhook Not Accessible
- Check n8n is running on port 5678
- For external access, use ngrok: `ngrok http 5678`
- Update webhook URLs in n8n settings if using tunnel

### Large Document Ingestion
- Increase chunk size for code: 2000-3000
- Use `pdf-parse` for PDFs (already in workflow)
- Monitor Qdrant disk usage: `docker exec qdrant du -sh /qdrant/storage`

### Embedding Dimension Mismatch
- nv-embedqa-e5-v5 produces 1024-dim vectors
- Ensure Qdrant collection uses `size: 1024`

### K8s Commands Fail
- Ensure `kubectl` configured: `kubectl cluster-info`
- Check context: `kubectl config current-context`

---

## Adding More Workflows

Browse 10,000+ workflows from:
- https://n8nworkflows.xyz/ (11,317 workflows, API available)
- https://github.com/enescingoz/awesome-n8n-templates (280+ curated)
- https://github.com/Zie619/n8n-workflows (4,343 workflows, searchable)
- https://n8n.io/workflows/ (12,125 community workflows)
- https://github.com/wassupjay/n8n-free-templates (200+ AI-focused)

Download JSON → Import in n8n → Configure credentials → Activate

---

## License & Credits

Workflows created by combining patterns from:
- n8n community templates (MIT/Apache-2.0)
- awesome-n8n-templates by enescingoz
- n8n-workflows by Zie619
- n8n-free-templates by wassupjay

Custom bot workflows: MIT License - Use freely for any purpose.

**Powered by NVIDIA Nemotron 3 Ultra 550B** 🚀
# n8n Desktop Bots - 9 AI Agents for Your Desktop (NVIDIA Nemotron 3 Ultra Only)

> **Built from 10,000+ n8n workflows** across the top community sources  
> **Powered exclusively by NVIDIA's Nemotron 3 Ultra 550B model**

## 🤖 The 9 Bots

### Core Development Bots (5)
| Bot | Purpose | Key Features |
|-----|---------|--------------|
| **🧑‍💻 Coding Assistant** | Code generation, review, refactor, debug, test | Multi-language, GitHub push, file save, test generation |
| **📚 RAG Bot** | Local document Q&A with vector search | PDF/code/text ingestion, Qdrant vectors, hybrid search |
| **🏗️ System Design Bot** | Architecture design, tech selection, capacity planning | C4 diagrams, Mermaid.js, ADRs, trade-off analysis |
| **🧠 High Thinking Bot** | Deep reasoning, debate, mental models, decisions | 6 modes, self-critique, Six Hats, decision matrices |
| **🧪 Testing Bot** | Test generation, execution, coverage, debugging | Vitest/Jest/Pytest, coverage reports, flaky detection |

### Advanced Production Bots (4) - **NEW**
| Bot | Purpose | Key Features |
|-----|---------|--------------|
| **🔬 Advanced RAG Bot** | Production RAG with hybrid search, reranking, agentic patterns | BM25 + dense fusion, Nemotron rerank, agentic multi-step, evaluation |
| **☁️ Cloud Deployment Bot** | Infrastructure as Code: K8s, Terraform, Helm, multi-cloud | Terraform modules, K8s manifests, Helm charts, CI/CD, cost estimation, validation |
| **🤖 AI/ML Pipeline Bot** | Full ML lifecycle: data prep, training, eval, deploy, monitor | Multi-framework (PyTorch/TF/Lightning/HF), HPO, optimization, serving, observability |
| **🎛️ n8n Manager Bot** | Production n8n ops: deploy, backup, scale, monitor, migrate | K8s/Docker/ECS deploy, encrypted backup/restore, KEDA/HPA/VPA, Prometheus/Grafana/Loki |

---

---

## 🚀 Quick Start

### Option A: Web Control Center & Dashboard (Recommended)

```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Start infrastructure (Qdrant vector DB + n8n)
./start-all.sh
# (or with docker compose: make docker-start)

# 3. Launch the Control Center Dashboard
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
# (or simply: make ui)

# 4. Open http://localhost:8000 in your browser!
```

### Option B: Terminal CLI Runner

```bash
# Check service connectivity
python cli.py status

# List all 9 bots
python cli.py list

# Run Coding Assistant
python cli.py code "Build an LRU cache with TTL in TypeScript"

# Run System Design Bot
python cli.py design "Real-time chat platform" --scale "100k RPS"

# Run High Thinking Bot
python cli.py think "Should we rewrite in Rust?" --mode firstPrinciples
```

---

## 📁 Project Structure

```
n8n-desktop-bots/
├── app/                                 # Control Center Web Application
│   ├── main.py                          # FastAPI server & API gateway
│   ├── client.py                        # Python SDK client for all 9 bots
│   └── static/                          # Modern Dark-Mode Dashboard
│       ├── index.html                   # Interactive UI (Tailwind + Mermaid.js)
│       ├── app.js                       # Dynamic bot forms & webhook dispatch
│       └── styles.css                   # Custom styles & dark theme
├── cli.py                               # Terminal CLI runner
├── scripts/
│   ├── health_check.py                  # Infrastructure connectivity test
│   └── import_workflows.py              # Automated n8n workflow importer
├── workflows/                           # 9 Production n8n Workflow JSONs
│   ├── 01-coding-assistant.json         # Coding Assistant Bot
│   ├── 02-rag-bot.json                  # RAG Bot
│   ├── 03-system-design-bot.json        # System Design Bot
│   ├── 04-high-thinking-bot.json        # High Thinking Bot
│   ├── 05-testing-bot.json              # Testing Bot
│   ├── 06-advanced-rag-bot.json         # Advanced RAG Bot
│   ├── 07-cloud-deployment-bot.json     # Cloud Deployment Bot
│   ├── 08-ml-pipeline-bot.json          # AI/ML Pipeline Bot
│   └── 09-n8n-manager-bot.json          # n8n Manager Bot
├── docker-compose.yml                   # Unified Docker orchestration
├── Dockerfile                           # Container definition for Control Center
├── Makefile                             # Convenient make commands
├── requirements.txt                     # Python dependencies
├── .env.example                         # Environment configuration template
├── DESKTOP_SETUP_GUIDE.md               # Detailed setup guide
├── start-all.sh                         # Infrastructure startup script
└── README.md                            # Project documentation
```

---

## 🔗 Webhook Endpoints

### Core Bots
| Bot | Endpoint | Methods |
|-----|----------|---------|
| Coding Assistant | `/webhook/coding-assistant` | POST |
| RAG Ingest | `/webhook/rag-ingest` | POST |
| RAG Query | `/webhook/rag-query` | POST |
| System Design | `/webhook/system-design` | POST |
| High Thinking | `/webhook/high-thinking` | POST |
| Test Generate | `/webhook/testing/generate` | POST |
| Test Execute | `/webhook/testing/execute` | POST |
| Test Coverage | `/webhook/testing/coverage` | POST |

### Advanced Bots
| Bot | Endpoints | Methods |
|-----|-----------|---------|
| Advanced RAG | `/webhook/rag/ingest`, `/webhook/rag/query`, `/webhook/rag/agentic`, `/webhook/rag/evaluate` | POST |
| Cloud Deploy | `/webhook/cloud/terraform/generate`, `/webhook/cloud/k8s/generate`, `/webhook/cloud/helm/generate`, `/webhook/cloud/deploy`, `/webhook/cloud/validate`, `/webhook/cloud/cost-estimate` | POST |
| ML Pipeline | `/webhook/ml/data/prepare`, `/webhook/ml/train`, `/webhook/ml/evaluate`, `/webhook/ml/deploy`, `/webhook/ml/monitor`, `/webhook/ml/experiment` | POST |
| n8n Manager | `/webhook/n8n/deploy`, `/webhook/n8n/backup`, `/webhook/n8n/restore`, `/webhook/n8n/scale`, `/webhook/n8n/monitor`, `/webhook/n8n/migrate` | POST |

---

## 💡 Usage Examples

### Core Bots

#### Generate Code
```bash
curl -X POST http://localhost:5678/webhook/coding-assistant \
  -H "Content-Type: application/json" \
  -d '{"task": "generate a GraphQL resolver for User with DataLoader", "language": "typescript"}'
```

#### Query Documents
```bash
curl -X POST http://localhost:5678/webhook/rag-query \
  -H "Content-Type: application/json" \
  -d '{"query": "How does authentication work?", "topK": 5}'
```

#### Design Architecture
```bash
curl -X POST http://localhost:5678/webhook/system-design \
  -H "Content-Type: application/json" \
  -d '{"task": "design", "requirements": "Event-driven order processing for 10k orders/min", "scale": "high"}'
```

#### Deep Reasoning
```bash
curl -X POST http://localhost:5678/webhook/high-thinking \
  -H "Content-Type: application/json" \
  -d '{"problem": "Build vs buy for analytics platform", "mode": "deep"}'
```

#### Generate & Run Tests
```bash
curl -X POST http://localhost:5678/webhook/testing/generate \
  -H "Content-Type: application/json" \
  -d '{"code": "export const add = (a, b) => a + b", "language": "typescript", "testTypes": ["unit", "edge"]}'
```

### Advanced Bots

#### Advanced RAG - Hybrid Search + Reranking
```bash
curl -X POST http://localhost:5678/webhook/rag/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Explain the authentication flow", "topK": 10, "hybridWeight": 0.5, "rerank": true, "searchMode": "hybrid"}'
```

#### Advanced RAG - Agentic Multi-step
```bash
curl -X POST http://localhost:5678/webhook/rag/agentic \
  -H "Content-Type: application/json" \
  -d '{"query": "Compare authentication methods across all docs", "maxSteps": 5, "tools": ["search_hybrid", "fetch_document"]}'
```

#### Cloud Deployment - Generate Terraform
```bash
curl -X POST http://localhost:5678/webhook/cloud/terraform/generate \
  -H "Content-Type: application/json" \
  -d '{"requirements": "EKS cluster with RDS, ElastiCache, ALB for microservices", "cloudProvider": "aws", "environment": "production", "modules": ["vpc", "eks", "rds", "elasticache", "alb"]}'
```

#### Cloud Deployment - Generate K8s Manifests
```bash
curl -X POST http://localhost:5678/webhook/cloud/k8s/generate \
  -H "Content-Type: application/json" \
  -d '{"appName": "my-api", "image": "myorg/my-api:v1.2.3", "replicas": 5, "autoscaling": {"enabled": true, "minReplicas": 3, "maxReplicas": 20}}'
```

#### Cloud Deployment - Cost Estimation
```bash
curl -X POST http://localhost:5678/webhook/cloud/cost-estimate \
  -H "Content-Type: application/json" \
  -d '{"terraformPlan": "...", "cloudProvider": "aws", "region": "us-east-1"}'
```

#### ML Pipeline - Train Model
```bash
curl -X POST http://localhost:5678/webhook/ml/train \
  -H "Content-Type: application/json" \
  -d '{"task": "classification", "framework": "lightning", "modelArch": "Transformer", "hyperparameters": {"lr": 3e-4, "batch_size": 64, "epochs": 50}, "tracking": "mlflow"}'
```

#### ML Pipeline - Deploy to K8s (KServe)
```bash
curl -X POST http://localhost:5678/webhook/ml/deploy \
  -H "Content-Type: application/json" \
  -d '{"modelPath": "s3://my-bucket/models/best.ckpt", "targetPlatform": "k8s", "servingFramework": "fastapi", "optimization": "onnx", "scaling": {"minReplicas": 2, "maxReplicas": 20}}'
```

#### ML Pipeline - Run Hyperparameter Optimization
```bash
curl -X POST http://localhost:5678/webhook/ml/experiment \
  -H "Content-Type: application/json" \
  -d '{"experimentName": "transformer-hpo", "searchSpace": {"lr": {"type": "loguniform", "low": 1e-5, "high": 1e-2}, "hidden_dim": {"type": "choice", "values": [256, 512, 1024]}}, "algorithm": "tpe", "maxTrials": 100}'
```

#### n8n Manager - Deploy to Kubernetes
```bash
curl -X POST http://localhost:5678/webhook/n8n/deploy \
  -H "Content-Type: application/json" \
  -d '{"mode": "kubernetes", "version": "latest", "domain": "n8n.mycompany.com", "replicas": 3, "database": {"type": "postgresql", "pool": 20}, "queue": {"type": "redis", "mode": "cluster"}}'
```

#### n8n Manager - Backup Configuration
```bash
curl -X POST http://localhost:5678/webhook/n8n/backup \
  -H "Content-Type: application/json" \
  -d '{"schedule": "0 2 * * *", "retention": "daily:30,weekly:12,monthly:12", "destinations": ["s3", "gcs"], "encryption": true}'
```

#### n8n Manager - Auto-scaling with KEDA
```bash
curl -X POST http://localhost:5678/webhook/n8n/scale \
  -H "Content-Type: application/json" \
  -d '{"currentReplicas": 3, "trigger": "queue_depth", "kedaConfig": {"scaler": "redis", "queueName": "bull:default", "targetItemsPerPod": 50}}'
```

---

## ⚙️ Requirements

| Tool | Version | Install |
|------|---------|---------|
| Node.js | 20+ | `brew install node@20` |
| Docker | Latest | Docker Desktop |
| Qdrant | Via Docker | Auto-started |
| n8n | Latest | `npm install -g n8n` |
| kubectl | Latest | For K8s deployments |
| helm | Latest | For Helm charts |
| terraform | Latest | For IaC |

**API Keys**: **NVIDIA API Key only** (get from https://build.nvidia.com/)
- Model: `nvidia/nemotron-3-ultra-550b-a55b` (chat/completion)
- Embeddings: `nvidia/nv-embedqa-e5-v5` (for RAG)
- Base URL: `https://integrate.api.nvidia.com/v1` (pre-configured)

**No OpenAI, Anthropic, HuggingFace, Ollama, or local models needed.**

---

## 🎯 Model Configuration

| Task | Model | Endpoint |
|------|-------|----------|
| **All Chat/Completion** | `nvidia/nemotron-3-ultra-550b-a55b` | `https://integrate.api.nvidia.com/v1` |
| **Embeddings (RAG)** | `nvidia/nv-embedqa-e5-v5` | `https://integrate.api.nvidia.com/v1` |

All workflows are pre-configured with these models and the NVIDIA base URL.

---

## 📚 Sources (10,000+ Workflows)

Workflows synthesized from patterns in:
- **n8nworkflows.xyz** - 11,317 workflows with API
- **enescingoz/awesome-n8n-templates** - 280+ curated (25k ⭐)
- **Zie619/n8n-workflows** - 4,343 workflows (56k ⭐)
- **n8n.io/workflows** - 12,125 community workflows
- **wassupjay/n8n-free-templates** - 200+ AI/ML focused (6k ⭐)

**Key patterns extracted from:**
- AI Research/RAG category (advanced RAG, agentic patterns)
- DevOps/Cloud category (Terraform, K8s, Helm, CI/CD)
- Database/Storage (vector DBs, hybrid search)
- OpenAI/LLMs (chain-of-thought, function calling, structured output)
- IT Operations (monitoring, scaling, backup)

---

## 🔧 Customization

### Add More Workflows
1. Browse sources above
2. Download `.json` files
3. Import in n8n → Workflows → Import from File
4. Configure credentials → Activate

### NVIDIA API Configuration
The OpenAI nodes in all workflows are configured with:
```json
{
  "type": "n8n-nodes-base.openAi",
  "baseUrl": "https://integrate.api.nvidia.com/v1",
  "credentials": { "openAiApi": "nvidiaApi" }
}
```

### Add Authentication
```bash
# n8n with basic auth
docker run -d -p 5678:5678 \
  -e N8N_BASIC_AUTH_ACTIVE=true \
  -e N8N_BASIC_AUTH_USER=admin \
  -e N8N_BASIC_AUTH_PASSWORD=securepass \
  n8nio/n8n
```

### Enable n8n API Access
```bash
# Set these for n8n Manager bot API operations
export N8N_API_URL=http://localhost:5678/api/v1
export N8N_API_KEY=your-api-key-from-n8n-settings
```

---

## 📄 License

MIT License - Free for personal and commercial use.

Workflows inspired by community templates (various MIT/Apache-2.0 licenses).

---

## 🙏 Credits

Built by combining the best patterns from the n8n community. Special thanks to:
- [enescingoz](https://github.com/enescingoz) for awesome-n8n-templates
- [Zie619](https://github.com/Zie619) for n8n-workflows
- [wassupjay](https://github.com/wassupjay) for n8n-free-templates
- n8n.io team for the platform
- All workflow contributors
- **NVIDIA for Nemotron 3 Ultra 550B** 🚀

---

**Happy Automating with Nemotron 3 Ultra!** 🎉

---

## 👤 Author & Architecture

**Abhi Gurjar**  
- Portfolio: [abhigurjar.vercel.app](https://abhigurjar.vercel.app)  
- GitHub: [@abhigurjar101](https://github.com/abhigurjar101)  
- LinkedIn: [Abhi Gurjar](https://in.linkedin.com/in/abhi-gurjar-b13067203)
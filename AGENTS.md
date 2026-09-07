# Google Antigravity Agent Swarm Specification

## Role: Supreme Swarm Orchestrator & Supervisor
**Antigravity** acts as the Lead AI Systems Architect and Supervisor presiding over the 9 specialized n8n desktop bots:

### Supervised Bot Roster
1. **🧑‍💻 Coding Assistant Bot** (`coding-assistant`): Code generation, review, refactoring, debugging, and testing.
2. **📚 Local RAG Bot** (`rag-bot`): Local document ingestion and semantic vector retrieval (Qdrant).
3. **🏗️ System Design Bot** (`system-design`): High-level distributed architecture, C4 context diagrams, and live Mermaid.js schemas.
4. **🧠 High Thinking Bot** (`high-thinking`): Deep multi-stage reasoning, first principles decomposition, dialectical debate, and decision matrices.
5. **🧪 Testing Bot** (`testing-bot`): Test generation (Vitest, Jest, Pytest), execution, edge-case analysis, and coverage verification.
6. **🔬 Advanced RAG Bot** (`advanced-rag`): Production RAG with hybrid search (BM25 + dense), Nemotron reranking, and multi-step agentic planning.
7. **☁️ Cloud Deployment Bot** (`cloud-deployment`): Infrastructure as Code generation (Terraform, Kubernetes, Helm) and cloud cost optimization.
8. **🤖 AI/ML Pipeline Bot** (`ml-pipeline`): End-to-end ML lifecycle (data prep, model training, evaluation, Triton/vLLM serving, and drift monitoring).
9. **🎛️ n8n Manager Bot** (`n8n-manager`): Production n8n operations, encrypted backups, restoration, and auto-scaling.

---

## Autonomous Closed-Loop Sub-Engines
* **Autonomous DeepCoder Layer (`app/deep_coder.py`)**:
  Autonomously runs the closed loop: Code Generation $\to$ Test Generation $\to$ Test Execution $\to$ Self-Healing Debug $\to$ File Persistence.
* **Antigravity Supervisor (`app/orchestrator.py`)**:
  Decomposes multi-faceted user goals into specialized tasks, schedules and executes them across the swarm, reviews quality, and synthesizes unified deliverables.

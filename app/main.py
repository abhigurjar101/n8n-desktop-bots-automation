"""
FastAPI Server & Webhook Gateway for n8n Desktop Bots Suite.
Provides local host runtime, Antigravity model guidance supervisor,
Full-Scale Qdrant RAG Engine, and Autonomous DeepCoder execution.
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Request, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.client import N8nBotClient
from app.agents import AGENT_REGISTRY, get_agent
from app.deep_coder import AutonomousDeepCoder
from app.rag_engine import rag_engine
from app.antigravity_brain import antigravity_supervisor
from app.jupyter_bridge import jupyter_bridge


app = FastAPI(
    title="n8n Desktop Bots & Antigravity Localhost Runtime",
    description="Control Center, Gateway, and Advanced Execution Engine for 9 Engineering Bots",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent.parent
WORKFLOWS_DIR = BASE_DIR / "workflows"
STATIC_DIR = Path(__file__).resolve().parent / "static"
WORKSPACE_DIR = BASE_DIR / "workspace"
WORKSPACE_DIR.mkdir(parents=True, exist_ok=True)

client = N8nBotClient()
deep_coder = AutonomousDeepCoder(str(WORKSPACE_DIR))

BOT_METADATA = [
    {
        "id": "coding-assistant",
        "name": "Coding Assistant",
        "emoji": "🧑‍💻",
        "category": "Core Development",
        "description": "Code generation, in-depth review, refactoring, debugging, and AST syntax validation.",
        "defaultWebhook": "coding-assistant",
        "supportedTasks": ["generate", "review", "refactor", "debug", "explain", "validate"],
    },
    {
        "id": "rag-bot",
        "name": "Local RAG Bot",
        "emoji": "📚",
        "category": "Core Development",
        "description": "Local document and codebase Q&A with Qdrant vector search.",
        "defaultWebhook": "rag-query",
        "supportedTasks": ["query", "ingest"],
    },
    {
        "id": "system-design",
        "name": "System Design Bot",
        "emoji": "🏗️",
        "category": "Core Development",
        "description": "Distributed systems architecture, C4 diagrams, ADRs, capacity planning, and live Mermaid diagrams.",
        "defaultWebhook": "system-design",
        "supportedTasks": ["design", "review", "capacity", "migration", "adr"],
    },
    {
        "id": "high-thinking",
        "name": "High Thinking & Reasoning",
        "emoji": "🧠",
        "category": "Core Development",
        "description": "Deep multi-stage reasoning, dialectical debate, first principles, and mental models.",
        "defaultWebhook": "high-thinking",
        "supportedTasks": ["deep", "chain", "debate", "mentalModels", "futures", "firstPrinciples"],
    },
    {
        "id": "testing-bot",
        "name": "Testing & QA Bot",
        "emoji": "🧪",
        "category": "Core Development",
        "description": "Test generation (Pytest, Vitest, Jest), sandbox execution, edge case validation, and coverage.",
        "defaultWebhook": "testing/generate",
        "supportedTasks": ["generate", "execute", "coverage"],
    },
    {
        "id": "advanced-rag",
        "name": "Advanced RAG Bot",
        "emoji": "🔬",
        "category": "Advanced Production",
        "description": "Production RAG with hybrid search (BM25 + dense Qdrant), neural reranking, and agentic planning.",
        "defaultWebhook": "rag/query",
        "supportedTasks": ["query", "agentic", "ingest", "evaluate"],
    },
    {
        "id": "cloud-deployment",
        "name": "Cloud Deployment Bot",
        "emoji": "☁️",
        "category": "Advanced Production",
        "description": "Infrastructure as Code: production Terraform modules, K8s manifests, Helm charts, and cloud cost estimation.",
        "defaultWebhook": "cloud/terraform/generate",
        "supportedTasks": ["terraform", "k8s", "helm", "deploy", "validate", "cost"],
    },
    {
        "id": "ml-pipeline",
        "name": "AI/ML Pipeline Bot",
        "emoji": "🤖",
        "category": "Advanced Production",
        "description": "End-to-end ML lifecycle: data preparation, training code, model evaluation, serving, and drift monitoring.",
        "defaultWebhook": "ml/data/prepare",
        "supportedTasks": ["prepare", "train", "evaluate", "deploy", "monitor"],
    },
    {
        "id": "n8n-manager",
        "name": "n8n Manager Bot",
        "emoji": "🎛️",
        "category": "Advanced Production",
        "description": "Self-hosted n8n operations: automated deployments, encrypted backups, restoration, and auto-scaling.",
        "defaultWebhook": "n8n/deploy",
        "supportedTasks": ["status", "deploy", "backup", "restore", "scale"],
    },
]


class ExecuteRequest(BaseModel):
    path: Optional[str] = None
    payload: Dict[str, Any]
    is_test: bool = False
    use_n8n: bool = False


class DeepCoderRequest(BaseModel):
    task: str
    language: str = "python"
    context: Optional[str] = None
    target_file: Optional[str] = None
    max_retries: int = 3
    auto_test: bool = True


class OrchestratorRequest(BaseModel):
    goal: str
    cloud_provider: str = "aws"
    language: str = "python"
    include_tests: bool = True
    include_iac: bool = True
    index_in_rag: bool = True


class RagQueryRequest(BaseModel):
    query: str
    collection: str = "desktop-docs"
    top_k: int = 5
    use_hybrid: bool = True
    use_rerank: bool = True


class RagIngestRequest(BaseModel):
    content: Optional[str] = None
    source_name: str = "document.txt"
    directory: Optional[str] = None
    collection: str = "desktop-docs"


class NvidiaKeyRequest(BaseModel):
    api_key: str


@app.get("/api/status")
async def get_status():
    """Returns connectivity status for n8n, Qdrant, and local execution engine."""
    services = await client.check_services_status()

    # Check local workflows count
    workflow_count = 0
    if WORKFLOWS_DIR.exists():
        workflow_count = len(list(WORKFLOWS_DIR.glob("*.json")))

    qdrant_cols = rag_engine.list_collections()

    return {
        "status": "online",
        "services": services,
        "localEngine": {
            "online": True,
            "agents_loaded": len(AGENT_REGISTRY),
            "embeddings_model": rag_engine.model_name,
            "qdrant_collections": len(qdrant_cols),
        },
        "workflowsCount": workflow_count,
        "workflowsDirectory": str(WORKFLOWS_DIR),
        "workspaceDirectory": str(WORKSPACE_DIR),
    }


@app.get("/api/bots")
async def list_bots():
    """Returns list of all 9 bots and their configurations."""
    return {"bots": BOT_METADATA}


@app.get("/api/workflows")
async def list_workflows():
    """List all workflow files on disk."""
    if not WORKFLOWS_DIR.exists():
        return {"workflows": []}

    workflows = []
    for f in sorted(WORKFLOWS_DIR.glob("*.json")):
        workflows.append({
            "filename": f.name,
            "sizeBytes": f.stat().st_size,
            "path": str(f),
        })
    return {"workflows": workflows}


@app.post("/api/bots/{bot_id}/execute")
async def execute_bot(bot_id: str, req: ExecuteRequest):
    """
    Executes a bot:
    1. If use_n8n is requested and n8n is running, routes to n8n webhook.
    2. Otherwise, executes immediately via the high-performance local agent.
    """
    agent = get_agent(bot_id)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Bot '{bot_id}' not found")

    # Check if user explicitly wants n8n and n8n is online
    if req.use_n8n:
        services = await client.check_services_status()
        if services["n8n"]["online"]:
            target_path = req.path or next((b["defaultWebhook"] for b in BOT_METADATA if b["id"] == bot_id), bot_id)
            n8n_result = await client.invoke_webhook(target_path, req.payload, is_test=req.is_test)
            if n8n_result.get("success"):
                return n8n_result

    # Execute with local advanced agent
    task = req.payload.get("task") or req.payload.get("requirements") or req.payload.get("problem") or req.payload.get("query") or "execute"
    result = await agent.execute(task=str(task), payload=req.payload)
    return result


@app.post("/api/deep-coder/automate")
async def run_autonomous_deep_coder(req: DeepCoderRequest):
    """Executes the closed-loop autonomous DeepCoder cycle with AST check and test runner."""
    result = await deep_coder.run(
        task=req.task,
        language=req.language,
        context=req.context,
        target_file=req.target_file,
        max_retries=req.max_retries,
        auto_test=req.auto_test,
    )
    return result


@app.post("/api/orchestrator/supervise")
async def run_antigravity_orchestrator(req: OrchestratorRequest):
    """Antigravity decomposes, coordinates, and supervises the multi-agent swarm."""
    result = await antigravity_supervisor.execute_goal(
        goal=req.goal,
        cloud_provider=req.cloud_provider,
        language=req.language,
        include_tests=req.include_tests,
        include_iac=req.include_iac,
        index_in_rag=req.index_in_rag,
    )
    return result


@app.post("/api/rag/query")
async def rag_query_endpoint(req: RagQueryRequest):
    """Executes full-scale hybrid search and neural reranking on Qdrant."""
    result = rag_engine.query_pipeline(
        collection_name=req.collection,
        query=req.query,
        top_k=req.top_k,
        use_hybrid=req.use_hybrid,
        use_rerank=req.use_rerank,
    )
    return result


@app.post("/api/rag/ingest")
async def rag_ingest_endpoint(req: RagIngestRequest):
    """Ingests raw text or directory into Qdrant collection."""
    if req.directory:
        res = rag_engine.ingest_directory(
            collection_name=req.collection,
            directory=req.directory,
        )
    elif req.content:
        res = rag_engine.ingest_text(
            collection_name=req.collection,
            content=req.content,
            source_name=req.source_name,
        )
    else:
        raise HTTPException(status_code=400, detail="Provide either 'content' or 'directory'")
    return res


@app.get("/api/rag/collections")
async def rag_list_collections():
    """Lists all Qdrant vector collections and stats."""
    collections = rag_engine.list_collections()
    return {"collections": collections}


@app.get("/api/credentials/status")
async def get_credentials_status():
    """Checks if external API keys (NVIDIA, etc.) are configured."""
    key = os.getenv("NVIDIA_API_KEY", "").strip()
    env_file = BASE_DIR / ".env"
    if not key and env_file.exists():
        content = env_file.read_text(encoding="utf-8")
        for line in content.splitlines():
            if line.startswith("NVIDIA_API_KEY="):
                key = line.split("=", 1)[1].strip()
                break

    has_key = bool(key and len(key) > 5)
    masked = f"{key[:7]}...{key[-4:]}" if has_key else None

    return {
        "nvidiaConfigured": has_key,
        "maskedKey": masked,
        "localEngineReady": True,
    }


@app.post("/api/credentials/nvidia")
async def save_nvidia_credentials(req: NvidiaKeyRequest):
    """Saves NVIDIA API key to .env."""
    raw_key = req.api_key.strip()
    if not raw_key:
        raise HTTPException(status_code=400, detail="API key cannot be empty")

    os.environ["NVIDIA_API_KEY"] = raw_key
    env_file = BASE_DIR / ".env"
    lines = []
    found = False
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            if line.startswith("NVIDIA_API_KEY="):
                lines.append(f"NVIDIA_API_KEY={raw_key}")
                found = True
            else:
                lines.append(line)

    if not found:
        lines.append(f"NVIDIA_API_KEY={raw_key}")

    env_file.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return {
        "success": True,
        "message": "NVIDIA API key saved and activated.",
        "maskedKey": f"{raw_key[:7]}...{raw_key[-4:]}",
    }


class JupyterTestAndPasteRequest(BaseModel):
    task_name: str
    code: str
    test_code: Optional[str] = None
    notebook_filename: str = "NEMI_Live_Notebook.ipynb"


@app.post("/api/jupyter/test-and-paste")
async def jupyter_test_and_paste_endpoint(req: JupyterTestAndPasteRequest):
    """Pre-tests code in live Jupyter IPython kernel and pastes to notebook if verified."""
    res = await asyncio.to_thread(
        jupyter_bridge.auto_test_and_paste,
        req.task_name,
        req.code,
        req.test_code,
        req.notebook_filename,
    )
    return res


@app.get("/api/jupyter/status")
async def jupyter_status_endpoint():
    """Checks Jupyter server connectivity and notebooks on Desktop."""
    url = jupyter_bridge.get_active_jupyter_url()
    desktop_notebooks = [f.name for f in jupyter_bridge.notebook_dir.glob("*.ipynb")]
    return {
        "active_url": url,
        "desktop_notebooks_count": len(desktop_notebooks),
        "notebooks": desktop_notebooks,
    }



# Mount Static Files (Web UI Dashboard)
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
async def root():
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return {"message": "n8n Desktop Bots & Antigravity Localhost API is running."}

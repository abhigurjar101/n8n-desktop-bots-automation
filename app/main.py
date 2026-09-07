"""
FastAPI Server & Webhook Gateway for n8n Desktop Bots Suite.
Serves the Control Center Dashboard and API endpoints.
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.client import N8nBotClient

app = FastAPI(
    title="n8n Desktop Bots Control Center",
    description="Control Center and Gateway for 9 NVIDIA Nemotron-powered n8n Bots",
    version="1.0.0",
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

client = N8nBotClient()

BOT_METADATA = [
    {
        "id": "coding-assistant",
        "name": "Coding Assistant",
        "emoji": "🧑‍💻",
        "category": "Core Development",
        "description": "Code generation, in-depth review, refactoring, debugging, and explanation.",
        "defaultWebhook": "coding-assistant",
        "supportedTasks": ["generate", "review", "refactor", "debug", "explain", "test"],
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
        "supportedTasks": ["design", "review", "capacity", "migration", "techSelection", "adr"],
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
        "description": "Test generation (Vitest, Jest, Pytest), execution, edge case validation, and coverage analysis.",
        "defaultWebhook": "testing/generate",
        "supportedTasks": ["generate", "execute", "coverage"],
    },
    {
        "id": "advanced-rag",
        "name": "Advanced RAG Bot",
        "emoji": "🔬",
        "category": "Advanced Production",
        "description": "Production RAG with hybrid search (BM25 + dense), Nemotron reranking, and multi-step agentic planning.",
        "defaultWebhook": "rag/query",
        "supportedTasks": ["query", "ingest", "agentic", "evaluate"],
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
        "supportedTasks": ["deploy", "backup", "restore", "scale"],
    },
]


class ExecuteRequest(BaseModel):
    path: Optional[str] = None
    payload: Dict[str, Any]
    is_test: bool = False


@app.get("/api/status")
async def get_status():
    """Returns connectivity status for n8n, Qdrant, and local workflows."""
    services = await client.check_services_status()

    # Check local workflows count
    workflow_count = 0
    if WORKFLOWS_DIR.exists():
        workflow_count = len(list(WORKFLOWS_DIR.glob("*.json")))

    return {
        "status": "online",
        "services": services,
        "workflowsCount": workflow_count,
        "workflowsDirectory": str(WORKFLOWS_DIR),
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
        workflows.append(
            {
                "filename": f.name,
                "sizeBytes": f.stat().st_size,
                "path": str(f),
            }
        )
    return {"workflows": workflows}


@app.post("/api/bots/{bot_id}/execute")
async def execute_bot(bot_id: str, req: ExecuteRequest):
    """Executes a specific bot webhook."""
    bot = next((b for b in BOT_METADATA if b["id"] == bot_id), None)
    if not bot:
        raise HTTPException(status_code=404, detail=f"Bot '{bot_id}' not found")

    target_path = req.path or bot["defaultWebhook"]
    result = await client.invoke_webhook(target_path, req.payload, is_test=req.is_test)
    return result


@app.post("/api/direct-webhook")
async def direct_webhook(req: ExecuteRequest):
    """Directly invokes any arbitrary n8n webhook path."""
    if not req.path:
        raise HTTPException(status_code=400, detail="Missing webhook 'path'")
    result = await client.invoke_webhook(req.path, req.payload, is_test=req.is_test)
    return result



from app.deep_coder import AutonomousDeepCoder
from app.orchestrator import AntigravityOrchestrator

deep_coder = AutonomousDeepCoder(client)
orchestrator = AntigravityOrchestrator(client)


class DeepCoderRequest(BaseModel):
    task: str
    language: str = "typescript"
    context: Optional[str] = None
    target_file: Optional[str] = None
    max_retries: int = 3
    auto_test: bool = True


class OrchestratorRequest(BaseModel):
    goal: str
    cloud_provider: str = "aws"
    language: str = "typescript"
    include_tests: bool = True
    include_iac: bool = True


class NvidiaKeyRequest(BaseModel):
    api_key: str


@app.post("/api/deep-coder/automate")
async def run_autonomous_deep_coder(req: DeepCoderRequest):
    """Executes the closed-loop autonomous DeepCoder cycle."""
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
    """Antigravity decomposes, coordinates, and supervises all 9 bots."""
    result = await orchestrator.execute_supervision_plan(
        goal=req.goal,
        cloud_provider=req.cloud_provider,
        language=req.language,
        include_tests=req.include_tests,
        include_iac=req.include_iac,
    )
    return result


@app.get("/api/credentials/status")
async def get_credentials_status():
    """Checks if the NVIDIA API Key is configured."""
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
    }


def sync_nvidia_key_to_n8n(api_key: str):
    """Syncs the NVIDIA API key directly to n8n credentials_entity."""
    import tempfile, subprocess, json
    cred_data = [
        {
            "id": "nvidia-cred-01",
            "name": "nvidiaApi",
            "type": "openAiApi",
            "data": {
                "apiKey": api_key,
                "url": "https://integrate.api.nvidia.com/v1",
            },
        }
    ]
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(cred_data, f)
        temp_path = f.name
    try:
        subprocess.run(
            ["n8n", "import:credentials", f"--input={temp_path}", "--projectId=ufv1yaTrP5HQnqhz"],
            capture_output=True, text=True, check=True
        )
    except Exception as e:
        print(f"Warning: Failed to auto-sync key to n8n: {e}")
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


@app.post("/api/credentials/nvidia")
async def save_nvidia_credentials(req: NvidiaKeyRequest):
    """Saves NVIDIA API key to .env and updates runtime environment and n8n credentials."""
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

    # Automatically sync key into n8n credentials entity
    sync_nvidia_key_to_n8n(raw_key)

    return {
        "success": True,
        "message": "NVIDIA API key saved and activated in Antigravity Orchestrator runtime and n8n credentials",
        "maskedKey": f"{raw_key[:7]}...{raw_key[-4:]}",
    }


# Mount Static Files (Web UI Dashboard)
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
async def root():
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return {"message": "n8n Desktop Bots API is running. UI assets not found."}


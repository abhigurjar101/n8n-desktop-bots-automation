"""
Python Client for n8n Desktop Bots Suite.
Provides high-level bindings to dispatch tasks to all 9 n8n bot webhooks.
"""

import os
from typing import Any, Dict, List, Optional, Union
import httpx


class N8nBotClient:
    """Client for interacting with n8n Desktop Bots webhooks."""

    def __init__(
        self,
        n8n_base_url: Optional[str] = None,
        qdrant_url: Optional[str] = None,
        timeout: float = 180.0,
    ):
        self.n8n_base_url = (n8n_base_url or os.getenv("N8N_BASE_URL", "http://localhost:5678")).rstrip("/")
        self.qdrant_url = (qdrant_url or os.getenv("QDRANT_URL", "http://localhost:6333")).rstrip("/")
        self.timeout = timeout

    async def check_services_status(self) -> Dict[str, Any]:
        """Check availability of n8n and Qdrant services."""
        status = {
            "n8n": {"online": False, "url": self.n8n_base_url, "details": None},
            "qdrant": {"online": False, "url": self.qdrant_url, "details": None},
        }

        async with httpx.AsyncClient(timeout=3.0) as client:
            # Check n8n
            try:
                resp = await client.get(f"{self.n8n_base_url}/healthz")
                if resp.status_code == 200:
                    status["n8n"]["online"] = True
                    status["n8n"]["details"] = "Healthy"
                else:
                    resp_root = await client.get(self.n8n_base_url)
                    status["n8n"]["online"] = resp_root.status_code < 500
                    status["n8n"]["details"] = f"HTTP {resp_root.status_code}"
            except Exception as e:
                status["n8n"]["details"] = str(e)

            # Check Qdrant
            try:
                resp = await client.get(f"{self.qdrant_url}/healthz")
                if resp.status_code == 200:
                    status["qdrant"]["online"] = True
                    status["qdrant"]["details"] = "Healthy"
                else:
                    resp_root = await client.get(self.qdrant_url)
                    status["qdrant"]["online"] = resp_root.status_code < 500
                    status["qdrant"]["details"] = f"HTTP {resp_root.status_code}"
            except Exception as e:
                status["qdrant"]["details"] = str(e)

        return status

    async def invoke_webhook(
        self,
        path: str,
        payload: Dict[str, Any],
        is_test: bool = False,
    ) -> Dict[str, Any]:
        """
        Send a POST request to an n8n webhook.
        If the standard webhook path (/webhook/...) is 404, optionally tries /webhook-test/...
        """
        clean_path = path.lstrip("/")
        webhook_prefix = "webhook-test" if is_test else "webhook"
        url = f"{self.n8n_base_url}/{webhook_prefix}/{clean_path}"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(url, json=payload)
                if response.status_code == 404 and not is_test:
                    # Try test webhook fallback
                    test_url = f"{self.n8n_base_url}/webhook-test/{clean_path}"
                    test_response = await client.post(test_url, json=payload)
                    if test_response.status_code == 200:
                        try:
                            return test_response.json()
                        except Exception:
                            return {"success": True, "raw": test_response.text}

                response.raise_for_status()
                try:
                    return response.json()
                except Exception:
                    return {"success": True, "raw": response.text}
            except httpx.ConnectError:
                return {
                    "success": False,
                    "error": f"Cannot connect to n8n at {self.n8n_base_url}. Ensure n8n is running (./start-all.sh).",
                }
            except httpx.HTTPStatusError as e:
                return {
                    "success": False,
                    "status_code": e.response.status_code,
                    "error": f"n8n webhook returned HTTP {e.response.status_code}: {e.response.text}",
                }
            except Exception as e:
                return {"success": False, "error": str(e)}

    # 1. Coding Assistant
    async def coding_assistant(
        self,
        task: str,
        code: Optional[str] = None,
        language: str = "typescript",
        context: Optional[str] = None,
        model: Optional[str] = None,
    ) -> Dict[str, Any]:
        payload = {
            "task": task,
            "code": code or "",
            "language": language,
            "context": context or "",
            "model": model or "nvidia/nemotron-3-ultra-550b-a55b",
        }
        return await self.invoke_webhook("coding-assistant", payload)

    # 2. Local Document RAG Bot
    async def rag_ingest(
        self,
        files: Optional[List[str]] = None,
        directory: Optional[str] = None,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ) -> Dict[str, Any]:
        payload = {
            "files": files or [],
            "directory": directory,
            "chunkSize": chunk_size,
            "chunkOverlap": chunk_overlap,
        }
        return await self.invoke_webhook("rag-ingest", payload)

    async def rag_query(
        self,
        query: str,
        collection: str = "desktop-docs",
        top_k: int = 5,
    ) -> Dict[str, Any]:
        payload = {"query": query, "collection": collection, "topK": top_k}
        return await self.invoke_webhook("rag-query", payload)

    # 3. System Design Bot
    async def system_design(
        self,
        requirements: str,
        task: str = "design",
        scale: Optional[str] = None,
        tech_stack: Optional[str] = None,
        constraints: Optional[str] = None,
        existing_architecture: Optional[str] = None,
        model: Optional[str] = None,
    ) -> Dict[str, Any]:
        payload = {
            "task": task,
            "requirements": requirements,
            "scale": scale or "10k RPS, 1M MAU",
            "techStack": tech_stack or "Open",
            "constraints": constraints or "None",
            "existingArchitecture": existing_architecture or "Greenfield",
            "model": model or "nvidia/nemotron-3-ultra-550b-a55b",
        }
        return await self.invoke_webhook("system-design", payload)

    # 4. High Thinking / Reasoning Bot
    async def high_thinking(
        self,
        problem: str,
        mode: str = "deep",
        context: Optional[str] = None,
        constraints: Optional[str] = None,
        iterations: int = 3,
        temperature: float = 0.3,
        model: Optional[str] = None,
    ) -> Dict[str, Any]:
        payload = {
            "problem": problem,
            "mode": mode,
            "context": context or "",
            "constraints": constraints or "",
            "iterations": iterations,
            "temperature": temperature,
            "model": model or "nvidia/nemotron-3-ultra-550b-a55b",
        }
        return await self.invoke_webhook("high-thinking", payload)

    # 5. Testing Bot
    async def testing_generate(
        self,
        code: str,
        language: str = "typescript",
        framework: Optional[str] = None,
        test_types: Optional[List[str]] = None,
        coverage_target: int = 80,
        existing_tests: Optional[str] = None,
        model: Optional[str] = None,
    ) -> Dict[str, Any]:
        payload = {
            "code": code,
            "language": language,
            "framework": framework or ("pytest" if language == "python" else "vitest"),
            "testTypes": test_types or ["unit", "integration", "edge"],
            "coverageTarget": coverage_target,
            "existingTests": existing_tests or "",
            "model": model or "nvidia/nemotron-3-ultra-550b-a55b",
        }
        return await self.invoke_webhook("testing/generate", payload)

    # 6. Advanced RAG Bot
    async def advanced_rag(
        self,
        action: str,  # 'ingest', 'query', 'agentic', 'evaluate'
        payload: Dict[str, Any],
    ) -> Dict[str, Any]:
        return await self.invoke_webhook(f"rag/{action}", payload)

    # 7. Cloud Deployment Bot
    async def cloud_deployment(
        self,
        subpath: str,  # 'terraform/generate', 'k8s/generate', 'helm/generate', 'cost-estimate', etc.
        payload: Dict[str, Any],
    ) -> Dict[str, Any]:
        return await self.invoke_webhook(f"cloud/{subpath}", payload)

    # 8. AI/ML Pipeline Bot
    async def ml_pipeline(
        self,
        subpath: str,  # 'data/prepare', 'train', 'evaluate', 'deploy', 'monitor'
        payload: Dict[str, Any],
    ) -> Dict[str, Any]:
        return await self.invoke_webhook(f"ml/{subpath}", payload)

    # 9. n8n Manager Bot
    async def n8n_manager(
        self,
        action: str,  # 'deploy', 'backup', 'restore', 'scale'
        payload: Dict[str, Any],
    ) -> Dict[str, Any]:
        return await self.invoke_webhook(f"n8n/{action}", payload)

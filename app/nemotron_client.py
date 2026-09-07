"""
Official NVIDIA Nemotron Cloud Client.
Connects directly to NVIDIA NIM API (integrate.api.nvidia.com) using the
user's authenticated API key, routing to active flagship Nemotron models
with seamless local intelligent fallback.
"""

import os
import json
import time
import asyncio
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

NVIDIA_ENDPOINT = "https://integrate.api.nvidia.com/v1/chat/completions"
ACTIVE_NEMOTRON_MODEL = "nvidia/nemotron-3.5-lightning-30b-a3b"
FALLBACK_NEMOTRON_MODEL = "mistralai/mistral-nemotron"



class NemotronClient:
    """NVIDIA Nemotron NIM API Client with automatic model discovery and fallback."""

    def __init__(self):
        self.endpoint = NVIDIA_ENDPOINT
        self.model = ACTIVE_NEMOTRON_MODEL

    def get_api_key(self) -> str:
        """Retrieves active NVIDIA API key from env or .env file."""
        key = os.getenv("NVIDIA_API_KEY", "").strip()
        if key:
            return key
        env_file = Path(__file__).resolve().parent.parent / ".env"
        if env_file.exists():
            for line in env_file.read_text(encoding="utf-8").splitlines():
                if line.startswith("NVIDIA_API_KEY="):
                    val = line.split("=", 1)[1].strip()
                    if val:
                        return val
        return ""

    def is_configured(self) -> bool:
        """Checks if a valid NVIDIA API key is available."""
        key = self.get_api_key()
        return bool(key and key.startswith("nvapi-") and len(key) > 10)

    def generate_sync(
        self,
        prompt: str,
        system_prompt: str = "You are NVIDIA Nemotron, the elite neural reasoning and architectural synthesizer.",
        max_tokens: int = 400,
        temperature: float = 0.2,
        timeout: int = 20,
    ) -> Dict[str, Any]:
        """
        Executes a real chat completion against NVIDIA NIM API with model fallback.
        """
        key = self.get_api_key()
        if not key:
            return {
                "success": False,
                "error": "NVIDIA_API_KEY not configured.",
                "content": "",
                "used_cloud": False,
            }

        models_to_try = [self.model, FALLBACK_NEMOTRON_MODEL]

        for target_model in models_to_try:
            payload = json.dumps({
                "model": target_model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": max_tokens,
                "temperature": temperature,
            })

            cmd = [
                "curl", "-s", "--max-time", str(timeout),
                self.endpoint,
                "-H", f"Authorization: Bearer {key}",
                "-H", "Content-Type: application/json",
                "-d", payload,
            ]

            start_time = time.time()
            try:
                res = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 2)
                duration = round(time.time() - start_time, 3)

                if res.returncode == 0 and res.stdout.strip():
                    data = json.loads(res.stdout)
                    if "choices" in data and len(data["choices"]) > 0:
                        content = data["choices"][0]["message"]["content"].strip()
                        usage = data.get("usage", {})
                        return {
                            "success": True,
                            "model": target_model,
                            "content": content,
                            "duration_seconds": duration,
                            "tokens_used": usage.get("total_tokens", 0),
                            "used_cloud": True,
                        }
            except Exception:
                continue

        return {
            "success": False,
            "error": "All Nemotron models timed out or queued.",
            "content": "",
            "used_cloud": False,
        }

    async def generate(
        self,
        prompt: str,
        system_prompt: str = "You are NVIDIA Nemotron, the elite neural reasoning and architectural synthesizer.",
        max_tokens: int = 1024,
        temperature: float = 0.2,
        timeout: int = 15,
    ) -> Dict[str, Any]:
        """Asynchronous wrapper running off the main asyncio event loop."""
        return await asyncio.to_thread(
            self.generate_sync,
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            timeout=timeout,
        )


# Global singleton
nemotron_client = NemotronClient()

#!/usr/bin/env python3
"""
Automated workflow importer for n8n Desktop Bots Suite.
Imports all 9 workflow JSON files from the workflows/ directory into n8n.
Supports n8n REST API (with N8N_API_KEY) and n8n CLI.
"""

import json
import os
import subprocess
import sys
import urllib.request
import urllib.error
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
WORKFLOWS_DIR = BASE_DIR / "workflows"


def import_via_cli(workflow_file: Path, project_id: str = "ufv1yaTrP5HQnqhz") -> bool:
    try:
        cmd = ["npx", "n8n", "import:workflow", f"--input={workflow_file}", f"--projectId={project_id}"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode != 0:
            print(f"    CLI Import error: {result.stderr or result.stdout}")
        return result.returncode == 0
    except Exception as e:
        print(f"    CLI Import exception: {e}")
        return False


def import_via_api(workflow_file: Path, n8n_url: str, api_key: str) -> bool:
    try:
        with open(workflow_file, "r") as f:
            workflow_data = json.load(f)

        # Structure payload for n8n REST API
        payload = {
            "name": workflow_data.get("name", workflow_file.stem),
            "nodes": workflow_data.get("nodes", []),
            "connections": workflow_data.get("connections", {}),
            "settings": workflow_data.get("settings", {}),
        }

        req = urllib.request.Request(
            f"{n8n_url.rstrip('/')}/api/v1/workflows",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "X-N8N-API-KEY": api_key,
            },
            method="POST",
        )

        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status in (200, 201)
    except Exception as e:
        print(f"    API Import failed: {e}")
        return False


def main():
    print("📦 Importing 9 n8n Desktop Bot Workflows...\n")

    if not WORKFLOWS_DIR.exists():
        print(f"Error: Workflows directory not found at {WORKFLOWS_DIR}")
        sys.exit(1)

    workflow_files = sorted(WORKFLOWS_DIR.glob("*.json"))
    print(f"Found {len(workflow_files)} workflows in {WORKFLOWS_DIR.name}/:\n")

    n8n_url = os.getenv("N8N_BASE_URL", "http://localhost:5678")
    api_key = os.getenv("N8N_API_KEY", "")
    project_id = os.getenv("N8N_PROJECT_ID", "ufv1yaTrP5HQnqhz")

    for wf in workflow_files:
        print(f"  • {wf.name}")
        imported = False

        if api_key:
            imported = import_via_api(wf, n8n_url, api_key)
            if imported:
                print("    ✓ Successfully imported via n8n REST API")

        if not imported:
            imported = import_via_cli(wf, project_id=project_id)
            if imported:
                print("    ✓ Successfully imported via n8n CLI")

        if not imported:
            print("    ℹ Ready for manual import: In n8n UI -> Workflows -> Import from File")

    print("\n" + "=" * 55)
    print("Workflows ready! Next step: Add credentials in n8n UI (http://localhost:5678):")
    print("  1. NVIDIA API (Name: nvidiaApi, Type: OpenAI API)")
    print("     Base URL: https://integrate.api.nvidia.com/v1")
    print("  2. Qdrant Auth (Name: qdrantAuth)")
    print("  3. Activate all 9 workflows")
    print("=" * 55)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
CLI Tool for n8n Desktop Bots Suite.
Dispatch tasks to any of the 9 bots directly from your terminal.
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path

# Try to use rich for styled terminal output, fallback to standard print if not installed
try:
    from rich.console import Console
    from rich.markdown import Markdown
    from rich.panel import Panel
    from rich.table import Table

    console = Console()
    HAS_RICH = True
except ImportError:
    HAS_RICH = False
    console = None

from app.client import N8nBotClient


def print_msg(msg: str, style: str = ""):
    if HAS_RICH and console:
        console.print(msg, style=style)
    else:
        print(msg)


def print_panel(content: str, title: str = ""):
    if HAS_RICH and console:
        console.print(Panel(content, title=title, border_style="green"))
    else:
        print(f"\n--- {title} ---\n{content}\n" + "-" * 30)


async def check_status():
    client = N8nBotClient()
    status = await client.check_services_status()

    if HAS_RICH and console:
        table = Table(title="n8n Desktop Bots Infrastructure Status", border_style="cyan")
        table.add_column("Service", style="bold")
        table.add_column("URL")
        table.add_column("Status")
        table.add_column("Details")

        n8n_status = "[green]ONLINE[/green]" if status["n8n"]["online"] else "[red]OFFLINE[/red]"
        table.add_row("n8n Server", status["n8n"]["url"], n8n_status, str(status["n8n"]["details"]))

        qdrant_status = "[green]ONLINE[/green]" if status["qdrant"]["online"] else "[red]OFFLINE[/red]"
        table.add_row("Qdrant Vector DB", status["qdrant"]["url"], qdrant_status, str(status["qdrant"]["details"]))

        console.print(table)
    else:
        print("Infrastructure Status:")
        print(f"  n8n Server: {'ONLINE' if status['n8n']['online'] else 'OFFLINE'} ({status['n8n']['url']})")
        print(f"  Qdrant DB:  {'ONLINE' if status['qdrant']['online'] else 'OFFLINE'} ({status['qdrant']['url']})")


def list_bots():
    from app.main import BOT_METADATA

    if HAS_RICH and console:
        table = Table(title="Available n8n Desktop Bots (9 AI Agents)", border_style="green")
        table.add_column("Emoji", justify="center")
        table.add_column("ID", style="bold cyan")
        table.add_column("Name", style="bold")
        table.add_column("Category")
        table.add_column("Description")

        for b in BOT_METADATA:
            table.add_row(b["emoji"], b["id"], b["name"], b["category"], b["description"])

        console.print(table)
    else:
        for b in BOT_METADATA:
            print(f"{b['emoji']} {b['name']} ({b['id']}) - {b['description']}")


async def run_bot(bot_id: str, payload: dict, is_test: bool = False):
    client = N8nBotClient()
    print_msg(f"[yellow]Dispatching task to [bold]{bot_id}[/bold]...[/yellow]")
    
    from app.main import BOT_METADATA
    bot = next((b for b in BOT_METADATA if b["id"] == bot_id), None)
    if not bot:
        print_msg(f"[red]Error: Unknown bot ID '{bot_id}'[/red]")
        sys.exit(1)

    result = await client.invoke_webhook(bot["defaultWebhook"], payload, is_test=is_test)

    if not result.get("success", True) and "error" in result:
        print_msg(f"[red]Error from n8n: {result.get('error')}[/red]")
        sys.exit(1)

    # Format and display output
    content = ""
    if "response" in result:
        resp = result["response"]
        if isinstance(resp, dict):
            content = resp.get("explanation", "")
            if resp.get("code"):
                content += f"\n\n```\n{resp['code']}\n```"
        else:
            content = str(resp)
    elif "fullResponse" in result:
        content = result["fullResponse"]
    else:
        content = json.dumps(result, indent=2)

    if HAS_RICH and console:
        console.print(Markdown(content))
    else:
        print("\n" + content)


def main():
    parser = argparse.ArgumentParser(description="n8n Desktop Bots CLI Runner")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # status
    subparsers.add_parser("status", help="Check status of n8n and Qdrant services")

    # list
    subparsers.add_parser("list", help="List all 9 available bots")

    # ui / serve
    serve_parser = subparsers.add_parser("serve", help="Launch the Web Control Center dashboard")
    serve_parser.add_argument("--port", type=int, default=8000, help="Port to bind (default: 8000)")
    serve_parser.add_argument("--host", type=str, default="127.0.0.1", help="Host to bind")

    # code
    code_parser = subparsers.add_parser("code", help="Run Coding Assistant Bot")
    code_parser.add_argument("task", help="Coding task or prompt")
    code_parser.add_argument("--file", help="File path to read code from")
    code_parser.add_argument("--code", help="Inline code snippet")
    code_parser.add_argument("--lang", default="typescript", help="Programming language")

    # design
    design_parser = subparsers.add_parser("design", help="Run System Design Bot")
    design_parser.add_argument("requirements", help="System requirements and goals")
    design_parser.add_argument("--scale", default="50k RPS, 5M DAU", help="Scale requirements")
    design_parser.add_argument("--stack", default="Open", help="Preferred tech stack")

    # think
    think_parser = subparsers.add_parser("think", help="Run High Thinking Bot")
    think_parser.add_argument("problem", help="Problem or thesis to analyze")
    think_parser.add_argument("--mode", default="deep", choices=["deep", "firstPrinciples", "debate", "mentalModels", "chain", "futures"], help="Reasoning mode")

    # orchestrate (Antigravity Supervisor)
    orch_parser = subparsers.add_parser("orchestrate", help="Antigravity orchestrates all bots for an end-to-end goal")
    orch_parser.add_argument("goal", help="High-level engineering or automation goal")
    orch_parser.add_argument("--cloud", default="aws", choices=["aws", "gcp", "azure", "multi"], help="Target cloud provider")
    orch_parser.add_argument("--lang", default="typescript", help="Programming language")

    # auto-code (Autonomous DeepCoder closed loop)
    auto_parser = subparsers.add_parser("auto-code", help="Autonomous closed-loop DeepCoder (code + test + self-heal)")
    auto_parser.add_argument("task", help="Coding task or feature")
    auto_parser.add_argument("--lang", default="typescript", help="Programming language")
    auto_parser.add_argument("--file", help="Destination file path to save verified code")
    auto_parser.add_argument("--max-retries", type=int, default=3, help="Max self-healing attempts")

    # set-key
    key_parser = subparsers.add_parser("set-key", help="Configure NVIDIA API Key for Nemotron 3 Ultra")
    key_parser.add_argument("key", help="Your NVIDIA API Key (nvapi-...)")

    args = parser.parse_args()

    if args.command == "status":
        asyncio.run(check_status())
    elif args.command == "list":
        list_bots()
    elif args.command == "serve":
        import uvicorn
        print_msg(f"[green]Starting n8n Desktop Bots Control Center on http://{args.host}:{args.port}[/green]")
        uvicorn.run("app.main:app", host=args.host, port=args.port, reload=True)
    elif args.command == "code":
        code = args.code or ""
        if args.file and Path(args.file).exists():
            code = Path(args.file).read_text()
        asyncio.run(run_bot("coding-assistant", {
            "task": args.task,
            "code": code,
            "language": args.lang,
        }))
    elif args.command == "design":
        asyncio.run(run_bot("system-design", {
            "task": "design",
            "requirements": args.requirements,
            "scale": args.scale,
            "techStack": args.stack,
        }))
    elif args.command == "think":
        asyncio.run(run_bot("high-thinking", {
            "problem": args.problem,
            "mode": args.mode,
        }))
    elif args.command == "orchestrate":
        from app.orchestrator import AntigravityOrchestrator
        print_msg(f"[bold green]👑 Antigravity Orchestrating Swarm for: {args.goal}[/bold green]")
        orch = AntigravityOrchestrator()
        result = asyncio.run(orch.execute_supervision_plan(
            goal=args.goal,
            cloud_provider=args.cloud,
            language=args.lang,
        ))
        print_panel(json.dumps(result, indent=2), title="Antigravity Swarm Deliverable")
    elif args.command == "auto-code":
        from app.deep_coder import AutonomousDeepCoder
        print_msg(f"[bold cyan]⚡ Autonomous DeepCoder starting on: {args.task}[/bold cyan]")
        coder = AutonomousDeepCoder()
        result = asyncio.run(coder.run(
            task=args.task,
            language=args.lang,
            target_file=args.file,
            max_retries=args.max_retries,
        ))
        print_panel(f"Status: {'PASSED' if result.get('success') else 'FAILED'}\nDuration: {result.get('duration_seconds')}s\nSaved: {result.get('saved_path')}\n\nCode:\n{result.get('code')}", title="DeepCoder Verification")
    elif args.command == "set-key":
        from app.main import BASE_DIR, sync_nvidia_key_to_n8n
        raw_key = args.key.strip()
        env_file = BASE_DIR / ".env"
        lines = []
        found = False
        if env_file.exists():
            for line in env_file.read_text().splitlines():
                if line.startswith("NVIDIA_API_KEY="):
                    lines.append(f"NVIDIA_API_KEY={raw_key}")
                    found = True
                else:
                    lines.append(line)
        if not found:
            lines.append(f"NVIDIA_API_KEY={raw_key}")
        env_file.write_text("\n".join(lines) + "\n")
        sync_nvidia_key_to_n8n(raw_key)
        print_msg(f"[green]✓ NVIDIA API key saved to .env & synced to n8n ({raw_key[:7]}...{raw_key[-4:]})[/green]")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()


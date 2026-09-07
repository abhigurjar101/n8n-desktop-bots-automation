#!/usr/bin/env python3
"""
Quick health check script for n8n Desktop Bots infrastructure.
Tests n8n (5678) and Qdrant (6333) ports and HTTP responses.
"""

import sys
import socket
import urllib.request
import urllib.error


def check_port(host: str, port: int, timeout: float = 2.0) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def check_http(url: str, timeout: float = 3.0) -> tuple[bool, str]:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "HealthCheck/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return True, f"HTTP {response.status}"
    except urllib.error.HTTPError as e:
        return True, f"HTTP {e.code}"
    except Exception as e:
        return False, str(e)


def main():
    print("🔍 Checking n8n Desktop Bots Infrastructure...\n")

    # 1. Check n8n
    n8n_port_open = check_port("127.0.0.1", 5678)
    if n8n_port_open:
        ok, detail = check_http("http://127.0.0.1:5678/")
        print(f"  [✓] n8n Server: ONLINE on port 5678 ({detail})")
    else:
        print("  [✗] n8n Server: OFFLINE on port 5678")
        print("      Run ./start-all.sh or docker-compose up to start.")

    # 2. Check Qdrant
    qdrant_port_open = check_port("127.0.0.1", 6333)
    if qdrant_port_open:
        ok, detail = check_http("http://127.0.0.1:6333/healthz")
        print(f"  [✓] Qdrant Vector DB: ONLINE on port 6333 ({detail})")
    else:
        print("  [✗] Qdrant Vector DB: OFFLINE on port 6333")
        print("      Run docker start qdrant or docker-compose up.")

    print("\n" + "=" * 50)
    if n8n_port_open and qdrant_port_open:
        print("🎉 All systems ready! Launch the UI with: make ui (or python cli.py serve)")
        sys.exit(0)
    else:
        print("⚠️  Some services are not running. Run: ./start-all.sh")
        sys.exit(1)


if __name__ == "__main__":
    main()

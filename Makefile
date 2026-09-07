# n8n Desktop Bots Suite Makefile

.PHONY: help install start ui status import docker-start docker-stop test

help:
	@echo "n8n Desktop Bots Suite - Available Commands:"
	@echo "  make install       Install Python dependencies"
	@echo "  make start         Start infrastructure (Qdrant + n8n via start-all.sh)"
	@echo "  make ui            Launch the Control Center Web Dashboard on http://localhost:8000"
	@echo "  make status        Check connectivity of n8n and Qdrant services"
	@echo "  make import        Import all 9 workflows into n8n"
	@echo "  make docker-start  Launch full stack with Docker Compose"
	@echo "  make docker-stop   Stop Docker Compose containers"

install:
	pip install -r requirements.txt

start:
	./start-all.sh

ui:
	python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

status:
	python scripts/health_check.py

import:
	python scripts/import_workflows.py

docker-start:
	docker compose up -d

docker-stop:
	docker compose down

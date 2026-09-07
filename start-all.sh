#!/bin/bash
# n8n Desktop Bots - Start All Infrastructure (NVIDIA Nemotron 3 Ultra Only)

set -e

echo "🚀 Starting n8n Desktop Bots Infrastructure..."

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Function to check if container exists and start it
start_qdrant() {
    echo -e "${YELLOW}Starting Qdrant (vector database)...${NC}"
    if docker ps -a --format '{{.Names}}' | grep -q '^qdrant$'; then
        docker start qdrant
    else
        docker run -d --name qdrant \
            -p 6333:6333 -p 6334:6334 \
            -v "$(pwd)/qdrant_data:/qdrant/storage" \
            qdrant/qdrant
    fi
    echo -e "${GREEN}✓ Qdrant running on http://localhost:6333${NC}"
}

# Function to start n8n
start_n8n() {
    echo -e "${YELLOW}Starting n8n...${NC}"
    echo -e "${GREEN}n8n will be available at http://localhost:5678${NC}"
    echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"
    npx n8n
}

# Main
echo "=========================================="
echo -e "  ${BLUE}n8n Desktop Bots - 9 AI Agents Ready${NC}"
echo -e "  ${GREEN}Powered by NVIDIA Nemotron 3 Ultra 550B${NC}"
echo "=========================================="
echo ""
echo -e "${GREEN}Core Development Bots:${NC}"
echo "  1. 🧑‍💻 Coding Assistant"
echo "  2. 📚 RAG Bot"
echo "  3. 🏗️  System Design Bot"
echo "  4. 🧠 High Thinking Bot"
echo "  5. 🧪 Testing Bot"
echo ""
echo -e "${GREEN}Advanced Production Bots:${NC}"
echo "  6. 🔬 Advanced RAG Bot (hybrid search, reranking, agentic)"
echo "  7. ☁️  Cloud Deployment Bot (Terraform, K8s, Helm, CI/CD)"
echo "  8. 🤖 AI/ML Pipeline Bot (train, eval, deploy, monitor, HPO)"
echo "  9. 🎛️  n8n Manager Bot (deploy, backup, scale, monitor, migrate)"
echo ""

# Check prerequisites
command -v docker >/dev/null 2>&1 || { echo -e "${RED}Docker not installed. Install Docker Desktop first.${NC}"; exit 1; }
command -v node >/dev/null 2>&1 || { echo -e "${RED}Node.js not installed. Install Node.js 20+ first.${NC}"; exit 1; }

# Optional tools (warn but don't fail)
command -v kubectl >/dev/null 2>&1 || echo -e "${YELLOW}⚠ kubectl not found - Cloud Deployment & n8n Manager bots need it for K8s${NC}"
command -v helm >/dev/null 2>&1 || echo -e "${YELLOW}⚠ helm not found - Cloud Deployment bot needs it for Helm charts${NC}"
command -v terraform >/dev/null 2>&1 || echo -e "${YELLOW}⚠ terraform not found - Cloud Deployment bot needs it for IaC${NC}"

start_qdrant

echo ""
echo "=========================================="
echo -e "  ${GREEN}Infrastructure Ready!${NC}"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Open http://localhost:5678"
echo "2. Import workflows from ./workflows/ (9 files)"
echo "3. Add credentials in n8n:"
echo "   - NVIDIA API (required) - Type: OpenAI API, Name: nvidiaApi"
echo "     Base URL: https://integrate.api.nvidia.com/v1 (pre-configured)"
echo "   - Qdrant HTTP Header Auth (for RAG bots) - Name: qdrantAuth"
echo "   - n8n API Key (for n8n Manager bot) - Name: n8nApiAuth"
echo "4. Activate all 9 workflows"
echo ""
echo "Models (pre-configured in workflows):"
echo "  - Chat/Completion: nvidia/nemotron-3-ultra-550b-a55b"
echo "  - Embeddings: nvidia/nv-embedqa-e5-v5"
echo ""

start_n8n
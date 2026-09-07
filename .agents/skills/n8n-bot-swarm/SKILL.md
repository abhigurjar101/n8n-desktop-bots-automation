---
name: n8n-bot-swarm
description: >-
  Antigravity Supreme Bot Swarm Orchestrator. Coordinates, supervises, and executes
  tasks across all 9 n8n desktop bots (Coding Assistant, RAG, System Design,
  High Thinking, Testing, Advanced RAG, Cloud Deployment, AI/ML Pipeline, n8n Manager).
---

# Antigravity Bot Swarm Orchestrator Skill

This skill equips Antigravity to act as the Supreme Orchestrator over the 9 desktop AI agents.

## Supervision Flow
When receiving a complex development or automation request:
1. **Analyze & Decompose**:
   - Determine which specialized bots to summon.
   - Plan dependencies (Architecture $\to$ Code $\to$ Test $\to$ Deploy).
2. **Dispatch & Supervise**:
   - Invoke bots via the local Gateway (`http://localhost:8000/api/bots/{bot_id}/execute` or Python client).
   - Validate intermediate deliverables.
   - Trigger the **Autonomous DeepCoder** loop if coding tasks require self-healing test verification.
3. **Synthesize & Deliver**:
   - Assemble full architecture diagrams (Mermaid), production code, unit tests, and infrastructure manifests.

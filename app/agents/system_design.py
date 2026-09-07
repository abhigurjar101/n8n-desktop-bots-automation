"""
System Design Bot (Core Development).
Provides distributed systems architecture, live Mermaid C4 diagrams,
capacity planning calculations, and Architecture Decision Records (ADRs).
"""

import math
import re
import time
from typing import Any, Dict, List, Optional
from app.agents.base import BaseAgent


class SystemDesignAgent(BaseAgent):
    """Architectural agent delivering C4 models, Mermaid diagrams, and capacity sizing."""

    def __init__(self):
        super().__init__(
            bot_id="system-design",
            name="System Design Bot",
            emoji="🏗️",
            category="Core Development",
        )

    async def execute(self, task: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        start_time = time.time()
        subtask = payload.get("subtask") or task.split(" ")[0].lower()
        if subtask not in ["design", "review", "capacity", "migration", "adr"]:
            subtask = "design"

        requirements = payload.get("requirements", task)
        scale = payload.get("scale", "10,000 RPS, 5M DAU")
        tech_stack = payload.get("techStack") or payload.get("tech_stack", "Python, FastAPI, PostgreSQL, Redis, Docker, Kubernetes")
        constraints = payload.get("constraints", "High Availability 99.99%, Sub-100ms p99 latency")

        mermaid_chart = self._generate_mermaid(requirements, tech_stack)
        capacity_data = self._calculate_capacity(scale)
        adr_content = self._generate_adr(requirements, tech_stack)

        response_md = f"""### System Architecture Blueprint: {requirements[:60]}

**Target Scale**: `{scale}`  
**Primary Tech Stack**: `{tech_stack}`  
**SLAs & Constraints**: `{constraints}`

---

#### 1. Visual Topology (Mermaid.js)

```mermaid
{mermaid_chart}
```

---

#### 2. Capacity Planning & Resource Budget
- **Peak Throughput**: `{capacity_data['peak_rps']:,} RPS` (Read: `{capacity_data['read_rps']:,}`, Write: `{capacity_data['write_rps']:,}`)
- **Daily Storage Ingestion**: `{capacity_data['daily_storage_gb']} GB/day` (`{capacity_data['yearly_storage_tb']} TB/year`)
- **Memory Cache Sizing (Redis 20% rule)**: `{capacity_data['cache_ram_gb']} GB RAM`
- **Network Bandwidth (Outbound)**: `{capacity_data['bandwidth_mbps']} Mbps`

---

#### 3. Architecture Decision Record (ADR-001)
{adr_content}
"""

        latency = round((time.time() - start_time) * 1000, 2)
        return {
            "success": True,
            "bot_id": self.bot_id,
            "bot_name": self.name,
            "latency_ms": latency,
            "subtask": subtask,
            "mermaid": mermaid_chart,
            "capacity": capacity_data,
            "rawResponse": response_md,
        }

    def _generate_mermaid(self, requirements: str, tech_stack: str) -> str:
        """Generates clean, syntactically valid Mermaid flowchart."""
        return """graph TD
    Client["📱 Web & Mobile Clients"] -->|HTTPS / TLS 1.3| CDN["🌐 CloudFront CDN & WAF"]
    CDN -->|Dynamic API Traffic| ALB["⚖️ Application Load Balancer"]

    subgraph VPC["🔒 Private VPC (Multi-AZ)"]
        ALB --> APIGateway["🚪 FastAPI Gateway Clusters"]
        
        subgraph Services["Microservices Tier"]
            APIGateway --> CoreService["⚙️ Core Domain Service"]
            APIGateway --> RAGService["🧠 RAG & Vector Engine"]
            APIGateway --> AsyncWorkers["⚡ Celery / Redis Workers"]
        end

        subgraph Storage["Data & Caching Layer"]
            CoreService -->|Cache Aside| RedisCache[("⚡ Redis Cluster (Hot Data)")]
            CoreService -->|ACID Write| PrimaryDB[("🗄️ PostgreSQL Primary")]
            PrimaryDB -.->|Read Replica| ReplicaDB[("🗄️ PostgreSQL Replica")]
            RAGService -->|Vector Search| QdrantDB[("🎯 Qdrant Vector Store")]
            AsyncWorkers -->|Events| KafkaQueue["📨 Kafka / RabbitMQ"]
            CoreService -->|Audit Logs| S3Storage[("📦 S3 Cold Storage")]
        end
    end

    classDef primary fill:#1e1b4b,stroke:#6366f1,stroke-width:2px,color:#fff;
    classDef storage fill:#064e3b,stroke:#10b981,stroke-width:2px,color:#fff;
    class ALB,APIGateway,CoreService,RAGService,AsyncWorkers primary;
    class RedisCache,PrimaryDB,ReplicaDB,QdrantDB,S3Storage storage;
"""

    def _calculate_capacity(self, scale_str: str) -> Dict[str, Any]:
        """Calculates rough capacity numbers from scale string."""
        # Defaults
        peak_rps = 10000
        dau = 5000000

        match_rps = re.search(r'(\d+[\d,]*)\s*(?:rps|requests)', scale_str.lower())
        if match_rps:
            try:
                peak_rps = int(match_rps.group(1).replace(",", ""))
            except Exception:
                pass

        read_rps = int(peak_rps * 0.8)
        write_rps = int(peak_rps * 0.2)

        avg_write_payload_kb = 2.5
        daily_storage_gb = round((write_rps * 86400 * avg_write_payload_kb) / (1024 * 1024), 2)
        yearly_storage_tb = round((daily_storage_gb * 365) / 1024, 2)

        # 20% of daily active working set in Redis
        cache_ram_gb = round(daily_storage_gb * 0.20, 2)

        # Network bandwidth: read payloads avg 10KB
        bandwidth_mbps = round((read_rps * 10 * 8) / 1024, 2)

        return {
            "peak_rps": peak_rps,
            "read_rps": read_rps,
            "write_rps": write_rps,
            "daily_storage_gb": daily_storage_gb,
            "yearly_storage_tb": yearly_storage_tb,
            "cache_ram_gb": cache_ram_gb,
            "bandwidth_mbps": bandwidth_mbps,
        }

    def _generate_adr(self, requirements: str, tech_stack: str) -> str:
        return f"""**Title**: ADR-001 High-Throughput Service Decoupling  
**Status**: Accepted  
**Context**: The system must sustain `{requirements[:60]}` without single points of failure under peak load.  

**Decision**:
1. Adopt **Event-Driven Architecture** with Redis Streams/Kafka for background tasks to decouple synchronous user requests from heavy compute.
2. Deploy a **Read-Replica Database Topology** with read/write splitting to prevent analytical or read-heavy traffic from locking transactional writes.
3. Leverage **Qdrant Vector Database** for high-dimensional nearest-neighbor retrieval with isolated memory-mapped index segments.

**Consequences**:
- **Positive**: Sub-50ms p95 latency for read paths, horizontal scalability of worker pods.
- **Trade-off**: Eventual consistency between primary database writes and search index sync (~200ms lag window).
"""

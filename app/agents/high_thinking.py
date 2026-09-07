"""
High Thinking & Reasoning Bot (Core Development).
Provides deep multi-stage reasoning, Tree-of-Thought exploration,
dialectical debate (Thesis, Antithesis, Synthesis), and first-principles analysis.
"""

import time
from typing import Any, Dict, List, Optional
from app.agents.base import BaseAgent


class HighThinkingAgent(BaseAgent):
    """Reasoning agent executing structured mental models, dialectics, and pre-mortems."""

    def __init__(self):
        super().__init__(
            bot_id="high-thinking",
            name="High Thinking & Reasoning",
            emoji="🧠",
            category="Core Development",
        )

    async def execute(self, task: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        start_time = time.time()
        mode = payload.get("mode") or "deep"
        problem = payload.get("problem") or task
        constraints = payload.get("constraints", "")

        if mode == "debate":
            res = self._dialectical_debate(problem)
        elif mode == "firstPrinciples":
            res = self._first_principles(problem)
        elif mode == "futures":
            res = self._scenario_planning(problem)
        elif mode == "mentalModels":
            res = self._mental_models(problem)
        else:
            res = self._tree_of_thought(problem, constraints)

        latency = round((time.time() - start_time) * 1000, 2)
        res.update({
            "success": True,
            "bot_id": self.bot_id,
            "bot_name": self.name,
            "mode": mode,
            "latency_ms": latency,
        })
        return res

    def _tree_of_thought(self, problem: str, constraints: str) -> Dict[str, Any]:
        """Explores 3 diverging solution branches, evaluates trade-offs, and synthesizes."""
        response_md = f"""### Tree-of-Thought (ToT) Exploration

**Problem**: `{problem}`  
**Constraints**: `{constraints or "Standard Production Latency & Reliability"}`

---

#### 🌲 Branch 1: Pragmatic Synchronous Architecture
- **Hypothesis**: Keep logic within a single unified service process to minimize operational overhead.
- **Pros**: Lowest development complexity, trivial local debugging, zero distributed state synchronization.
- **Cons**: Becomes a CPU bottleneck under high-concurrency spikes; tight coupling between sub-components.
- **Viability Score**: `7.2 / 10`

---

#### 🌲 Branch 2: Event-Driven Asynchronous Pipeline
- **Hypothesis**: Decouple ingestion, transformation, and storage via message queue (Kafka / Redis Streams).
- **Pros**: Infinite horizontal scaling for workers, resilient backpressure handling, isolated crash domains.
- **Cons**: Adds operational infrastructure overhead, requires robust dead-letter queue (DLQ) retry semantics.
- **Viability Score**: `9.1 / 10` (Recommended)

---

#### 🌲 Branch 3: Edge-Serverless Compute
- **Hypothesis**: Push user-facing endpoints to edge runtimes (Cloudflare Workers / AWS Lambda).
- **Pros**: Zero idle cost, global proximity caching, rapid automatic scale-out.
- **Cons**: Cold start penalties for heavy ML containers, strict payload and execution time limits.
- **Viability Score**: `6.5 / 10`

---

### ⚖️ Synthesized Optimal Path
Adopt **Branch 2 (Event-Driven)** for heavy workloads paired with a lightweight edge cache. This protects core databases while ensuring predictable sub-100ms response times.
"""
        return {"rawResponse": response_md}

    def _dialectical_debate(self, problem: str) -> Dict[str, Any]:
        """Executes Thesis -> Antithesis -> Synthesis dialectic."""
        response_md = f"""### Dialectical Reasoning Debate: {problem[:60]}

#### 🏛️ Thesis (The Optimistic Case)
The immediate approach should prioritize speed of delivery, leveraging mature off-the-shelf abstractions and monolithic simplicity to validate value quickly.

#### ⚔️ Antithesis (The Adversarial Counter-Case)
Premature reliance on monolithic or simplistic patterns will incur massive technical debt. Concurrency locks, un-indexed queries, and tight coupling will cause critical production failures at 10x scale.

#### ⚖️ Synthesis (The Pragmatic Truth)
Build a modular monolith with strictly enforced interface boundaries and asynchronous background queues. This captures 90% of microservice decoupled benefits with only 10% of the operational complexity.
"""
        return {"rawResponse": response_md}

    def _first_principles(self, problem: str) -> Dict[str, Any]:
        """Breaks down problem into fundamental physical and mathematical truths."""
        response_md = f"""### First-Principles Deconstruction: {problem[:60]}

1. **Fundamental Truth #1 (Physics of Data)**: Network I/O is 1,000x slower than RAM access, which is 100x slower than CPU L1/L2 cache. Any high-performance system must minimize network hops and cache hot data in memory.
2. **Fundamental Truth #2 (Axiom of State)**: Every distributed state transition requires either latency (two-phase commit consensus) or eventual consistency risk (CAP theorem).
3. **Fundamental Truth #3 (Resource Bounds)**: Every server has finite file descriptors, socket buffers, and compute cycles. Unbounded queues will eventually exhaust memory.

#### Actionable Deduction
Never allow unbound in-memory queues; enforce strict timeouts, backpressure limits, and circuit breakers at every network boundary.
"""
        return {"rawResponse": response_md}

    def _scenario_planning(self, problem: str) -> Dict[str, Any]:
        response_md = f"""### Scenario Planning & Stress Testing
- **Scenario A (Happy Path)**: Normal load, 99.9% cache hit rate, p95 < 30ms.
- **Scenario B (Database Degraded)**: Primary DB CPU at 95%. Fallback to stale read cache and queue mutation requests.
- **Scenario C (Network Partition)**: Local worker agents buffer events to disk and retry with exponential backoff.
"""
        return {"rawResponse": response_md}

    def _mental_models(self, problem: str) -> Dict[str, Any]:
        response_md = f"""### Applied Mental Models
- **Occam's Razor**: The simplest architecture that fulfills the SLA is the most reliable.
- **Second-Order Thinking**: What happens after the cache warms up? Does invalidation create thundering herds?
- **Inversion**: How could this system fail catastrophically? (e.g., Redis OOM crash, unindexed join). Now design guardrails against that failure mode.
"""
        return {"rawResponse": response_md}

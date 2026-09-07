"""
Local RAG Bot (Core Development).
Provides document and codebase Q&A using live Qdrant vector database.
"""

from typing import Any, Dict, List, Optional
from app.agents.base import BaseAgent
from app.rag_engine import rag_engine


class RagBotAgent(BaseAgent):
    """Agent executing document ingestion and vector semantic search."""

    def __init__(self):
        super().__init__(
            bot_id="rag-bot",
            name="Local RAG Bot",
            emoji="📚",
            category="Core Development",
        )

    async def execute(self, task: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        subtask = payload.get("subtask") or task.split(" ")[0].lower()
        collection = payload.get("collection") or "desktop-docs"

        if subtask in ["ingest", "add", "index"]:
            content = payload.get("content") or payload.get("text", "")
            source = payload.get("source") or payload.get("filename", "user-input.txt")
            directory = payload.get("directory")

            if directory:
                res = rag_engine.ingest_directory(collection, directory)
            elif content:
                res = rag_engine.ingest_text(collection, content, source_name=source)
            else:
                return {
                    "success": False,
                    "error": "Provide either 'content' (string) or 'directory' (path) to ingest.",
                    "rawResponse": "❌ Ingestion failed: Missing content or directory parameter.",
                }

            summary_md = f"""### Ingestion Summary for Collection `{collection}`

- **Status**: `{"Success" if res.get("success") else "Failed"}`
- **Source**: `{source or directory}`
- **Chunks Ingested**: `{res.get("chunks_ingested", res.get("files_indexed", 0))}`
- **Total Tokens**: `{res.get("total_tokens", "N/A")}`

Data is indexed in local Qdrant vector store and ready for sub-second semantic retrieval.
"""
            res["rawResponse"] = summary_md
            return res

        # Default: Query mode
        query = payload.get("query") or task
        top_k = int(payload.get("topK") or payload.get("top_k", 5))

        res = rag_engine.query_pipeline(
            collection_name=collection,
            query=query,
            top_k=top_k,
            use_hybrid=True,
            use_rerank=True,
        )

        citations_md = "\n".join([
            f"- **{c['citation_id']}** `{c['source']}` ({c['lines']}) — Score: `{c['score']}`\n  > {c['snippet']}"
            for c in res.get("citations", [])
        ])

        formatted_md = f"""### Local RAG Query Result

**Query**: `{query}`  
**Collection**: `{collection}` | **Latency**: `{res.get('latency_ms', 0)} ms`

#### Answer
{res.get('answer', 'No answer synthesized.')}

#### Verified Citations
{citations_md if citations_md else "No citations returned."}
"""
        res["rawResponse"] = formatted_md
        return res

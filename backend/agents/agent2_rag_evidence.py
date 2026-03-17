import time
from backend.db.models import Agent2Response, EvidenceSource
from backend.rag.retriever import semantic_search


async def run(claim: str, context: str = "") -> dict:
    t0 = time.time()
    try:
        hits = semantic_search(claim, n_results=5)
        if not hits:
            return Agent2Response(error="no results").model_dump()

        top_score = hits[0]["score"] if hits else 0.5
        sources = [
            EvidenceSource(
                name=h.get("source", "DB"),
                url=h.get("url", "#"),
                snippet=h.get("text", "")[:200],
            )
            for h in hits[:3]
        ]

        return Agent2Response(
            p_true=float(top_score),
            sources=sources,
            rag_hits=len(hits),
            latency_ms=int((time.time() - t0) * 1000),
        ).model_dump()
    except Exception as e:
        return Agent2Response(error=str(e)).model_dump()

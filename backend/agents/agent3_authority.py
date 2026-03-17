import asyncio, time
from backend.db.models import Agent3Response, EvidenceSource
from backend.mcp.who_server import get_who_alerts, get_who_fact_sheet
from backend.mcp.fda_server import get_drug_label, search_drug_recalls


async def run(claim: str, claim_type: str = "general") -> dict:
    t0 = time.time()
    try:
        words = [w for w in claim.split() if len(w) > 4][:3]
        topic = " ".join(words)

        tasks = [get_who_fact_sheet(topic), get_who_alerts(topic)]
        if claim_type == "drug_interaction":
            tasks.append(get_drug_label(topic))

        results = await asyncio.gather(*tasks, return_exceptions=True)
        sources = []
        authority_found = False

        for r in results:
            if isinstance(r, Exception) or not isinstance(r, dict):
                continue
            if r.get("fact_sheet"):
                fs = r["fact_sheet"]
                sources.append(
                    EvidenceSource(
                        name=r.get("source", "WHO"),
                        url=fs.get("url", "#"),
                        snippet=fs.get("snippet", "")[:200],
                    )
                )
                authority_found = True
            if r.get("recalls"):
                for rec in r["recalls"][:1]:
                    sources.append(
                        EvidenceSource(
                            name="FDA Recalls",
                            url="https://www.fda.gov",
                            snippet=rec.get("reason", ""),
                        )
                    )

        p_true = 0.5 if authority_found else 0.4

        return Agent3Response(
            p_true=p_true,
            sources=sources,
            authority_found=authority_found,
            latency_ms=int((time.time() - t0) * 1000),
        ).model_dump()

    except Exception as e:
        return Agent3Response(error=str(e)).model_dump()

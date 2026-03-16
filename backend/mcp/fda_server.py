"""
MCP Tool: FDA drug recall and safety alert database.
Called by the agent when a claim involves a specific drug name,
supplement, or medical device.
"""
import aiohttp
from backend.config import FDA_API_BASE

async def search_drug_recalls(drug_name: str, limit: int = 3) -> dict:
    """
    Search FDA recall database for a specific drug.
    Returns recent recalls with reason, date, and classification.
    """
    try:
        url = f"{FDA_API_BASE}/drug/enforcement.json"
        params = {
            "search": f"product_description:{drug_name}",
            "limit":  limit
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=5) as r:
                if r.status == 404:
                    return {"source": "FDA", "recalls": []}
                data = await r.json()
                results = data.get("results", [])
                return {
                    "source": "FDA",
                    "recalls": [
                        {
                            "drug":           r.get("product_description", "")[:100],
                            "reason":         r.get("reason_for_recall", ""),
                            "classification": r.get("classification", ""),
                            "date":           r.get("recall_initiation_date", ""),
                            "status":         r.get("status", "")
                        }
                        for r in results
                    ]
                }
    except Exception as e:
        return {"source": "FDA", "recalls": [], "error": str(e)}


async def get_drug_label(drug_name: str) -> dict:
    """
    Fetch official FDA drug label — indications, warnings, contraindications.
    This is the ground truth for drug claims.
    """
    try:
        url = f"{FDA_API_BASE}/drug/label.json"
        params = {"search": f"openfda.brand_name:{drug_name}", "limit": 1}
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=5) as r:
                if r.status == 404:
                    return {"source": "FDA", "label": None}
                data = await r.json()
                results = data.get("results", [])
                if not results:
                    return {"source": "FDA", "label": None}
                label = results[0]
                return {
                    "source": "FDA",
                    "label": {
                        "indications":       " ".join(label.get("indications_and_usage", []))[:500],
                        "warnings":          " ".join(label.get("warnings", []))[:500],
                        "contraindications": " ".join(label.get("contraindications", []))[:500],
                        "drug_interactions": " ".join(label.get("drug_interactions", []))[:500],
                    }
                }
    except Exception as e:
        return {"source": "FDA", "label": None, "error": str(e)}

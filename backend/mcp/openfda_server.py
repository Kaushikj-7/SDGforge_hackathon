"""
MCP Tool: OpenFDA adverse event reports (FAERS database).
Called when the agent needs real-world drug safety evidence
beyond the official label.
"""
import aiohttp
from backend.config import FDA_API_BASE, OPENFDA_KEY

async def get_adverse_events(drug_name: str, limit: int = 5) -> dict:
    """
    Search FDA Adverse Event Reporting System for a drug.
    Returns top reported adverse events with counts.
    """
    try:
        url = f"{FDA_API_BASE}/drug/event.json"
        params = {
            "search": f"patient.drug.medicinalproduct:{drug_name}",
            "count":  "patient.reaction.reactionmeddrapt.exact",
            "limit":  limit
        }
        if OPENFDA_KEY:
            params["api_key"] = OPENFDA_KEY
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=5) as r:
                if r.status == 404:
                    return {"source": "OpenFDA", "adverse_events": []}
                data = await r.json()
                results = data.get("results", [])
                return {
                    "source": "OpenFDA",
                    "adverse_events": [
                        {"reaction": item.get("term"), "count": item.get("count")}
                        for item in results
                    ]
                }
    except Exception as e:
        return {"source": "OpenFDA", "adverse_events": [], "error": str(e)}

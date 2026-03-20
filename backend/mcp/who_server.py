"""
MCP Tool: WHO health alerts and disease outbreak feed.
Called by the agent when a claim involves infectious disease,
vaccination, or global health emergency topics.
"""
import aiohttp
from typing import Optional

WHO_DISEASE_FEED = "https://www.who.int/api/news/diseaseoutbreaknews"

async def get_who_alerts(topic: str, limit: int = 3) -> dict:
    """
    Search WHO outbreak news for claims related to a disease or health topic.
    Returns list of relevant alerts with title, date, and URL.
    """
    try:
        async with aiohttp.ClientSession() as session:
            params = {"sf_culture": "en", "$top": 20}
            async with session.get(WHO_DISEASE_FEED, params=params, timeout=5) as r:
                if r.status != 200:
                    return {"source": "WHO", "results": [], "error": f"HTTP {r.status}"}
                data = await r.json()
                items = data.get("value", [])
                # Filter by topic keyword
                filtered = [
                    {
                        "title": item.get("Title", ""),
                        "date":  item.get("PublicationDateAndTime", ""),
                        "url":   f"https://www.who.int{item.get('Url', '')}",
                        "summary": item.get("Summary", "")[:300]
                    }
                    for item in items
                    if topic.lower() in (item.get("Title", "") + item.get("Summary", "")).lower()
                ]
                return {"source": "WHO", "results": filtered[:limit]}
    except Exception as e:
        return {"source": "WHO", "results": [], "error": str(e)}


async def get_who_fact_sheet(topic: str) -> dict:
    """
    Fetch WHO fact sheet for common health topics (vaccines, diseases, nutrition).
    Uses WHO's public fact sheets API endpoint.
    """
    try:
        url = f"https://www.who.int/api/hubs/cms/features?sf_culture=en&$filter=substringof('{topic}',Title)"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=5) as r:
                if r.status != 200:
                    return {"source": "WHO", "fact_sheet": None}
                data = await r.json()
                items = data.get("value", [])
                if items:
                    return {
                        "source": "WHO",
                        "fact_sheet": {
                            "title":   items[0].get("Title"),
                            "url":     f"https://www.who.int{items[0].get('Url','')}",
                            "snippet": items[0].get("Summary", "")[:400]
                        }
                    }
                return {"source": "WHO", "fact_sheet": None}
    except Exception as e:
        return {"source": "WHO", "fact_sheet": None, "error": str(e)}

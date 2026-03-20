"""
Logs every verified claim as an SDG 3 impact event to the SDGforge platform.
Non-blocking — called with asyncio.create_task so it never slows down the response.
If SDGforge is unreachable, silently fails (no user impact).
"""
import aiohttp
from datetime import datetime, timezone
from backend.config import SDGFORGE_API, SDGFORGE_TOKEN

SDG_3_GOAL_ID = "3"   # Good Health and Well-Being

async def log_sdgforge_impact(verdict: dict):
    if not SDGFORGE_TOKEN or not SDGFORGE_API:
        return

    payload = {
        "sdg_goal":        SDG_3_GOAL_ID,
        "event_type":      "misinformation_check",
        "verdict":         verdict.get("verdict"),
        "risk_level":      verdict.get("risk_level"),
        "confidence":      verdict.get("confidence"),
        "claim_type":      verdict.get("claim_type"),
        "from_cache":      verdict.get("from_cache", False),
        "timestamp":       datetime.now(timezone.utc).isoformat(),
        "impact_metric":   "health_claims_verified"
    }

    try:
        async with aiohttp.ClientSession() as session:
            await session.post(
                f"{SDGFORGE_API}/api/impact/log",
                json=payload,
                headers={"Authorization": f"Bearer {SDGFORGE_TOKEN}"},
                timeout=aiohttp.ClientTimeout(total=3)
            )
    except Exception:
        pass   # silent fail — never interrupt the user flow

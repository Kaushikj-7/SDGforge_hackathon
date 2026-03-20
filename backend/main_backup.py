"""
FastAPI server — exposes the agent as an SSE streaming endpoint.
Run: uvicorn backend.main:app --reload --port 8000
"""
import json
import asyncio
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from backend.config import ALLOWED_ORIGINS
from backend.agent.orchestrator import run_agent
from backend.cache.claim_cache import init_cache
from backend.sdgforge_hook import log_sdgforge_impact

app = FastAPI(title="Health Fact Checker API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["POST", "GET"],
    allow_headers=["*"]
)

@app.on_event("startup")
async def startup():
    await init_cache()

class VerifyRequest(BaseModel):
    selected_text:       str
    surrounding_context: str = ""
    page_title:          str = ""
    page_url:            str = ""

@app.post("/verify/stream")
async def verify_stream(req: VerifyRequest):
    """
    SSE endpoint. Streams agent progress events then final verdict.
    The extension reads this with fetch + ReadableStream.
    """
    async def event_generator():
        async for event in run_agent(
            selected_text       = req.selected_text,
            surrounding_context = req.surrounding_context,
            page_title          = req.page_title,
            page_url            = req.page_url
        ):
            yield f"data: {json.dumps(event)}\n\n"
            await asyncio.sleep(0)   # yield control to event loop

            # After final verdict, fire SDGforge hook (non-blocking)
            if event.get("status") == "done":
                asyncio.create_task(
                    log_sdgforge_impact(event.get("verdict", {}))
                )

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"   # critical for Nginx — disables buffering
        }
    )

@app.get("/health")
async def health():
    return {"status": "ok", "version": "2.0.0"}

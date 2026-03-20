import asyncio, json, time

from fastapi import FastAPI, UploadFile, File

from fastapi.middleware.cors import CORSMiddleware

from fastapi.responses import StreamingResponse, JSONResponse

from pydantic import BaseModel

from backend.preprocessing.vision import extract_text_from_image
from backend.db.models import VerifyRequest

from backend.config import ALLOWED_ORIGINS

from backend.db.queries import init_db, get_cached, save_claim, get_dashboard_stats

from backend.preprocessing.language_detector import detect_language

from backend.preprocessing.translator import translate_to_english, translate_correction

from backend.preprocessing.claim_segmenter import segment_claims

from backend.rag.retriever import semantic_search

from backend.agents import (

    agent1_detector,

    agent2_rag_evidence,

    agent3_authority,

    agent4_correction,

    agent5_bias,

)

from backend.agents.aggregator import aggregate

from backend.sdgforge_hook import log_sdgforge_impact



app = FastAPI(title="TruthLens API", version="3.0.0")

app.add_middleware(

    CORSMiddleware,

    allow_origins=ALLOWED_ORIGINS,

    allow_methods=["*"],

    allow_headers=["*"],

)





@app.on_event("startup")

async def startup():

    init_db()





# ── Main streaming verify endpoint ────────────────────────────────────────

@app.post("/verify/stream")

async def verify_stream(req: VerifyRequest):

    async def generate():

        # Step 1: Language detection

        lang_info = detect_language(req.selected_text)

        lang_name = lang_info.get("name", "Unknown")

        lang_code = lang_info.get("code", "en")

        yield f"data: {json.dumps({'status': 'detecting', 'message': f'Language: {lang_name}', 'lang': lang_code, 'confidence_so_far': 0.05})}\n\n"



        # Step 2: Cache check

        cached = get_cached(req.selected_text)

        if cached:

            yield f"data: {json.dumps({'status': 'cache_hit', 'message': 'Returning verified result', 'confidence_so_far': 1.0})}\n\n"

            yield f"data: {json.dumps({'status': 'done', 'verdict': cached})}\n\n"

            return



        # Step 3: Translate to English if needed

        claim_en = await translate_to_english(req.selected_text, lang_info["code"])

        if lang_code != "en":
            yield f"data: {json.dumps({'status': 'translating', 'message': f'Translating from {lang_name}...', 'confidence_so_far': 0.15})}\n\n"

        # Step 4: RAG context enrichment
        rag_context = semantic_search(claim_en, n_results=3)
        yield f"data: {json.dumps({'status': 'searching', 'message': f'Found {len(rag_context)} relevant sources in knowledge base', 'confidence_so_far': 0.35})}\n\n"

        # Step 5: Run all 5 agents IN PARALLEL
        yield f"data: {json.dumps({'status': 'agents', 'message': 'Running 5 specialized agents in parallel...', 'confidence_so_far': 0.55})}\n\n"



        context_str = req.surrounding_context[:300]

        a1, a2, a3, a5 = await asyncio.gather(

            agent1_detector.run(claim_en, context_str),

            agent2_rag_evidence.run(claim_en, context_str),

            agent3_authority.run(claim_en, "general"),

            agent5_bias.run(claim_en, "UNCERTAIN", lang_info["code"]),

        )



        if a1.get("claim_type") and a1["claim_type"] != "general":

            a3 = await agent3_authority.run(claim_en, a1["claim_type"])



        # Agent 4 needs evidence from agents 2+3 to generate real correction

        all_evidence = a2.get("sources", []) + a3.get("sources", [])

        a4 = await agent4_correction.run(

            claim_en, all_evidence, a1.get("verdict", "UNCERTAIN"), lang_info["code"]

        )



        yield f"data: {json.dumps({'status': 'aggregating', 'message': 'Combining agent results...', 'confidence_so_far': 0.75})}\n\n"



        # Step 6: Bayesian aggregation

        result = aggregate(a1, a2, a3, a4, a5)

        yield f"data: {json.dumps({'status': 'translating', 'message': 'Generating easy Hindi & Kannada translations...', 'confidence_so_far': 0.90})}\n\n"
        hi_trans, kn_trans = await asyncio.gather(
            translate_correction(a4.get("correction", ""), [], "hi"),
            translate_correction(a4.get("correction", ""), [], "kn")
        )
        
        result["regional_translations"] = {
            "Hindi": hi_trans.get("correction", ""),
            "Kannada": kn_trans.get("correction", "")
        }


        result.update(

            {

                "original_lang": lang_info["code"],

                "lang_name": lang_info["name"],

                "claim_text": req.selected_text,

                "translated_text": claim_en if claim_en != req.selected_text else "",

                "page_url": req.page_url,

                "page_title": req.page_title,

            }

        )



        # Step 7: Save to DB

        save_claim(result)



        # Step 8: SDGforge hook (non-blocking)

        asyncio.create_task(log_sdgforge_impact(result))



        yield f"data: {json.dumps({'status': 'done', 'verdict': result})}\n\n"



    return StreamingResponse(

        generate(),

        media_type="text/event-stream",

        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},

    )





# ── Dashboard data endpoint ────────────────────────────────────────────────

@app.get("/api/dashboard")

async def dashboard():

    """Returns all live stats for the extension popup dashboard and web dashboard."""

    return JSONResponse(get_dashboard_stats())





# ── Multimodal image endpoint ──────────────────────────────────────────────

@app.post("/verify/image")
async def verify_image(file: UploadFile = File(...)):
    contents = await file.read()
    text = await extract_text_from_image(contents)
    if not text:
        return {"error": "Could not extract text"}
    return {"extracted_text": text}





@app.get("/health")

async def health():

    return {"status": "ok", "version": "3.0.0"}


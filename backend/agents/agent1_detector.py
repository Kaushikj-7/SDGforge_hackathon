"""
Agent 1: Groq Llama3-70B initial detection.
Fastest agent — sets the baseline P(true).
"""

import json, time
from groq import AsyncGroq
from backend.config import GROQ_API_KEY, GROQ_MODEL
from backend.db.models import Agent1Response

client = AsyncGroq(api_key=GROQ_API_KEY)

PROMPT = """You are a medical fact-checker. Analyze this health claim.

Claim: {claim}
Context: {context}

Respond ONLY with valid JSON:
{{
  "verdict": "TRUE|FALSE|MISLEADING|UNCERTAIN",
  "p_true": 0.0,
  "reasoning": "one sentence",
  "claim_type": "health_myth|drug_interaction|disease_claim|general"
}}

p_true is the probability (0.0-1.0) that the claim is factually correct."""


async def run(claim: str, context: str = "") -> dict:
    t0 = time.time()
    try:
        resp = await client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": PROMPT.format(claim=claim, context=context[:300]),
                }
            ],
            temperature=0.05,
            max_tokens=256,
            response_format={"type": "json_object"},
        )
        data = json.loads(resp.choices[0].message.content)
        return Agent1Response(
            p_true=float(data.get("p_true", 0.5)),
            verdict=data.get("verdict", "UNCERTAIN"),
            reasoning=data.get("reasoning", ""),
            claim_type=data.get("claim_type", "general"),
            latency_ms=int((time.time() - t0) * 1000),
        ).model_dump()
    except Exception as e:
        return Agent1Response(error=str(e)).model_dump()

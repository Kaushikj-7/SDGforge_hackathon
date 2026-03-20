"""
Agent 5: Bias + SDG 10 (Reduced Inequalities) framing agent.
"""

import json, time
from groq import AsyncGroq
from backend.config import GROQ_API_KEY, GROQ_MODEL
from backend.db.models import Agent5Response

client = AsyncGroq(api_key=GROQ_API_KEY)

PROMPT = """You are an expert in health equity and the UN Sustainable Development Goals.
Analyze this health claim through the lens of SDG 10 (Reduced Inequalities) and SDG 3 (Good Health).

Claim: "{claim}"
Language detected: {lang}
Verdict: {verdict}

Respond ONLY with JSON:
{{
  "vulnerable_populations": ["list of communities most harmed if this claim spreads"],
  "inequality_angle": "one sentence on digital divide / info inequality aspect",
  "sdg3_impact": "one sentence on health impact",
  "sdg10_impact": "one sentence on inequality impact",
  "bias_flags": ["any bias in the claim itself — e.g. targets specific ethnic group, exploits fear"],
  "non_english_risk": true/false
}}

non_english_risk: true if this claim is dangerous and the correction is primarily circulating online in English but the claim is in {lang}."""


async def run(claim: str, verdict: str, lang: str = "en") -> dict:
    t0 = time.time()
    try:
        resp = await client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": PROMPT.format(claim=claim, verdict=verdict, lang=lang),
                }
            ],
            temperature=0.1,
            max_tokens=400,
            response_format={"type": "json_object"},
        )
        data = json.loads(resp.choices[0].message.content)
        return Agent5Response(
            vulnerable_populations=data.get("vulnerable_populations", []),
            inequality_angle=data.get("inequality_angle", ""),
            sdg3_impact=data.get("sdg3_impact", ""),
            sdg10_impact=data.get("sdg10_impact", ""),
            bias_flags=data.get("bias_flags", []),
            non_english_risk=data.get("non_english_risk", False),
            latency_ms=int((time.time() - t0) * 1000),
        ).model_dump()
    except Exception as e:
        return Agent5Response(error=str(e)).model_dump()

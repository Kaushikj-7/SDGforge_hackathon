import json, time
from groq import AsyncGroq
from backend.config import GROQ_API_KEY, GROQ_MODEL
from backend.preprocessing.translator import translate_correction
from backend.db.models import Agent4Response, EvidenceSource

client = AsyncGroq(api_key=GROQ_API_KEY)

PROMPT = """You are a public health educator focusing on health equity. A user has highlighted this health claim.

Claim: "{claim}"
Evidence from trusted sources: {evidence_snippets}
Groq initial verdict: {groq_verdict}

First, deeply analyze the claim. Then write a CLEAR, COMPASSionate, and EXTREMELY SIMPLE correction for a general audience with an 8th-grade reading level. Break down any complex medical terms.

Respond ONLY with valid JSON:
{{
  "correction": "2-3 sentence correction in plain language",
  "explanation": "1 sentence technical explanation",
  "p_true_adjustment": 0.0,
  "sources": [
    {{"name": "source name", "url": "source url", "snippet": "key quote under 100 chars"}}
  ]
}}"""

async def run(claim: str, evidence: list, groq_verdict: str, target_lang: str = 'en') -> dict:
    t0 = time.time()
    try:
        evidence_text = '\n'.join([f'- {e.get("source", e.get("name", "Unknown"))}: {e.get("snippet", "")[:150]}' for e in evidence[:4]])
        
        resp = await client.chat.completions.create(model=GROQ_MODEL, messages=[{'role': 'user', 'content': PROMPT.format(claim=claim, evidence_snippets=evidence_text or 'None', groq_verdict=groq_verdict)}], temperature=0.3, max_tokens=500, response_format={'type': 'json_object'})
        data = json.loads(resp.choices[0].message.content)
        correction_en = data.get('correction', 'No correction available.')
        sources_models = [EvidenceSource(name=s.get('name', 'Unknown'), url=s.get('url', '#'), snippet=s.get('snippet', '')[:200]) for s in data.get('sources', [])]
        correction_out = (await translate_correction(correction_en, [], target_lang))['correction'] if target_lang != 'en' else correction_en
        return Agent4Response(correction=correction_out, correction_en=correction_en, explanation=data.get('explanation', ''), p_true_adjustment=float(data.get('p_true_adjustment', 0.0)), sources=sources_models, latency_ms=int((time.time() - t0) * 1000)).model_dump()
    except Exception as e:
        return Agent4Response(correction='Unable to generate correction. Please consult a healthcare professional.', correction_en='Unable to generate correction.', error=str(e)).model_dump()

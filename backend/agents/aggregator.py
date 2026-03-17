"""
Bayesian P(true) Aggregator Placeholder.
Combines probability estimates from all agents.
"""

WEIGHTS = {
    "groq_detector": 0.30,
    "rag_evidence": 0.35,
    "authority_check": 0.25,
    "gemini_correction": 0.10,
}

RISK_THRESHOLDS = [
    (0.80, "LOW"),
    (0.55, "MEDIUM"),
    (0.30, "HIGH"),
    (0.00, "CRITICAL"),
]

VERDICT_MAP = {
    "LOW": "LIKELY_TRUE",
    "MEDIUM": "UNCERTAIN",
    "HIGH": "LIKELY_FALSE",
    "CRITICAL": "FALSE",
}


def aggregate(
    agent1: dict, agent2: dict, agent3: dict, agent4: dict, agent5: dict
) -> dict:
    scores = {
        "groq_detector": agent1.get("p_true", 0.5),
        "rag_evidence": agent2.get("p_true", 0.5),
        "authority_check": agent3.get("p_true", 0.5),
        "gemini_correction": 0.5 + agent4.get("p_true_adjustment", 0.0),
    }

    # Weighted average
    total_weight = sum(WEIGHTS[k] for k in scores)
    p_true = sum(scores[k] * WEIGHTS[k] for k in scores) / total_weight
    p_true = max(0.01, min(0.99, p_true))

    risk_level = "CRITICAL"
    for threshold, level in RISK_THRESHOLDS:
        if p_true >= threshold:
            risk_level = level
            break

    verdict = VERDICT_MAP[risk_level]
    # Simple confidence: how far from the "uncertain" midpoint (0.5)
    # Scaled to 0.4-0.95 range for realism
    confidence = 0.4 + (abs(p_true - 0.5) * 1.1)
    confidence = max(0.4, min(0.95, confidence))

    all_sources = []
    seen_urls = set()
    for agent_data in [agent2, agent3, agent4]:
        for src in agent_data.get("sources", []):
            url = src.get("url", "")
            if url not in seen_urls and url:
                all_sources.append(src)
                seen_urls.add(url)

    return {
        "p_true": round(p_true, 3),
        "risk_level": risk_level,
        "verdict": verdict,
        "confidence": round(confidence, 3),
        "correction": agent4.get("correction", agent1.get("reasoning", "")),
        "explanation": agent4.get("explanation", ""),
        "sources": all_sources[:4],
        "bias_flags": agent5.get("bias_flags", []),
        "inequality_angle": agent5.get("inequality_angle", ""),
        "claim_type": agent1.get("claim_type", "general"),
        "agent_scores": scores,
    }

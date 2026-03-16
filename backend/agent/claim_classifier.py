"""
Lightweight claim classifier — runs before the agent loop
to decide the optimal tool sequence.
No LLM call needed here: pure keyword + regex heuristics.
Fast: ~1ms, no network.
"""
import re

DRUG_KEYWORDS = [
    "mg", "dosage", "dose", "tablet", "capsule", "injection",
    "interaction", "prescription", "overdose", "side effect",
    "contraindication", "warfarin", "aspirin", "ibuprofen",
    "metformin", "statin", "antibiotic", "paracetamol", "acetaminophen"
]

DISEASE_KEYWORDS = [
    "cancer", "diabetes", "covid", "hiv", "aids", "malaria",
    "tuberculosis", "alzheimer", "stroke", "heart attack",
    "hypertension", "depression", "autism", "vaccine", "immunity"
]

MYTH_PATTERNS = [
    r"cures?\s+\w+",
    r"prevents?\s+\w+",
    r"causes?\s+\w+",
    r"always\s+(safe|healthy|harmful|dangerous)",
    r"never\s+(causes?|leads? to)",
    r"100%\s+(effective|safe|proven)",
    r"doctors\s+(don't want|hate)",
    r"natural\s+\w+\s+(is|are)\s+(better|safer|healthier)"
]

def classify_claim(text: str) -> dict:
    """
    Returns:
        claim_type: "drug_interaction" | "disease_claim" | "health_myth" | "general"
        priority_tools: list of tool names in recommended call order
        drug_names: list of detected drug names (if any)
    """
    text_lower = text.lower()

    is_drug   = any(kw in text_lower for kw in DRUG_KEYWORDS)
    is_disease = any(kw in text_lower for kw in DISEASE_KEYWORDS)
    is_myth   = any(re.search(p, text_lower) for p in MYTH_PATTERNS)

    if is_drug:
        return {
            "claim_type":    "drug_interaction",
            "priority_tools": ["fda_drug_label", "phase5_drugbank", "phase4_detect", "phase6_correct"],
            "drug_names":    _extract_drug_names(text)
        }
    elif is_myth:
        return {
            "claim_type":    "health_myth",
            "priority_tools": ["phase4_detect", "phase5_pubmed", "who_fact_sheet", "phase6_correct"],
            "drug_names":    []
        }
    elif is_disease:
        return {
            "claim_type":    "disease_claim",
            "priority_tools": ["phase4_detect", "who_alerts", "phase5_pubmed", "phase6_correct"],
            "drug_names":    []
        }
    else:
        return {
            "claim_type":    "general",
            "priority_tools": ["phase4_detect", "phase5_pubmed", "phase6_correct"],
            "drug_names":    []
        }

def _extract_drug_names(text: str) -> list:
    """
    Simple capitalized noun extraction for drug name detection.
    Production version should use a medical NER model.
    """
    words = text.split()
    return [w.strip(".,;()") for w in words if w[0].isupper() and len(w) > 3]

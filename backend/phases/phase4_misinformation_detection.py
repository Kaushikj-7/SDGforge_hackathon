#!/usr/bin/env python3
"""
Phase 4: Misinformation Detection
Multi-Agent Debate Matrix (Proponent, Skeptic, Adjudicator)
Incorporates Zero-Knowledge User Profiles for Personalized Harm Assessment
"""

import json
import requests
import sys
import os

# Try importing from config, fallback to environment or defaults
try:
    from config import GROQ_API_KEY, GROQ_ENDPOINT, GROQ_MODEL, GEMINI_API_KEY
except ImportError:
    GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
    GROQ_ENDPOINT = os.environ.get(
        "GROQ_ENDPOINT", "https://api.groq.com/openai/v1/chat/completions"
    )
    GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")


def _call_groq_agent(role_prompt, claim, context=""):
    """Generic caller for Groq LLaMA models"""
    if not GROQ_API_KEY or GROQ_API_KEY == "your_groq_api_key_here":
        return f"{role_prompt.split()[0]} Agent: (Offline - No API Key)"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    messages = [
        {"role": "system", "content": role_prompt},
        {"role": "user", "content": f"Claim: {claim}\nContext: {context}"},
    ]

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": messages,
        "temperature": 0.2,
        "max_tokens": 500,
    }

    try:
        response = requests.post(
            GROQ_ENDPOINT, headers=headers, json=payload, timeout=20
        )
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            return f"Error: Groq HTTP {response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"


def _call_gemini_adjudicator(
    proponent_arg, skeptic_arg, claim, context="", user_profile=None
):
    """Gemini 1.5 Flash Adjudicator mapping to strict JSON scheme"""
    if not GEMINI_API_KEY or GEMINI_API_KEY == "your_gemini_api_key_here":
        return None  # Let the pipeline fallback to pattern matching

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}

    profile_str = ""
    if user_profile and isinstance(user_profile, dict):
        profile_str = f"\nUSER PROFILE (Calculate conditional harm based on this!):\n{json.dumps(user_profile, indent=2)}\n"

    prompt = f"""
You are the Supreme Medical Adjudicator. Your job is to read a user's health claim, and the arguments of two AI systems (Proponent and Skeptic), and declare a final verdict.
CRITICAL: If a "USER PROFILE" is provided, evaluate risk *specifically* for that user. Even if a claim is generally safe, if it interacts dangerously with their Profile (e.g. they take Statins and the claim tells them to consume Grapefruit), you MUST return a 'critical' or 'high' risk_level.

Claim: "{claim}"
Context: "{context}"

Proponent Argument:
{proponent_arg}

Skeptic Argument:
{skeptic_arg}
{profile_str}

Provide analysis in this exact JSON format. DO NOT generate markdown wrappers, just raw JSON:
{{
    "verdict": "misinformation|potential_misinformation|likely_accurate|uncertain",
    "confidence": 0.0-1.0,
    "risk_level": "low|medium|high|critical",
    "reasoning": "Brief synthesis resolving the debate, citing personal risk if applicable",
    "medical_entities": ["list", "of", "medical", "terms", "found", "for", "database", "searching"],
    "action_needed": "specific recommended action for users"
}}
"""

    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=25)
        if resp.status_code == 200:
            content = resp.json()["candidates"][0]["content"]["parts"][0]["text"]

            # Extract JSON
            json_start = content.find("{")
            json_end = content.rfind("}") + 1
            json_str = content[json_start:json_end]

            return json.loads(json_str)
        return None
    except Exception as e:
        print(f"Adjudicator failed: {e}")
        return None


def groq_misinformation_detection(text, context=None, user_profile=None):
    """The Multi-Agent Debate Matrix logic"""
    print("🤖 Agent 1 (Proponent) analyzing...")
    proponent_prompt = "You are a Proponent Medical Researcher. Argue WHY the given claim MIGHT be scientifically valid, looking for emerging studies, fringe logic, or edge cases. Keep it under 150 words."
    proponent_arg = _call_groq_agent(proponent_prompt, text, context)

    print("🤖 Agent 2 (Skeptic) analyzing...")
    skeptic_prompt = "You are a Ruthless Medical Skeptic. Debunk the given claim using standard medical consensus, highlighting logical fallacies, lack of evidence, or dangers. Keep it under 150 words."
    skeptic_arg = _call_groq_agent(skeptic_prompt, text, context)

    print("⚖️ Agent 3 (Adjudicator) formulating verdict...")
    verdict = _call_gemini_adjudicator(
        proponent_arg, skeptic_arg, text, context, user_profile
    )

    return verdict


def detect_misinformation(text, context=None, user_profile=None):
    """Main misinformation detection function"""
    print("🚨 Phase 4: Multi-Agent Misinformation Adjudication...")

    # Try fully agentic debate detection first
    ai_analysis = groq_misinformation_detection(text, context, user_profile)

    if ai_analysis and "verdict" in ai_analysis:
        verdict = ai_analysis.get("verdict", "uncertain")
        confidence = float(ai_analysis.get("confidence", 0.5))
        risk_level = ai_analysis.get("risk_level", "medium")
        action_needed = ai_analysis.get(
            "action_needed", "Consult healthcare professionals"
        )

        # Verdict emoji mapping
        verdict_emojis = {
            "misinformation": "🚨",
            "potential_misinformation": "⚠️",
            "likely_accurate": "✅",
            "uncertain": "❔",
        }

        emoji = verdict_emojis.get(verdict, "❔")
        print(
            f"{emoji} AI Analysis: {verdict.upper()} ({verdict.replace('_', ' ').title()})"
        )
        print(f"🎯 Confidence: {confidence:.2f} ({confidence * 100:.0f}%)")
        print(f"⚠️ Risk Level: {risk_level.upper()}")
        print(
            f"📋 Recommended Action: {action_needed[:100]}{'...' if len(action_needed) > 100 else ''}"
        )

        return ai_analysis
    else:
        # Fallback to pattern matching
        print("⚠️ AI detection unavailable or failed, using pattern matching...")
        return pattern_based_detection(text)


def pattern_based_detection(text):
    """Fallback pattern-based misinformation detection"""
    high_risk_patterns = [
        "cure cancer",
        "miracle cure",
        "vaccines cause autism",
        "drink bleach",
        "essential oils cure cancer",
    ]
    positive_patterns = ["consult your doctor", "fda approved", "balanced diet"]

    text_lower = text.lower()
    high_risk_matches = [p for p in high_risk_patterns if p in text_lower]
    positive_matches = [p for p in positive_patterns if p in text_lower]

    if len(high_risk_matches) >= 1:
        return {
            "verdict": "misinformation",
            "confidence": 0.85,
            "risk_level": "critical",
            "reasoning": f"Contains dangerous misinformation patterns: {', '.join(high_risk_matches)}",
            "medical_entities": high_risk_matches,
            "action_needed": "Do not follow this advice. Consult healthcare professionals immediately.",
        }
    elif len(positive_matches) >= 2:
        return {
            "verdict": "likely_accurate",
            "confidence": 0.75,
            "risk_level": "low",
            "reasoning": f"Contains positive medical guidance patterns.",
            "medical_entities": positive_matches,
            "action_needed": "Information appears reasonable.",
        }
    else:
        return {
            "verdict": "uncertain",
            "confidence": 0.50,
            "risk_level": "medium",
            "reasoning": "No clear misinformation or positive patterns detected",
            "medical_entities": [],
            "action_needed": "Verify information with qualified healthcare professionals.",
        }


if __name__ == "__main__":
    # Internal module testing
    res = detect_misinformation(
        "Drinking grapefruit juice is perfectly healthy everyday."
    )
    print(res)

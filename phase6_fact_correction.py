#!/usr/bin/env python3
"""
Phase 6: Fact Correction
AI-powered fact-checking and correction using Gemini
"""

import requests
import json
from config import GEMINI_API_KEY, GEMINI_MODEL

def correct_misinformation(claim, sources, misinformation_analysis):
    """Main fact correction function"""
    print("🏥 Phase 6: Medical Fact-Checking (Gemini AI)...")
    
    # Use Gemini for comprehensive fact-checking
    corrected_facts = gemini_fact_correction(claim, sources, misinformation_analysis)
    
    print("✅ Medical fact-check completed")
    return corrected_facts

def gemini_fact_correction(claim, sources, analysis=None):
    """Concise fact-checking using Gemini AI with source URLs"""
    try:
        # Prepare sources summary with URLs
        sources_summary = "\n".join([
            f"- {s['source']}: {s['title']} - {s.get('url', 'No URL')}"
            for s in sources[:3]
        ])
        
        prompt = f"""
You are a medical fact-checker. Analyze this health claim and provide a CONCISE fact-check in exactly this format:

CLAIM: "{claim}"

SOURCES:
{sources_summary}

Provide a SHORT response (maximum 150 words) with:

**VERDICT:** [TRUE/FALSE/PARTIALLY TRUE/MISLEADING]

**CORRECTION:** [In 2-3 sentences, what is the accurate information]

**EXPLANATION:** [In 1-2 sentences, why this matters for health/safety]

**SOURCES:** [List 2-3 reliable sources with URLs that support your assessment]

Keep it brief, clear, and actionable. Focus on patient safety.
"""
        
        api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
        
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": 0.1,
                "maxOutputTokens": 500,
                "topP": 0.8,
                "topK": 40
            }
        }
        
        response = requests.post(api_url, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if 'candidates' in result and result['candidates']:
                fact_check = result['candidates'][0]['content']['parts'][0]['text']
                return format_concise_output(fact_check, sources)
            else:
                return generate_concise_fallback(claim, sources, analysis)
        else:
            print(f"⚠️ Gemini API error: {response.status_code}")
            return generate_concise_fallback(claim, sources, analysis)
            
    except Exception as e:
        print(f"❌ Gemini fact-check error: {e}")
        return generate_concise_fallback(claim, sources, analysis)

def format_concise_output(fact_check, sources):
    """Format the output to be concise with source URLs"""
    # Add source URLs if not already included
    source_urls = "\n".join([
        f"• {s['source']}: {s.get('url', 'URL not available')}"
        for s in sources[:3]
    ])
    
    if "**SOURCES:**" not in fact_check:
        fact_check += f"\n\n**VERIFIED SOURCES:**\n{source_urls}"
    
    return fact_check

def generate_concise_fallback(claim, sources, analysis=None):
    """Generate concise fallback correction when AI is unavailable"""
    
    verdict = "REQUIRES VERIFICATION"
    if analysis:
        ai_verdict = analysis.get('verdict', 'uncertain')
        if ai_verdict == 'misinformation':
            verdict = "FALSE"
        elif ai_verdict == 'potential_misinformation':
            verdict = "MISLEADING"
    
    source_urls = "\n".join([
        f"• {s['source']}: {s.get('url', 'URL not available')}"
        for s in sources[:3]
    ])
    
    return f"""**VERDICT:** {verdict}

**CORRECTION:** This claim requires verification with medical professionals. Always consult healthcare providers for accurate medical information.

**EXPLANATION:** Medical claims should be verified through peer-reviewed sources and professional medical guidance to ensure safety.

**VERIFIED SOURCES:**
{source_urls}

⚠️ Consult healthcare professionals for personalized medical advice."""

def generate_fallback_correction(claim, analysis=None):
    """Generate fallback correction when AI is unavailable"""
    
    # Determine severity based on analysis
    if analysis:
        verdict = analysis.get('verdict', 'uncertain')
        risk_level = analysis.get('risk_level', 'medium')
    else:
        verdict = 'uncertain'
        risk_level = 'medium'
    
    if verdict == 'misinformation' and risk_level in ['high', 'critical']:
        return f"""
1. **Assessment:** The claim "{claim}" contains dangerous medical misinformation.

2. **Correction:** This claim contradicts established medical evidence and could be harmful if followed. Medical decisions should always be based on peer-reviewed research and guidance from qualified healthcare professionals.

3. **Explanation:** Misinformation can spread quickly and cause real harm by discouraging people from seeking proper medical care or encouraging dangerous practices. Always verify health information with reputable sources.

4. **Medical Disclaimer:** This assessment is for informational purposes only. For any health concerns, consult qualified healthcare professionals. In medical emergencies, contact emergency services immediately.
"""
    
    elif verdict == 'potential_misinformation':
        return f"""
1. **Assessment:** The claim "{claim}" contains elements that require careful verification.

2. **Correction:** While some aspects may have basis in fact, the claim as presented may be misleading or lack sufficient scientific support. It's important to consult multiple reliable sources.

3. **Explanation:** Health information can be complex, and claims may be partially true but taken out of context or oversimplified. Professional medical guidance is essential for accurate interpretation.

4. **Medical Disclaimer:** This assessment is for informational purposes only. Always consult qualified healthcare professionals for medical advice tailored to your specific situation.
"""
    
    else:
        return f"""
1. **Assessment:** The claim "{claim}" requires verification with qualified medical sources.

2. **Correction:** Without access to comprehensive fact-checking resources, we cannot definitively assess this claim. Please consult reputable medical sources and healthcare professionals.

3. **Explanation:** Medical information should always be verified through multiple reliable sources, including peer-reviewed research and guidance from healthcare professionals.

4. **Medical Disclaimer:** This assessment is for informational purposes only. For accurate medical information and personalized advice, consult qualified healthcare professionals.
"""

def assess_correction_quality(correction_text):
    """Assess the quality and completeness of the correction"""
    quality_indicators = {
        'has_assessment': any(word in correction_text.lower() for word in ['assessment', 'true', 'false', 'misleading']),
        'has_correction': 'correction' in correction_text.lower(),
        'has_explanation': 'explanation' in correction_text.lower(),
        'has_disclaimer': any(word in correction_text.lower() for word in ['disclaimer', 'consult', 'professional']),
        'mentions_evidence': any(word in correction_text.lower() for word in ['research', 'study', 'evidence', 'clinical']),
        'appropriate_length': 200 <= len(correction_text) <= 2000
    }
    
    quality_score = sum(quality_indicators.values()) / len(quality_indicators)
    
    return {
        'quality_score': quality_score,
        'indicators': quality_indicators,
        'length': len(correction_text),
        'quality_level': 'high' if quality_score >= 0.8 else 'medium' if quality_score >= 0.6 else 'low'
    }

def format_correction_for_display(correction_text):
    """Format the correction for better readability"""
    # Add proper spacing and formatting
    formatted = correction_text.strip()
    
    # Ensure proper line breaks between sections
    formatted = formatted.replace('2. **Correction:**', '\n2. **Correction:**')
    formatted = formatted.replace('3. **Explanation:**', '\n3. **Explanation:**')
    formatted = formatted.replace('4. **Medical Disclaimer:**', '\n4. **Medical Disclaimer:**')
    
    # Clean up extra whitespace
    lines = [line.strip() for line in formatted.split('\n')]
    formatted = '\n'.join(line for line in lines if line)
    
    return formatted

def generate_personalized_advice(claim, user_context=None):
    """Generate personalized advice based on claim and user context"""
    if not user_context:
        return "For personalized medical advice, please consult with a qualified healthcare professional who can assess your individual situation."
    
    # This would be expanded with more sophisticated personalization
    advice = f"""
Based on your interest in "{claim}", here are some general recommendations:

• Consult with your healthcare provider to discuss any health concerns
• Verify health information through reputable sources (WHO, CDC, medical journals)
• Be cautious of claims that seem too good to be true
• Don't stop or change prescribed treatments without medical supervision
• Keep a healthy skepticism about miracle cures or instant solutions

Remember: This is general guidance and not a substitute for professional medical advice.
"""
    
    return advice

if __name__ == "__main__":
    # Test the module
    test_claims = [
        "Vaccines cause autism in children",
        "Drinking lemon water cures cancer",
        "Regular exercise helps prevent heart disease"
    ]
    
    test_sources = [
        {
            'source': 'CDC',
            'title': 'Vaccine Safety Information',
            'reliability': 0.97
        },
        {
            'source': 'WHO',
            'title': 'World Health Organization Guidelines',
            'reliability': 0.98
        }
    ]
    
    for claim in test_claims:
        print(f"\n=== Testing Claim: {claim} ===")
        correction = correct_misinformation(claim, test_sources, None)
        quality = assess_correction_quality(correction)
        
        print(f"Correction Quality: {quality['quality_level']}")
        print(f"Correction Preview: {correction[:200]}...")
        print("-" * 50)

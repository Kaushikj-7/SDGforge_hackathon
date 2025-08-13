#!/usr/bin/env python3
"""
Phase 4: Misinformation Detection
AI-powered detection using Groq and pattern matching
"""

import json
import requests
from config import GROQ_API_KEY, GROQ_ENDPOINT, GROQ_MODEL

def detect_misinformation(text, context=None):
    """Main misinformation detection function"""
    print("🚨 Phase 4: Enhanced Misinformation Detection (Groq AI)...")
    
    # Try AI detection first
    ai_analysis = groq_misinformation_detection(text, context)
    
    if ai_analysis:
        verdict = ai_analysis.get('verdict', 'uncertain')
        confidence = ai_analysis.get('confidence', 0.5)
        risk_level = ai_analysis.get('risk_level', 'medium')
        action_needed = ai_analysis.get('action_needed', 'Consult healthcare professionals')
        
        # Verdict emoji mapping
        verdict_emojis = {
            "misinformation": "🚨",
            "potential_misinformation": "⚠️", 
            "likely_accurate": "✅",
            "uncertain": "❓"
        }
        
        emoji = verdict_emojis.get(verdict, "❓")
        print(f"{emoji} AI Analysis: {verdict.upper()} ({verdict.replace('_', ' ').title()})")
        print(f"🎯 Confidence: {confidence:.2f} ({confidence*100:.0f}%)")
        print(f"⚠️ Risk Level: {risk_level.upper()}")
        print(f"📋 Recommended Action: {action_needed[:100]}{'...' if len(action_needed) > 100 else ''}")
        
        return ai_analysis
    else:
        # Fallback to pattern matching
        print("⚠️ AI detection unavailable, using pattern matching...")
        return pattern_based_detection(text)

def groq_misinformation_detection(text, context=None):
    """AI-powered misinformation detection using Groq"""
    try:
        context_info = f"\nContext: {context}" if context else ""
        
        prompt = f"""
You are a medical expert AI analyzing health information for potential misinformation.

Text to analyze: "{text}"{context_info}

Provide analysis in this exact JSON format:
{{
    "verdict": "misinformation|potential_misinformation|likely_accurate|uncertain",
    "confidence": 0.0-1.0,
    "risk_level": "low|medium|high|critical",
    "reasoning": "Brief explanation of why this verdict was reached",
    "medical_entities": ["list", "of", "medical", "terms", "found"],
    "action_needed": "specific recommended action for users"
}}

Focus on:
- Dangerous medical advice that could harm people
- False claims about treatments, cures, or prevention
- Conspiracy theories about health organizations or vaccines
- Unproven miracle cures or treatments
- Misinformation about established medical science

Be especially careful about claims that:
- Promise instant or miracle cures
- Contradict established medical consensus
- Discourage people from seeking proper medical care
- Promote dangerous substances or practices
"""
        
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messages": [{"role": "user", "content": prompt}],
            "model": GROQ_MODEL,
            "temperature": 0.1,
            "max_tokens": 1000
        }
        
        response = requests.post(GROQ_ENDPOINT, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            # Extract JSON from response
            try:
                json_start = content.find('{')
                json_end = content.rfind('}') + 1
                json_str = content[json_start:json_end]
                analysis = json.loads(json_str)
                return analysis
            except (json.JSONDecodeError, ValueError) as e:
                print(f"⚠️ JSON parsing error: {e}")
                return None
        else:
            print(f"⚠️ Groq API error: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Groq detection error: {e}")
        return None

def pattern_based_detection(text):
    """Fallback pattern-based misinformation detection"""
    # Dangerous misinformation patterns
    high_risk_patterns = [
        'cure cancer', 'cure covid', 'cure diabetes', 'cure aids', 'cure hiv',
        'miracle cure', 'instant cure', 'natural cure for cancer',
        'vaccines cause autism', 'vaccines are dangerous', 'vaccines kill',
        'big pharma conspiracy', 'government conspiracy', 'medical conspiracy',
        'drink bleach', 'inject bleach', 'hydrogen peroxide cure',
        'essential oils cure cancer', 'homeopathy cures',
        'covid is fake', 'covid hoax', 'pandemic hoax',
        'microchips in vaccines', '5g causes covid', 'bill gates microchip'
    ]
    
    # Medium risk patterns
    medium_risk_patterns = [
        'doctors don\'t want you to know', 'medical industry hiding',
        'natural alternative to', 'big pharma doesn\'t want',
        'government hiding cure', 'suppress this information',
        'detox removes toxins', 'alkaline water cures',
        'colloidal silver cures', 'vitamin c cures covid'
    ]
    
    # Positive health patterns (likely accurate)
    positive_patterns = [
        'consult your doctor', 'seek medical advice', 'talk to healthcare provider',
        'clinical trials show', 'peer reviewed study', 'medical research',
        'fda approved', 'who recommends', 'cdc guidelines',
        'exercise regularly', 'balanced diet', 'healthy lifestyle'
    ]
    
    text_lower = text.lower()
    
    # Count pattern matches
    high_risk_matches = [pattern for pattern in high_risk_patterns if pattern in text_lower]
    medium_risk_matches = [pattern for pattern in medium_risk_patterns if pattern in text_lower]
    positive_matches = [pattern for pattern in positive_patterns if pattern in text_lower]
    
    # Determine verdict based on pattern matches
    if len(high_risk_matches) >= 1:
        return {
            'verdict': 'misinformation',
            'confidence': 0.85,
            'risk_level': 'critical',
            'reasoning': f'Contains dangerous misinformation patterns: {", ".join(high_risk_matches)}',
            'medical_entities': high_risk_matches,
            'action_needed': 'Do not follow this advice. Consult healthcare professionals immediately.'
        }
    elif len(medium_risk_matches) >= 2:
        return {
            'verdict': 'potential_misinformation',
            'confidence': 0.70,
            'risk_level': 'high',
            'reasoning': f'Contains suspicious patterns: {", ".join(medium_risk_matches)}',
            'medical_entities': medium_risk_matches,
            'action_needed': 'Verify with trusted medical sources before acting on this information.'
        }
    elif len(positive_matches) >= 2:
        return {
            'verdict': 'likely_accurate',
            'confidence': 0.75,
            'risk_level': 'low',
            'reasoning': f'Contains positive medical guidance patterns: {", ".join(positive_matches)}',
            'medical_entities': positive_matches,
            'action_needed': 'Information appears reasonable, but still consult healthcare professionals.'
        }
    else:
        return {
            'verdict': 'uncertain',
            'confidence': 0.50,
            'risk_level': 'medium',
            'reasoning': 'No clear misinformation or positive patterns detected',
            'medical_entities': [],
            'action_needed': 'Verify information with qualified healthcare professionals.'
        }

def assess_claim_credibility(text):
    """Assess the credibility of health claims"""
    credibility_indicators = {
        'positive': [
            'clinical trial', 'peer reviewed', 'published study', 'medical journal',
            'fda approved', 'who guideline', 'cdc recommendation', 'medical consensus',
            'evidence based', 'scientific study', 'research shows', 'meta analysis'
        ],
        'negative': [
            'secret cure', 'doctors hate', 'suppressed by', 'hidden truth',
            'miracle cure', 'instant results', 'no side effects', 'works 100%',
            'ancient remedy', 'natural cure', 'big pharma conspiracy', 'government cover up'
        ]
    }
    
    text_lower = text.lower()
    
    positive_score = sum(1 for indicator in credibility_indicators['positive'] if indicator in text_lower)
    negative_score = sum(1 for indicator in credibility_indicators['negative'] if indicator in text_lower)
    
    if positive_score > negative_score:
        credibility = 'high'
    elif negative_score > positive_score:
        credibility = 'low'
    else:
        credibility = 'medium'
    
    return {
        'credibility': credibility,
        'positive_indicators': positive_score,
        'negative_indicators': negative_score
    }

if __name__ == "__main__":
    # Test the module
    test_cases = [
        "Vaccines cause autism in children and should be avoided",
        "Regular exercise and a balanced diet help prevent heart disease",
        "Essential oils can cure cancer naturally without any side effects",
        "Consult your doctor before taking any new medication",
        "Drinking bleach can cure COVID-19 instantly"
    ]
    
    for i, text in enumerate(test_cases, 1):
        print(f"\n=== Test Case {i} ===")
        print(f"Text: {text}")
        result = detect_misinformation(text)
        credibility = assess_claim_credibility(text)
        print(f"Verdict: {result['verdict']}")
        print(f"Confidence: {result['confidence']}")
        print(f"Risk Level: {result['risk_level']}")
        print(f"Credibility: {credibility['credibility']}")

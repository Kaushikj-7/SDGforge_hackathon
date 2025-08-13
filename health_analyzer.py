#!/usr/bin/env python3
"""
CONSOLIDATED HEALTH MISINFORMATION ANALYZER
Main application combining all functionality in one file
Handles: URLs | Articles | Messages | Text Claims
"""

import sys
import os
from real_medical_apis import ComprehensiveMedicalAPIs, process_input, simple_nlp_preprocess, generate_report

def main_health_analyzer():
    """Main health information analyzer"""
    print("Starting Consolidated Health Information Analyzer...")
    print("All-in-one system: Input Processing + AI Analysis + Medical Sources")
    print("-" * 70)
    
    print("\n=== CONSOLIDATED HEALTH ANALYZER ===")
    print("📱 Handles: URLs | Articles | Forwarded Messages | Text")
    print("🤖 Powered by: Groq + Gemini + Comprehensive Medical Sources")
    print("🏥 Sources: PubMed | WHO | CDC | NIH | FDA | ClinicalTrials.gov")
    print("=" * 70 + "\n")
    
    # Initialize medical APIs
    medical_api = ComprehensiveMedicalAPIs()
    
    # Phase 1: Input Processing
    print("📥 Phase 1: Input Processing...")
    print("Enter any of the following:")
    print("• Website URL (e.g., news article about health)")
    print("• Forwarded message from WhatsApp/Telegram")
    print("• Copy-pasted article content")
    print("• Plain health claim")
    print("-" * 40)
    
    user_input = input("Paste your content here: ")
    print(f"✅ Input received ({len(user_input)} characters)")
    
    # Phase 2: Content Analysis
    print("\n🔍 Phase 2: Content Analysis...")
    processed_input = process_input(user_input)
    print(f"📋 Input Type: {processed_input['type'].upper()}")
    print(f"📄 Source: {processed_input['source']}")
    print(f"📰 Title: {processed_input['title']}")
    print(f"📝 Content: {processed_input['content'][:50]}...")
    
    # Phase 3: Medical Research
    print("\n🔬 Phase 3: Comprehensive Medical Research...")
    medical_sources = medical_api.search_medical_sources(processed_input['content'])
    
    research_count = len([s for s in medical_sources if s['type'] == 'research'])
    guideline_count = len([s for s in medical_sources if s['type'] == 'guideline'])
    regulation_count = len([s for s in medical_sources if s['type'] == 'regulation'])
    drug_safety_count = len([s for s in medical_sources if s['type'] == 'drug_safety'])
    
    print(f"📚 Consulted {len(medical_sources)} authoritative sources:")
    print(f"  📋 Research: {research_count} sources")
    print(f"  📋 Guidelines: {guideline_count} sources")
    print(f"  📋 Regulation: {regulation_count} sources")
    if drug_safety_count > 0:
        print(f"  💊 Drug Safety: {drug_safety_count} sources")
    
    if medical_sources:
        print(f"\n  🔍 Top Sources:")
        for i, source in enumerate(medical_sources[:3], 1):
            print(f"    {i}. {source['source']}: {source['title'][:50]}...")
    print()
    
    # Phase 4: Language Processing
    print("🧠 Phase 4: Language Processing...")
    language, cleaned_text = simple_nlp_preprocess(processed_input['content'])
    print(f"🌐 Language: {language}")
    print(f"🧹 Cleaned text: {cleaned_text[:50]}...")
    
    # Phase 5: AI Detection
    print("\n🚨 Phase 5: Enhanced Misinformation Detection (Groq AI)...")
    detection_result = medical_api.detect_misinformation_groq(processed_input['content'])
    
    verdict_emoji = "✅" if detection_result['verdict'] == 'likely_accurate' else "⚠️" if detection_result['verdict'] == 'uncertain' else "❌"
    print(f"{verdict_emoji} AI Analysis: {detection_result['verdict'].replace('_', ' ').upper()} ({detection_result['verdict'].replace('_', ' ').title()})")
    print(f"🎯 Confidence: {detection_result['confidence']:.2f} ({detection_result['confidence']*100:.0f}%)")
    print(f"⚠️ Risk Level: {detection_result['risk_level'].upper()}")
    print(f"📋 Recommended Action: {detection_result['action_needed']}")
    
    # Phase 6: Fact Checking
    print("\n🏥 Phase 6: Medical Fact-Checking (Gemini AI)...")
    fact_check_result = medical_api.fact_check_gemini(processed_input['content'], medical_sources)
    print("✅ Medical fact-check completed")
    
    # Phase 7: Generate Report
    print("\n📊 Phase 7: Generating Comprehensive Report...")
    
    # Create verdict string
    verdict_map = {
        'likely_accurate': '✅ LIKELY ACCURATE',
        'uncertain': '⚠️ UNCERTAIN', 
        'likely_misinformation': '❌ LIKELY MISINFORMATION'
    }
    
    input_type_emoji = {
        'url': '🌐 URL',
        'article': '📄 ARTICLE', 
        'forwarded_message': '📱 FORWARDED MESSAGE',
        'plain_text': '💬 PLAIN_TEXT'
    }
    
    verdict = f"{input_type_emoji.get(processed_input['type'], '📝 TEXT')}: {verdict_map.get(detection_result['verdict'], '❓ UNKNOWN')}"
    
    # Create reasoning
    reasoning = f"""📋 Content Analysis:
• Input Type: {processed_input['type'].replace('_', ' ').title()}
• Source: {processed_input['source']}
• Language: {language}
• Platform: N/A

🤖 AI Assessment:
• Detection Model: Groq Llama3-70B (Medical Specialized)
• Verdict: {detection_result['verdict'].replace('_', ' ').title()}
• Confidence: {detection_result['confidence']:.2f} ({detection_result['confidence']*100:.0f}%)
• Fact-Checker: Google Gemini AI

📚 Evidence Review:
• Medical Sources: {len(medical_sources)} authoritative sources consulted
• Literature Search: PubMed, ClinicalTrials.gov, FDA, WHO, CDC, NIH
• Cross-Reference: Multiple international health organizations

⚠️ Important Notice:
This analysis is for informational purposes only.
Always consult qualified healthcare professionals for medical decisions."""
    
    # Generate final report
    report = generate_report(verdict, reasoning, medical_sources, fact_check_result)
    print("✅ Analysis completed!")
    
    print(f"\n{report}")
    
    print("\n" + "=" * 60)
    print("🏥 MEDICAL DISCLAIMER:")
    print("This AI analysis is for informational purposes only.")
    print("For medical emergencies, contact emergency services immediately.")
    print("Always consult qualified healthcare professionals for medical advice.")
    print("=" * 60)

if __name__ == "__main__":
    main_health_analyzer()

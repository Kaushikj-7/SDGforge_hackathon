#!/usr/bin/env python3
"""
Simple Health Analyzer
Uses individual phase modules for analysis
"""

import sys

# Import phase modules
from phase1_user_input import get_user_input, classify_input_type
from phase2_content_retrieval import extract_from_url
from phase4_misinformation_detection import detect_misinformation
from phase5_trusted_source_retrieval import retrieve_trusted_sources
from phase6_fact_correction import gemini_fact_correction

def simple_health_analyzer():
    """Simple health analyzer using phase modules"""
    print("🏥 SIMPLE HEALTH ANALYZER")
    print("=" * 50)
    print("📱 Analyzes health claims with AI + Medical Sources")
    print("🤖 Powered by: Groq + Gemini + FDA + PubMed")
    print("-" * 50)
    
    # Phase 1: Get user input
    print("\n📥 Enter your health claim or question:")
    user_input = input("> ")
    
    if not user_input.strip():
        print("❌ No input provided. Exiting.")
        return
    
    print(f"✅ Input received: {len(user_input)} characters")
    
    # Phase 2: Process input
    print("\n🔍 Processing input...")
    processed = classify_input_type(user_input)
    print(f"📋 Type: {processed.get('type', 'text')}")
    
    # Phase 3: Extract content if needed
    content = user_input
    if processed.get('type') == 'url':
        print("🌐 Extracting content from URL...")
        extracted = extract_from_url(user_input)
        if extracted and isinstance(extracted, dict):
            content = extracted.get('content', user_input)
            if len(content) > 10:
                print(f"📄 Extracted {len(content)} characters")
                print(f"📰 Title: {extracted.get('title', 'Unknown')}")
            else:
                print("⚠️ Could not extract content, using original input")
                content = user_input
        elif extracted and isinstance(extracted, str):
            content = extracted
            print(f"📄 Extracted {len(content)} characters")
        else:
            print("⚠️ Could not extract content, using original input")
            content = user_input
    
    # Phase 4: AI Detection
    print("\n🤖 AI Misinformation Detection...")
    try:
        detection_result = detect_misinformation(content)
        if detection_result:
            verdict = detection_result.get('verdict', 'uncertain')
            confidence = detection_result.get('confidence', 0.5)
            print(f"📊 Verdict: {verdict.upper()}")
            print(f"🎯 Confidence: {confidence:.2f} ({confidence*100:.0f}%)")
        else:
            print("⚠️ AI detection unavailable")
    except Exception as e:
        print(f"⚠️ AI detection error: {e}")
    
    # Phase 5: Medical Sources (with Drug Safety)
    print("\n🔬 Searching Medical Sources...")
    try:
        sources = retrieve_trusted_sources(content, max_results=5)
        print(f"✅ Found {len(sources)} authoritative sources")
        
        if sources:
            print("\n📚 Top Medical Sources:")
            for i, source in enumerate(sources[:3], 1):
                print(f"  {i}. {source['source']}")
                print(f"     {source['title'][:60]}...")
                print(f"     {source['url']}")
    except Exception as e:
        print(f"⚠️ Medical source search error: {e}")
        sources = []
    
    # Phase 6: Fact Checking
    print("\n🏥 Medical Fact-Checking...")
    try:
        fact_check = gemini_fact_correction(content, sources)
        if fact_check and len(fact_check.strip()) > 10:
            print("✅ Fact-check completed")
            print("\n" + "=" * 60)
            print("📝 CONCISE MEDICAL ANALYSIS:")
            print("=" * 60)
            print(fact_check)
            print("=" * 60)
        else:
            print("⚠️ Fact-check unavailable")
    except Exception as e:
        print(f"⚠️ Fact-check error: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Analysis Complete!")
    print("\n⚠️ MEDICAL DISCLAIMER:")
    print("This analysis is for informational purposes only.")
    print("Always consult healthcare professionals for medical advice.")
    print("=" * 50)

if __name__ == "__main__":
    try:
        simple_health_analyzer()
    except KeyboardInterrupt:
        print("\n\n👋 Analysis interrupted. Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Please check your configuration and try again.")

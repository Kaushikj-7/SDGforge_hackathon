#!/usr/bin/env python3
"""
Universal Health Information Analyzer
Handles: URLs, Articles, Forwarded Messages, Plain Text
Uses: Groq + Gemini APIs + PubMed for comprehensive medical analysis
"""

import sys
import os

# Import modules
try:
    from phase3_nlp_preprocessing import nlp_preprocess
except ImportError:
    print("⚠️ Language detection unavailable, using fallback")
    def nlp_preprocess(text):
        return "en", text.lower().strip()

from phase7_explainable_output import generate_explainable_output
from groq_gemini_medical_apis import gemini_fact_correction
from real_medical_apis import comprehensive_medical_search, enhanced_groq_detection
from article_message_processor import enhanced_input_processor

def universal_health_analyzer():
    """
    Universal analyzer for any type of health-related input:
    - URLs (news articles, blog posts, social media links)
    - Forwarded messages (WhatsApp, Telegram, SMS)
    - Article snippets (copy-pasted content)
    - Plain text health claims
    """
    print("=== UNIVERSAL HEALTH INFORMATION ANALYZER ===")
    print("📱 Handles: URLs | Articles | Forwarded Messages | Text")
    print("🤖 Powered by: Groq + Gemini + Comprehensive Medical Sources")
    print("🏥 Sources: PubMed | ClinicalTrials.gov | FDA | WHO | CDC | NIH | Cochrane")
    print("=" * 70 + "\n")
    
    # Phase 1: Get and Process Input
    print("📥 Phase 1: Input Processing...")
    print("Enter any of the following:")
    print("• Website URL (e.g., news article about health)")
    print("• Forwarded message from WhatsApp/Telegram")
    print("• Copy-pasted article content")
    print("• Plain health claim")
    print("-" * 40)
    
    user_input = input("Paste your content here: ").strip()
    
    if not user_input:
        print("❌ No input provided. Exiting...")
        return
    
    print(f"\n✅ Input received ({len(user_input)} characters)")
    
    # Phase 2: Content Extraction and Classification
    print("\n🔍 Phase 2: Content Analysis...")
    try:
        extracted = enhanced_input_processor(user_input)
        
        print(f"📋 Input Type: {extracted['type'].upper()}")
        print(f"📄 Source: {extracted['source']}")
        
        if 'platform' in extracted:
            print(f"📱 Platform: {extracted['platform']}")
        
        if 'title' in extracted and extracted['title']:
            print(f"📰 Title: {extracted['title'][:80]}...")
        
        content_to_analyze = extracted['content']
        print(f"📝 Content: {content_to_analyze[:100]}...")
        
    except Exception as e:
        print(f"⚠️ Content extraction failed: {e}")
        content_to_analyze = user_input
        extracted = {
            "type": "fallback",
            "source": "Direct Input",
            "content": user_input
        }
    
    # Phase 3: Comprehensive Medical Literature Search
    print(f"\n🔬 Phase 3: Comprehensive Medical Research...")
    try:
        # Extract key medical terms for better search
        search_query = content_to_analyze[:200]  # Use first 200 chars for search
        literature = comprehensive_medical_search(search_query)
        
        print(f"📚 Consulted {len(literature)} authoritative sources:")
        
        # Group sources by type for better display
        source_types = {}
        for article in literature:
            source_type = article.get('type', 'unknown')
            if source_type not in source_types:
                source_types[source_type] = []
            source_types[source_type].append(article)
        
        # Display grouped sources
        for source_type, articles in source_types.items():
            type_name = source_type.replace('_', ' ').title()
            print(f"  📋 {type_name}: {len(articles)} sources")
        
        # Show top 3 most relevant sources
        print(f"\n  🔍 Top Sources:")
        for i, article in enumerate(literature[:3], 1):
            print(f"    {i}. {article['source']}: {article['title'][:50]}...")
        
    except Exception as e:
        print(f"⚠️ Comprehensive literature search failed: {e}")
        literature = [{"title": "Search unavailable", "source": "Error", "url": "", "summary": "", "type": "error"}]
    
    # Phase 4: NLP Preprocessing
    print(f"\n🧠 Phase 4: Language Processing...")
    try:
        language, cleaned_text = nlp_preprocess(content_to_analyze)
        print(f"🌐 Language: {language}")
        print(f"🧹 Cleaned text: {cleaned_text[:80]}...")
    except Exception as e:
        print(f"⚠️ Language processing failed: {e}")
        language, cleaned_text = "unknown", content_to_analyze.lower().strip()
    
    # Phase 5: Enhanced AI Misinformation Detection
    print(f"\n🚨 Phase 5: Enhanced Misinformation Detection (Groq AI)...")
    try:
        # Use enhanced detection with context
        content_context = f"Source: {extracted['source']}, Type: {extracted['type']}"
        analysis = enhanced_groq_detection(cleaned_text, content_context)
        
        verdict = analysis['verdict']
        confidence = analysis['confidence']
        risk_level = analysis['risk_level']
        action_needed = analysis['action_needed']
        
        # Determine emoji and color coding based on risk level
        if risk_level == "critical":
            status_emoji = "🔴"
            status_color = "CRITICAL ALERT"
        elif verdict == "misinformation":
            status_emoji = "🚨"
            status_color = "RED ALERT"
        elif verdict == "potential_misinformation":
            status_emoji = "⚠️"
            status_color = "WARNING"
        elif verdict == "likely_accurate":
            status_emoji = "✅"
            status_color = "VERIFIED"
        else:
            status_emoji = "❓"
            status_color = "UNCERTAIN"
        
        print(f"{status_emoji} AI Analysis: {verdict.upper()} ({status_color})")
        print(f"🎯 Confidence: {confidence:.2f} ({int(confidence*100)}%)")
        print(f"⚠️ Risk Level: {risk_level.upper()}")
        print(f"📋 Recommended Action: {action_needed.replace('_', ' ').title()}")
        
    except Exception as e:
        print(f"⚠️ AI detection failed: {e}")
        verdict, confidence, risk_level, action_needed = "uncertain", 0.5, "medium", "verify"
        status_emoji = "❓"
    
    # Phase 6: Medical Fact-Checking
    print(f"\n🏥 Phase 6: Medical Fact-Checking (Gemini AI)...")
    try:
        sources_summary = [f"{art['source']}: {art['title']}" for art in literature[:3]]
        
        # Create context for fact-checking
        fact_check_context = f"""
        Content Type: {extracted['type']}
        Source: {extracted['source']}
        AI Detection: {verdict} (confidence: {confidence:.2f})
        Content: {content_to_analyze[:500]}
        """
        
        corrected_facts = gemini_fact_correction(fact_check_context, sources_summary)
        print("✅ Medical fact-check completed")
        
    except Exception as e:
        print(f"⚠️ Fact-checking failed: {e}")
        corrected_facts = "Medical fact-checking service unavailable. Please consult healthcare professionals."
    
    # Phase 7: Comprehensive Report Generation
    print(f"\n📊 Phase 7: Generating Comprehensive Report...")
    
    # Enhanced verdict based on content type and analysis
    if extracted['type'] == 'url':
        verdict_prefix = "🌐 WEB CONTENT:"
    elif extracted['type'] == 'forwarded_message':
        verdict_prefix = "📱 FORWARDED MESSAGE:"
    elif extracted['type'] == 'article_snippet':
        verdict_prefix = "📰 ARTICLE CONTENT:"
    else:
        verdict_prefix = "💬 TEXT CLAIM:"
    
    if verdict == "misinformation":
        final_verdict = f"{verdict_prefix} 🚨 MISINFORMATION DETECTED"
    elif verdict == "potential_misinformation":
        final_verdict = f"{verdict_prefix} ⚠️ POTENTIALLY MISLEADING"
    elif verdict == "likely_accurate":
        final_verdict = f"{verdict_prefix} ✅ APPEARS CREDIBLE"
    else:
        final_verdict = f"{verdict_prefix} ❓ REQUIRES VERIFICATION"
    
    # Enhanced reasoning with content context
    reasoning = f"""
📋 Content Analysis:
• Input Type: {extracted['type'].title().replace('_', ' ')}
• Source: {extracted['source']}
• Language: {language}
• Platform: {extracted.get('platform', 'N/A')}

🤖 AI Assessment:
• Detection Model: Groq Llama3-70B (Medical Specialized)
• Verdict: {verdict.replace('_', ' ').title()}
• Confidence: {confidence:.2f} ({int(confidence*100)}%)
• Fact-Checker: Google Gemini AI

📚 Evidence Review:
• Medical Sources: {len(literature)} authoritative sources consulted
• Literature Search: PubMed, ClinicalTrials.gov, FDA, WHO, CDC, NIH, Cochrane
• Cross-Reference: Multiple international health organizations

⚠️ Important Notice:
This analysis is for informational purposes only.
Always consult qualified healthcare professionals for medical decisions.
"""
    
    # Create citations with enhanced information
    citations = []
    for article in literature:
        citation = f"{article['source']} - {article['title']}"
        if article.get('url'):
            citation += f" ({article['url']})"
        if article.get('summary'):
            citation += f" | Summary: {article['summary'][:100]}..."
        citations.append(citation)
    
    # Add original source citation if URL
    if extracted['type'] == 'url':
        citations.insert(0, f"Original Source: {extracted['source']}")
    
    # Generate final comprehensive report
    final_output = generate_explainable_output(
        verdict=final_verdict,
        reasoning=reasoning.strip(),
        citations=citations,
        corrected_text=corrected_facts
    )
    
    print("✅ Analysis completed!\n")
    print(final_output)
    
    # Additional warnings based on content type
    print("\n" + "="*60)
    
    if extracted['type'] == 'forwarded_message':
        print("📱 FORWARDED MESSAGE WARNING:")
        print("Be cautious with health information from forwarded messages.")
        print("Always verify with official medical sources before acting.")
        
    elif extracted['type'] == 'url':
        print("🌐 WEB CONTENT NOTICE:")
        print("Online health information varies in quality.")
        print("Prioritize information from recognized medical institutions.")
        
    print("\n🏥 MEDICAL DISCLAIMER:")
    print("This AI analysis is for informational purposes only.")
    print("For medical emergencies, contact emergency services immediately.")
    print("Always consult qualified healthcare professionals for medical advice.")
    print("="*60)
    
    return final_output

if __name__ == "__main__":
    try:
        print("Starting Universal Health Information Analyzer...")
        print("Supports: Articles | URLs | Forwarded Messages | Text Claims")
        print("AI Powered: Groq + Gemini + PubMed Integration")
        print("-" * 70 + "\n")
        
        result = universal_health_analyzer()
        
    except KeyboardInterrupt:
        print("\n\n🛑 Analysis interrupted by user.")
    except Exception as e:
        print(f"\n\n❌ Error in analysis: {e}")
        print("💡 Please check your API keys in config.py")
        sys.exit(1)

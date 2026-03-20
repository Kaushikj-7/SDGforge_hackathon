import sys
import os

with open('simple_backend.py', 'w', encoding='utf-8') as f:
    f.write('''#!/usr/bin/env python3
\"\"\"
Simplified Flask Backend for Medical Fact Verifier Extension
\"\"\"

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from flask import Flask, request, jsonify
    print("✅ Flask imported successfully")
except ImportError as e:
    print(f"❌ Flask import error: {e}")
    exit(1)

try:
    from flask_cors import CORS
    print("✅ Flask-CORS imported successfully")
except ImportError:
    print("⚠️ Flask-CORS not available, using manual CORS")
    CORS = None

import time
import json
import traceback

try:
    from phase1_user_input import classify_input_type
    from phase2_content_retrieval import retrieve_content
    from phase4_misinformation_detection import detect_misinformation
    from phase5_trusted_source_retrieval import retrieve_trusted_sources
    from phase6_fact_correction import correct_misinformation_with_chain
except ImportError as e:
    print(f"⚠️ Phase import error: {e}")
    classify_input_type = None
    retrieve_content = None
    detect_misinformation = None
    retrieve_trusted_sources = None
    correct_misinformation_with_chain = None

app = Flask(__name__)

# Enable CORS manually if flask_cors is not available
if CORS:
    CORS(app)
else:
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response

@app.route('/api/verify', methods=['POST', 'OPTIONS'])
def verify_medical_fact():
    \"\"\"API endpoint for medical fact verification with full Phase 1-6 pipeline\"\"\"
    if request.method == 'OPTIONS':
        return '', 200

    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'error': 'Missing required field: text'}), 400

        # Extract all parameters from frontend payload
        claim_text = data.get('text', '').strip()
        context = data.get('context', '')
        source_url = data.get('source_url', '')
        user_profile = data.get('user_profile', {})
        extraction_mode = data.get('extraction_mode', 'text')

        print(f"📥 Verification request: {claim_text[:50]}...")
        print(f"📋 Mode: {extraction_mode} | Profile: {bool(user_profile)}")

        # Initialize proof_chain
        proof_chain = [
            {\"node\": \"User Claim Received\", \"type\": \"input\", \"content\": claim_text[:100]}
        ]

        # PHASE 1: Classification
        if classify_input_type:
            classified = classify_input_type(claim_text)
            proof_chain.append({
                \"node\": f\"Classified: {classified.get('type', 'text')}\",
                \"type\": \"classification\"
            })

        # PHASE 2: Content Retrieval & Processing
        if retrieve_content:
            input_data = {
                \"type\": \"plain_text\",
                \"content\": claim_text,
                \"context\": context,
                \"source_url\": source_url,
                \"extraction_mode\": extraction_mode
            }
            content_result = retrieve_content(input_data)
            processed_claim = content_result.get('content', claim_text)
            proof_chain.append({
                \"node\": \"Content Processed\",
                \"type\": \"content\"
            })
        else:
            processed_claim = claim_text

        # PHASE 4: Misinformation Detection (WITH USER_PROFILE!)
        analysis_result = None
        medical_entities = []

        if detect_misinformation:
            analysis_result = detect_misinformation(
                processed_claim,
                context=context,
                user_profile=user_profile  # CRITICAL: Pass user_profile here
            )
            if analysis_result:
                proof_chain.append({
                    \"node\": f\"Analysis: {analysis_result.get('verdict', 'pending')}\",
                    \"type\": \"analysis\",
                    \"confidence\": analysis_result.get('confidence', 0.0)
                })
                medical_entities = analysis_result.get('medical_entities', [])

        if not analysis_result:
            # Fallback analysis if Phase 4 fails
            analysis_result = {
                'verdict': 'uncertain',
                'confidence': 0.0,
                'risk_level': 'medium',
                'reasoning': 'Offline mode - AI unavailable',
                'medical_entities': [],
                'action_needed': 'Verify with healthcare professionals'
            }

        # PHASE 5: Trusted Source Retrieval
        sources = []
        if retrieve_trusted_sources and medical_entities:
            query = ' '.join(medical_entities[:3])
            try:
                sources = retrieve_trusted_sources(query, max_results=3, force_test=False)
            except Exception as e:
                print(f"⚠️ Phase 5 error: {e}")

            if sources:
                proof_chain.append({
                    \"node\": f\"Found {len(sources)} Trusted Source(s)\",
                    \"type\": \"sources\"
                })

        # PHASE 6: Fact Correction WITH PROOF_CHAIN
        if correct_misinformation_with_chain:
            fact_check = correct_misinformation_with_chain(
                claim=processed_claim,
                sources=sources,
                misinformation_analysis=analysis_result,
                proof_chain_input=proof_chain
            )
            corrected_fact = fact_check.get('corrected_fact', 'Unable to verify')
            proof_chain = fact_check.get('proof_chain', proof_chain)
        else:
            corrected_fact = \"Phase 6 unavailable - check server logs\"

        # Map verdict to API status
        verdict = analysis_result.get('verdict', 'uncertain')
        status_map = {
            'misinformation': 'harmful',
            'potential_misinformation': 'caution',
            'likely_accurate': 'safe',
            'uncertain': 'caution'
        }
        status = status_map.get(verdict, 'caution')

        # Build source links from sources or use defaults
        source_links = [s.get('url', '') for s in sources if isinstance(s, dict) and s.get('url')][:3]
        if not source_links:
            source_links = [
                'https://www.who.int/',
                'https://www.cdc.gov/',
                'https://pubmed.ncbi.nlm.nih.gov/'
            ]

        # Add final node to proof chain
        proof_chain.append({
            \"node\": \"Verification Complete\",
            \"type\": \"final\"
        })

        # Build response
        response = {
            'status': status,
            'corrected_fact': corrected_fact,
            'explanation': analysis_result.get('reasoning', 'Claim requires verification'),
            'source_links': source_links,
            'proof_chain': proof_chain,
            'confidence': analysis_result.get('confidence', 0.0),
            'risk_level': analysis_result.get('risk_level', 'medium'),
            'action_needed': analysis_result.get('action_needed', 'Consult healthcare professionals')
        }

        print(f\"✅ Response: {status} (confidence: {analysis_result.get('confidence', 0):.1%})\")
        return jsonify(response)

    except Exception as e:
        print(f\"❌ Error: {e}\")
        traceback.print_exc()

        return jsonify({
            'error': str(e),
            'status': 'error',
            'corrected_fact': 'Unable to verify claim.',
            'explanation': 'An error occurred during verification. Check server logs.',
            'source_links': [],
            'proof_chain': [{\"node\": \"Error Occurred\", \"type\": \"error\", \"message\": str(e)}]
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    \"\"\"Health check endpoint\"\"\"
    return jsonify({
        'status': 'healthy',
        'service': 'Medical Fact Verifier API'
    })

@app.route('/', methods=['GET'])
def home():
    \"\"\"Root endpoint\"\"\"
    return jsonify({
        'service': 'Medical Fact Verifier API',
        'status': 'running'
    })

if __name__ == '__main__':
    print(\"🩺 Starting Simple Medical Fact Verifier Backend...\")
    print(\"📡 Server: http://localhost:5000\")
    print(\"🔗 API: http://localhost:5000/api/verify\")

    try:
        app.run(host='127.0.0.1', port=5000, debug=False)
    except Exception as e:
        print(f\"❌ Failed to start server: {e}\")
        print(\"💡 Try running with: python simple_backend.py\")
''')

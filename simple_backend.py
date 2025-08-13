#!/usr/bin/env python3
"""
Simplified Flask Backend for Medical Fact Verifier Extension
"""

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
    """API endpoint for medical fact verification"""
    
    if request.method == 'OPTIONS':
        # Handle preflight request
        return '', 200
    
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({'error': 'Missing required field: text'}), 400
        
        text = data['text']
        source_url = data.get('source_url', '')
        
        print(f"📥 Verification request: {text[:50]}...")
        
        # Simple classification
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['cure cancer', 'bleach', 'vaccines cause autism']):
            status = 'harmful'
            fact = "This claim is dangerous misinformation."
            explanation = "Contradicts medical evidence and could cause harm."
        elif any(word in text_lower for word in ['natural sugar', 'essential oils']):
            status = 'caution'
            fact = "This claim needs professional verification."
            explanation = "Partially true but requires medical context."
        else:
            status = 'safe'
            fact = "This information appears reasonable."
            explanation = "Aligns with general medical guidance."
        
        response = {
            'status': status,
            'corrected_fact': fact,
            'explanation': explanation,
            'source_links': [
                'https://www.who.int/',
                'https://www.cdc.gov/',
                'https://pubmed.ncbi.nlm.nih.gov/'
            ]
        }
        
        print(f"✅ Response: {status}")
        return jsonify(response)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({
            'error': str(e),
            'status': 'error',
            'corrected_fact': 'Unable to verify claim.',
            'explanation': 'Please try again later.',
            'source_links': ['https://www.who.int/']
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Medical Fact Verifier API'
    })

@app.route('/', methods=['GET'])
def home():
    """Root endpoint"""
    return jsonify({
        'service': 'Medical Fact Verifier API',
        'status': 'running'
    })

if __name__ == '__main__':
    print("🏥 Starting Simple Medical Fact Verifier Backend...")
    print("📍 Server: http://localhost:5000")
    print("🔗 API: http://localhost:5000/api/verify")
    
    try:
        app.run(host='127.0.0.1', port=5000, debug=False)
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        print("💡 Try running with: python simple_backend.py")

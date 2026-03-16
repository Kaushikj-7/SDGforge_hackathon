import google.generativeai as genai
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
import time
import base64
import PIL.Image
import io

app = Flask(__name__)
CORS(app)

# Configuration
GEMINI_API_KEY = "AIzaSyCnyKic-UqewPDfETN0dzlWmz3EeA9NsaY"
genai.configure(api_key=GEMINI_API_KEY)

# System Prompt for medical verification
SYSTEM_PROMPT = """
You are a Medical Fact Verifier AI. Your task is to analyze medical claims and provide a verdict.
Status must be one of: "safe", "caution", "harmful".
- "safe": Fact is accurate according to medical consensus.
- "caution": Fact is partially true, lacks context, or evidence is mixed.
- "harmful": Fact is dangerously incorrect or contradicts established medical safety.

You MUST respond in valid JSON format only:
{
  "status": "safe" | "caution" | "harmful",
  "corrected_fact": "A concise correction or confirmation of the claim",
  "explanation": "A detailed medical explanation",
  "source_links": ["https://who.int", "https://cdc.gov"],
  "proof_chain": [{"node": "Step 1"}, {"node": "Step 2"}]
}
"""

@app.route('/', methods=['GET'])
def index():
    return jsonify({"message": "Medical Fact Verifier Gemini API is running", "endpoints": ["/status", "/api/health", "/api/verify"]})

@app.route('/status', methods=['GET'])
def get_status():
    return jsonify({"status": "online", "model": "gemini-1.5-flash"})

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok", "timestamp": time.time()})

@app.route('/api/verify', methods=['POST'])
def verify_fact():
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400

    text = data.get('text', '')
    context = data.get('context', '')
    extraction_mode = data.get('extraction_mode', 'text')
    image_data = data.get('image_data', '')

    print(f"[*] Verifying fact using Gemini ({extraction_mode})...")

    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        if extraction_mode == "vision" and image_data:
            # Decode base64 image
            img_bytes = base64.b64decode(image_data)
            img = PIL.Image.open(io.BytesIO(img_bytes))
            
            prompt = f"{SYSTEM_PROMPT}\n\nAnalyze the medical claim in this image and its context: {context}"
            response = model.generate_content([prompt, img])
        else:
            prompt = f"{SYSTEM_PROMPT}\n\nClaim: {text}\nContext: {context}"
            response = model.generate_content(prompt)

        # Parse JSON response from Gemini
        try:
            # Clean response text (remove markdown backticks if present)
            clean_text = response.text.strip()
            if clean_text.startswith("```json"):
                clean_text = clean_text[7:-3].strip()
            elif clean_text.startswith("```"):
                clean_text = clean_text[3:-3].strip()
                
            result = json.loads(clean_text)
            return jsonify(result)
        except Exception as parse_err:
            print(f"Parse error: {parse_err}\nRaw content: {response.text}")
            return jsonify({
                "status": "caution",
                "corrected_fact": "Unable to parse AI response.",
                "explanation": "The AI provided a response but it was not in the expected format. Raw response: " + response.text[:200],
                "source_links": [],
                "proof_chain": []
            })

    except Exception as e:
        print(f"Gemini API Error: {e}")
        return jsonify({
            "status": "error",
            "corrected_fact": "AI Verification Failed",
            "explanation": str(e),
            "source_links": [],
            "proof_chain": []
        }), 500

if __name__ == '__main__':
    print("🚀 Medical Fact Verifier Gemini Backend starting on http://localhost:5001")
    app.run(host='0.0.0.0', port=5001, debug=True)

if __name__ == '__main__':
    print("🚀 Medical Fact Verifier Backend starting on http://localhost:5001")
    app.run(host='0.0.0.0', port=5001, debug=True)

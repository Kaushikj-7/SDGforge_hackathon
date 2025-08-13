#!/usr/bin/env python3
"""
Ultra Simple Backend for Extension Testing
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.parse

class MedicalFactHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        if self.path == '/api/health':
            response = {'status': 'healthy', 'service': 'Medical Fact Verifier'}
        else:
            response = {'service': 'Medical Fact Verifier API', 'status': 'running'}
        
        self.wfile.write(json.dumps(response).encode())
    
    def do_POST(self):
        """Handle POST requests"""
        if self.path == '/api/verify':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                
                text = data.get('text', '').lower()
                print(f"📥 Verifying: {text[:50]}...")
                
                # Simple classification
                if any(word in text for word in ['cure cancer', 'bleach', 'vaccines cause autism']):
                    status = 'harmful'
                    fact = "This claim is dangerous misinformation that could cause harm."
                elif any(word in text for word in ['natural sugar', 'essential oils']):
                    status = 'caution'
                    fact = "This claim requires professional medical verification."
                else:
                    status = 'safe'
                    fact = "This information appears to be reasonable medical guidance."
                
                response = {
                    'status': status,
                    'corrected_fact': fact,
                    'explanation': f"Medical assessment based on current evidence.",
                    'source_links': [
                        'https://www.who.int/',
                        'https://www.cdc.gov/',
                        'https://pubmed.ncbi.nlm.nih.gov/'
                    ]
                }
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode())
                
                print(f"✅ Response sent: {status}")
                
            except Exception as e:
                print(f"❌ Error: {e}")
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                error_response = {
                    'status': 'error',
                    'corrected_fact': 'Unable to verify claim.',
                    'explanation': 'Server error occurred.',
                    'source_links': ['https://www.who.int/']
                }
                self.wfile.write(json.dumps(error_response).encode())

if __name__ == '__main__':
    print("🏥 Medical Fact Verifier Backend Server")
    print("=" * 40)
    print("📍 Server: http://localhost:5000")
    print("🔗 API: http://localhost:5000/api/verify")
    print("✅ CORS enabled for browser extension")
    print("=" * 40)
    
    server = HTTPServer(('localhost', 5000), MedicalFactHandler)
    
    try:
        print("🚀 Server starting...")
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
        server.server_close()

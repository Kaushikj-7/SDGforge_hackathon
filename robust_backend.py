#!/usr/bin/env python3
"""
Robust Backend for Extension Testing - Never stops!
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.parse
import traceback
import signal
import sys

class MedicalFactHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        """Override to provide better logging"""
        print(f"🌐 {self.address_string()} - {format % args}")
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        try:
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            print("✅ CORS preflight handled")
        except Exception as e:
            print(f"❌ CORS error: {e}")
    
    def do_GET(self):
        """Handle GET requests"""
        try:
            print(f"📥 GET request: {self.path}")
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            if self.path == '/api/health':
                response = {'status': 'healthy', 'service': 'Medical Fact Verifier'}
                print("💚 Health check requested")
            elif self.path == '/favicon.ico':
                response = {'message': 'No favicon available'}
                print("🎨 Favicon requested")
            else:
                response = {'service': 'Medical Fact Verifier API', 'status': 'running'}
                print("📋 Default API info sent")
            
            self.wfile.write(json.dumps(response).encode())
            print(f"✅ GET response sent successfully")
            
        except Exception as e:
            print(f"❌ GET error: {e}")
            traceback.print_exc()
            try:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Server error'}).encode())
            except:
                pass
    
    def do_POST(self):
        """Handle POST requests"""
        try:
            print(f"📥 POST request: {self.path}")
            
            if self.path == '/api/verify':
                content_length = int(self.headers.get('Content-Length', 0))
                if content_length > 0:
                    post_data = self.rfile.read(content_length)
                    data = json.loads(post_data.decode('utf-8'))
                    text = data.get('text', '').lower()
                    print(f"🔍 Verifying: {text[:50]}...")
                else:
                    text = ""
                    print("⚠️ Empty POST data")
                
                # Enhanced classification logic with detailed responses
                if any(word in text for word in ['cure cancer', 'bleach', 'drinking bleach', 'vaccines cause autism', 'essential oils cure', 'miracle cure']):
                    status = 'harmful'
                    fact = "⚠️ DANGEROUS: This claim is harmful misinformation that could cause serious health risks."
                    explanation = "Medical misinformation can lead to dangerous self-treatment, delayed medical care, or rejection of proven treatments. Always consult healthcare professionals for medical advice."
                    sources = [
                        'https://www.who.int/news-room/feature-stories/detail/how-to-report-misinformation-online',
                        'https://www.cdc.gov/healthliteracy/researchevaluate.html',
                        'https://pubmed.ncbi.nlm.nih.gov/34234532/'
                    ]
                elif any(word in text for word in ['natural remedy', 'herbal medicine', 'supplement', 'alternative treatment']):
                    status = 'caution'
                    fact = "⚠️ CAUTION: Natural remedies may have benefits but require professional medical verification."
                    explanation = "While some natural treatments have evidence, others may be unproven or interact dangerously with medications. Always discuss with your healthcare provider before trying alternatives."
                    sources = [
                        'https://www.nccih.nih.gov/health/be-an-informed-consumer',
                        'https://www.fda.gov/consumers/consumer-updates/dietary-supplements',
                        'https://pubmed.ncbi.nlm.nih.gov/'
                    ]
                elif any(word in text for word in ['vaccine', 'vaccination', 'exercise', 'diet', 'nutrition', 'sleep', 'hydration']):
                    status = 'safe'
                    fact = "✅ SAFE: This information aligns with established medical guidelines."
                    explanation = "This content appears to follow evidence-based medical recommendations. However, individual health needs vary, so consult your healthcare provider for personalized advice."
                    sources = [
                        'https://www.cdc.gov/vaccines/vac-gen/side-effects.htm',
                        'https://www.who.int/news-room/fact-sheets/detail/physical-activity',
                        'https://www.nih.gov/health-information'
                    ]
                else:
                    status = 'safe'
                    fact = "ℹ️ This information appears to be general health guidance."
                    explanation = "While this content doesn't appear harmful, always verify health information with qualified healthcare professionals."
                    sources = [
                        'https://www.who.int/',
                        'https://www.cdc.gov/',
                        'https://pubmed.ncbi.nlm.nih.gov/'
                    ]
                
                response = {
                    'status': status,
                    'corrected_fact': fact,
                    'explanation': explanation,
                    'source_links': sources,
                    'original_text': text[:100] + ('...' if len(text) > 100 else ''),
                    'verification_timestamp': __import__('datetime').datetime.now().isoformat()
                }
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode())
                
                print(f"✅ Verification response sent: {status}")
            else:
                print(f"❓ Unknown POST path: {self.path}")
                self.send_response(404)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Not found'}).encode())
                
        except Exception as e:
            print(f"❌ POST error: {e}")
            traceback.print_exc()
            try:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                error_response = {
                    'status': 'error',
                    'corrected_fact': '❌ Unable to verify this medical claim due to a server error.',
                    'explanation': 'The verification service encountered an error. Please try again or consult healthcare professionals for medical advice.',
                    'source_links': [
                        'https://www.who.int/',
                        'https://www.cdc.gov/healthliteracy/',
                        'https://medlineplus.gov/'
                    ],
                    'original_text': '',
                    'verification_timestamp': __import__('datetime').datetime.now().isoformat()
                }
                self.wfile.write(json.dumps(error_response).encode())
            except:
                pass

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print('\n🛑 Received interrupt signal')
    print('👋 Server shutting down gracefully...')
    sys.exit(0)

if __name__ == '__main__':
    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    print("🏥 ROBUST Medical Fact Verifier Backend Server")
    print("=" * 50)
    print("📍 Server: http://localhost:5000")
    print("🔗 API: http://localhost:5000/api/verify")
    print("💚 Health: http://localhost:5000/api/health")
    print("✅ CORS enabled for browser extension")
    print("🛡️ Error handling: ROBUST mode")
    print("=" * 50)
    
    server = HTTPServer(('localhost', 5000), MedicalFactHandler)
    
    try:
        print("🚀 Server starting in ROBUST mode...")
        print("💡 Press Ctrl+C to stop")
        print("🔄 Server will keep running until manually stopped")
        print("-" * 50)
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n💥 Server crashed: {e}")
        traceback.print_exc()
    finally:
        print("🧹 Cleaning up...")
        server.server_close()
        print("👋 Goodbye!")

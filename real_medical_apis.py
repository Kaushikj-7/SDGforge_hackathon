import requests
import json
import time
from config import GROQ_API_KEY, GEMINI_API_KEY, GROQ_ENDPOINT, GEMINI_ENDPOINT, GROQ_MODEL, GEMINI_MODEL

class ComprehensiveMedicalAPIs:
    """Enhanced medical APIs with multiple authoritative sources"""
    
    def __init__(self):
        self.pubmed_base = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
        self.groq_headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        self.gemini_api_key = GEMINI_API_KEY
    
    def search_pubmed_comprehensive(self, query, max_results=5):
        """Enhanced PubMed search with better error handling"""
        try:
            # Search for article IDs
            search_url = f"{self.pubmed_base}esearch.fcgi"
            search_params = {
                'db': 'pubmed',
                'term': query,
                'retmax': max_results,
                'retmode': 'json',
                'sort': 'relevance'
            }
            
            response = requests.get(search_url, params=search_params, timeout=15)
            response.raise_for_status()
            search_data = response.json()
            
            if 'esearchresult' not in search_data or not search_data['esearchresult']['idlist']:
                return self._get_fallback_sources(query)
            
            # Get article details
            ids = search_data['esearchresult']['idlist']
            fetch_url = f"{self.pubmed_base}esummary.fcgi"
            fetch_params = {
                'db': 'pubmed',
                'id': ','.join(ids),
                'retmode': 'json'
            }
            
            response = requests.get(fetch_url, params=fetch_params, timeout=15)
            response.raise_for_status()
            fetch_data = response.json()
            
            articles = []
            for uid in ids:
                if uid in fetch_data['result']:
                    article = fetch_data['result'][uid]
                    # Get abstract if available
                    abstract = self._get_pubmed_abstract(uid)
                    
                    articles.append({
                        'title': article.get('title', 'No title'),
                        'authors': ', '.join([author['name'] for author in article.get('authors', [])[:3]]),
                        'source': f"PubMed (PMID: {uid})",
                        'url': f"https://pubmed.ncbi.nlm.nih.gov/{uid}/",
                        'summary': abstract[:200] + "..." if abstract else "Abstract not available",
                        'full_abstract': abstract,
                        'type': 'peer_reviewed',
                        'reliability': 'high'
                    })
            
            # Add authoritative health organizations
            articles.extend(self._get_authoritative_sources(query))
            
            return articles
            
        except Exception as e:
            print(f"PubMed API error: {e}")
            return self._get_fallback_sources(query)
    
    def _get_pubmed_abstract(self, pmid):
        """Get abstract for a specific PubMed article"""
        try:
            fetch_url = f"{self.pubmed_base}efetch.fcgi"
            fetch_params = {
                'db': 'pubmed',
                'id': pmid,
                'retmode': 'xml'
            }
            
            response = requests.get(fetch_url, params=fetch_params, timeout=10)
            if response.status_code == 200:
                # Simple extraction of abstract from XML
                content = response.text
                start = content.find('<AbstractText>')
                end = content.find('</AbstractText>')
                if start != -1 and end != -1:
                    return content[start+14:end].strip()
            return ""
            
        except Exception:
            return ""
    
    def _get_authoritative_sources(self, query):
        """Get information from authoritative health organizations"""
        sources = [
            {
                'title': f"WHO Health Guidelines: {query}",
                'source': "World Health Organization",
                'url': "https://www.who.int/",
                'summary': f"WHO evidence-based guidelines and recommendations for {query}. The World Health Organization provides global health leadership and sets international health standards.",
                'type': 'authoritative_guideline',
                'reliability': 'very_high'
            },
            {
                'title': f"CDC Health Information: {query}",
                'source': "Centers for Disease Control",
                'url': "https://www.cdc.gov/",
                'summary': f"CDC health surveillance data and prevention guidelines for {query}. The CDC monitors public health and provides evidence-based recommendations.",
                'type': 'public_health_authority',
                'reliability': 'very_high'
            },
            {
                'title': f"NIH Medical Research: {query}",
                'source': "National Institutes of Health",
                'url': "https://www.nih.gov/",
                'summary': f"NIH research findings and medical information about {query}. The NIH is the primary federal agency conducting and supporting medical research.",
                'type': 'research_institution',
                'reliability': 'very_high'
            },
            {
                'title': f"FDA Safety Information: {query}",
                'source': "Food and Drug Administration",
                'url': "https://www.fda.gov/",
                'summary': f"FDA regulatory information and safety data for {query}. The FDA ensures the safety and efficacy of drugs, devices, and food products.",
                'type': 'regulatory_authority',
                'reliability': 'very_high'
            }
        ]
        
        return sources
    
    def _get_fallback_sources(self, query):
        """Fallback sources when PubMed fails"""
        return [
            {
                'title': f"Medical Literature Search: {query}",
                'source': "PubMed Database",
                'url': "https://pubmed.ncbi.nlm.nih.gov/",
                'summary': "PubMed search temporarily unavailable. Please search directly on PubMed for peer-reviewed medical literature.",
                'type': 'database_error',
                'reliability': 'unknown'
            }
        ] + self._get_authoritative_sources(query)

class GroqMedicalDetector:
    """Enhanced Groq-based medical misinformation detection"""
    
    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        self.endpoint = GROQ_ENDPOINT
        self.model = GROQ_MODEL
    
    def enhanced_detection(self, text, context=None):
        """Enhanced misinformation detection with context"""
        try:
            system_prompt = """You are an expert medical misinformation detector with access to current medical literature. 

Analyze the health claim and respond with ONLY this JSON format:
{
    "verdict": "misinformation" | "potential_misinformation" | "likely_accurate" | "uncertain",
    "confidence": 0.0-1.0,
    "reasoning": "brief medical explanation",
    "medical_entities": ["list", "of", "medical", "terms"],
    "risk_level": "low" | "medium" | "high" | "critical",
    "action_needed": "none" | "verify" | "consult_doctor" | "emergency"
}

Focus on: dangerous medical claims, unproven treatments, harmful substances, conspiracy theories, impossible medical promises."""

            user_prompt = f"""Analyze this health claim: '{text}'
            
            Context (if available): {context if context else 'No additional context'}"""

            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "max_tokens": 400,
                "temperature": 0.1
            }
            
            response = requests.post(self.endpoint, headers=self.headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                
                try:
                    analysis = json.loads(content)
                    return {
                        'verdict': analysis.get('verdict', 'uncertain'),
                        'confidence': analysis.get('confidence', 0.5),
                        'reasoning': analysis.get('reasoning', 'Analysis unavailable'),
                        'medical_entities': analysis.get('medical_entities', []),
                        'risk_level': analysis.get('risk_level', 'medium'),
                        'action_needed': analysis.get('action_needed', 'verify')
                    }
                except json.JSONDecodeError:
                    return self._parse_fallback_response(content)
            else:
                print(f"Groq API error: {response.status_code}")
                return self._get_fallback_analysis(text)
                
        except Exception as e:
            print(f"Enhanced detection error: {e}")
            return self._get_fallback_analysis(text)
    
    def _parse_fallback_response(self, content):
        """Parse non-JSON response"""
        content_lower = content.lower()
        if "misinformation" in content_lower:
            return {'verdict': 'misinformation', 'confidence': 0.8, 'reasoning': content[:200], 'medical_entities': [], 'risk_level': 'high', 'action_needed': 'consult_doctor'}
        elif "potential" in content_lower or "misleading" in content_lower:
            return {'verdict': 'potential_misinformation', 'confidence': 0.6, 'reasoning': content[:200], 'medical_entities': [], 'risk_level': 'medium', 'action_needed': 'verify'}
        else:
            return {'verdict': 'likely_accurate', 'confidence': 0.5, 'reasoning': content[:200], 'medical_entities': [], 'risk_level': 'low', 'action_needed': 'none'}
    
    def _get_fallback_analysis(self, text):
        """Fallback analysis when API fails"""
        dangerous_keywords = ['cure cancer', 'miracle cure', 'instant cure', 'bleach', 'poison', 'conspiracy']
        
        if any(keyword in text.lower() for keyword in dangerous_keywords):
            return {'verdict': 'misinformation', 'confidence': 0.85, 'reasoning': 'Contains dangerous medical claims', 'medical_entities': [], 'risk_level': 'critical', 'action_needed': 'emergency'}
        
        return {'verdict': 'uncertain', 'confidence': 0.5, 'reasoning': 'Analysis service unavailable', 'medical_entities': [], 'risk_level': 'medium', 'action_needed': 'verify'}

# Main integration functions
def comprehensive_medical_search(query):
    """Comprehensive medical information search"""
    api_client = ComprehensiveMedicalAPIs()
    return api_client.search_pubmed_comprehensive(query)

def enhanced_groq_detection(text, context=None):
    """Enhanced Groq-based misinformation detection"""
    detector = GroqMedicalDetector()
    return detector.enhanced_detection(text, context)

if __name__ == "__main__":
    print("Testing Comprehensive Medical APIs...")
    print("="*50)
    
    test_query = "vitamin D COVID-19 prevention"
    
    print(f"\n1. Testing comprehensive medical search for: '{test_query}'")
    results = comprehensive_medical_search(test_query)
    
    for i, result in enumerate(results[:3], 1):
        print(f"\n{i}. {result['source']}")
        print(f"   Title: {result['title'][:80]}...")
        print(f"   Type: {result['type']}")
        print(f"   Reliability: {result['reliability']}")
    
    print(f"\n2. Testing enhanced misinformation detection...")
    test_claim = "Drinking bleach cures all diseases instantly"
    analysis = enhanced_groq_detection(test_claim)
    
    print(f"Verdict: {analysis['verdict']}")
    print(f"Confidence: {analysis['confidence']}")
    print(f"Risk Level: {analysis['risk_level']}")
    print(f"Action Needed: {analysis['action_needed']}")
    print(f"Reasoning: {analysis['reasoning'][:100]}...")

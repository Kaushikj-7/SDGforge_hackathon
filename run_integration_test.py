import sys
import os
import json

# Add parent directory to path so we can import simple_backend
import simple_backend
from flask import Flask

client = simple_backend.app.test_client()

print("\n--- Running Integration Test ---")

# We will mock the phases directly on simple_backend module to avoid calling external APIs
def mock_classify_input_type(text):
    return {'type': 'text'}

def mock_retrieve_content(data):
    return {'content': data.get('content', '')}

def mock_detect_misinformation(claim, context=None, user_profile=None):
    return {
        'verdict': 'misinformation',
        'confidence': 0.95,
        'risk_level': 'high',
        'reasoning': 'Bleach is extremely toxic.',
        'medical_entities': ['bleach', 'COVID-19'],
        'action_needed': 'Do not consume'
    }

def mock_retrieve_trusted_sources(query, max_results=3, force_test=False):
    return [
        {'source': 'WHO', 'title': 'COVID Mythbusters', 'url': 'https://who.int'}
    ]

def mock_correct_misinformation_with_chain(claim, sources, misinformation_analysis, proof_chain_input=None):
    proof_chain = proof_chain_input.copy() if proof_chain_input else []
    proof_chain.append({'node': 'Mock Fact-Check', 'type': 'fact_check'})
    return {
        'corrected_fact': 'Bleach is toxic and does not cure COVID-19.',
        'proof_chain': proof_chain
    }

# Apply mocks
simple_backend.classify_input_type = mock_classify_input_type
simple_backend.retrieve_content = mock_retrieve_content
simple_backend.detect_misinformation = mock_detect_misinformation
simple_backend.retrieve_trusted_sources = mock_retrieve_trusted_sources
simple_backend.correct_misinformation_with_chain = mock_correct_misinformation_with_chain

payload = {
    'text': 'Drinking bleach cures COVID-19',
    'extraction_mode': 'text',
    'context': 'Found on Facebook',
    'user_profile': {
        'age_group': 'adult',
        'conditions': []
    }
}

response = client.post('/api/verify', 
                        data=json.dumps(payload),
                        content_type='application/json')

print(f"Status Code: {response.status_code}")
data = json.loads(response.data)

print("Response JSON:")
print(json.dumps(data, indent=2))

assert response.status_code == 200
assert data['status'] == 'harmful'
assert 'Bleach is toxic' in data['corrected_fact']
assert 'proof_chain' in data
assert len(data['proof_chain']) > 0

print("\n✅ INTEGRATION TEST PASSED: Full complete pipeline simulated with Mock payloads executed safely.")

import asyncio
from backend.real_medical_apis import ComprehensiveMedicalAPIs

api_client = ComprehensiveMedicalAPIs()

def semantic_search(query: str, n_results: int = 3) -> list:
    '''Real real-time RAG fetching from NIH pubmed via API!'''
    try:
        results = api_client.search_pubmed_comprehensive(query, max_results=n_results)
        hits = []
        for r in results:
            hits.append({
                'source': r.get('source', 'PubMed'),
                'url': r.get('url', 'https://pubmed.ncbi.nlm.nih.gov/'),
                'text': r.get('summary', '') or r.get('title', ''),
                'score': 0.8
            })
        return hits
    except Exception as e:
        print(f"RAG Error: {e}")
        return []

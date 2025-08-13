#!/usr/bin/env python3
"""
Phase 2: Content Retrieval
Extracts content from URLs, processes articles, messages
"""

import requests
from urllib.parse import urlparse

def retrieve_content(input_data):
    """Retrieve and process content based on input type"""
    print("🔍 Phase 2: Content Analysis...")
    
    input_type = input_data.get('type', 'plain_text')
    content = input_data.get('content', '')
    
    if input_type == 'url':
        return extract_from_url(content)
    elif input_type == 'forwarded_message':
        return process_forwarded_message(content)
    elif input_type == 'article':
        return process_article_content(content)
    else:
        return process_plain_text(content)

def extract_from_url(url):
    """Extract content from URL"""
    try:
        print(f"🌐 Fetching content from: {url[:50]}...")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            # Simple text extraction (would use BeautifulSoup in production)
            content = response.text
            
            # Extract title (simple method)
            title_start = content.find('<title>')
            title_end = content.find('</title>')
            if title_start != -1 and title_end != -1:
                title = content[title_start+7:title_end].strip()
            else:
                title = "Web Article"
            
            # Simple content extraction (remove HTML tags)
            import re
            
            # Remove script and style tags completely
            content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL | re.IGNORECASE)
            content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL | re.IGNORECASE)
            
            # Remove HTML tags
            text_content = re.sub('<[^<]+?>', '', content)
            
            # Clean up whitespace and special characters
            text_content = re.sub(r'\s+', ' ', text_content).strip()
            text_content = re.sub(r'[^\w\s.,!?;:()\-\'"]+', ' ', text_content)
            
            # Try to extract main content (look for common content indicators)
            paragraphs = text_content.split('.')
            meaningful_paragraphs = [p.strip() for p in paragraphs if len(p.strip()) > 50 and not any(keyword in p.lower() for keyword in ['javascript', 'script', 'function', 'var ', 'window.', 'document.'])]
            
            if meaningful_paragraphs:
                clean_content = '. '.join(meaningful_paragraphs[:10])  # Take first 10 meaningful paragraphs
            else:
                clean_content = text_content[:1000]  # Fallback to first 1000 chars
            
            return {
                'type': 'url',
                'source': urlparse(url).netloc,
                'title': title,
                'content': clean_content[:2000],  # Limit content
                'url': url
            }
        else:
            print(f"⚠️ Failed to fetch URL (status: {response.status_code})")
            return {
                'type': 'url',
                'source': 'Web',
                'title': 'Unable to fetch content',
                'content': f"URL provided: {url}",
                'url': url
            }
            
    except Exception as e:
        print(f"❌ URL extraction error: {e}")
        return {
            'type': 'url',
            'source': 'Web',
            'title': 'Error fetching content',
            'content': f"URL provided: {url}",
            'url': url
        }

def process_forwarded_message(content):
    """Process forwarded message content"""
    # Clean forwarded message indicators
    cleaned = content.replace('Forwarded', '').replace('FWD:', '').strip()
    
    return {
        'type': 'forwarded_message',
        'source': 'Forwarded Message',
        'title': 'Forwarded Health Information',
        'content': cleaned,
        'original_length': len(content)
    }

def process_article_content(content):
    """Process article content"""
    # Extract potential title (first line if it looks like a title)
    lines = content.split('\n')
    potential_title = lines[0].strip() if lines else "Health Article"
    
    # If first line is short and doesn't end with punctuation, it might be a title
    if len(potential_title) < 100 and not potential_title.endswith(('.', '!', '?')):
        title = potential_title
        article_content = '\n'.join(lines[1:]).strip()
    else:
        title = "Health Article"
        article_content = content
    
    return {
        'type': 'article',
        'source': 'Article Text',
        'title': title,
        'content': article_content,
        'word_count': len(article_content.split())
    }

def process_plain_text(content):
    """Process plain text health claim"""
    return {
        'type': 'plain_text',
        'source': 'User Input',
        'title': 'Health Claim',
        'content': content,
        'length': len(content)
    }

if __name__ == "__main__":
    # Test the module
    test_inputs = [
        {'type': 'plain_text', 'content': 'Vaccines cause autism'},
        {'type': 'url', 'content': 'https://www.who.int/news'},
        {'type': 'forwarded_message', 'content': 'Forwarded: Drink lemon water to cure cancer'}
    ]
    
    for test_input in test_inputs:
        print(f"\nTesting: {test_input['type']}")
        result = retrieve_content(test_input)
        print(f"Result: {result['title']}")
        print(f"Content: {result['content'][:50]}...")

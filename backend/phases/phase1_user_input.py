#!/usr/bin/env python3
"""
Phase 1: User Input Processing
Handles different types of health-related input
"""

def get_user_input():
    """Get and validate user input"""
    print("📥 Phase 1: Input Processing...")
    print("Enter any of the following:")
    print("• Website URL (e.g., news article about health)")
    print("• Forwarded message from WhatsApp/Telegram")
    print("• Copy-pasted article content")
    print("• Plain health claim")
    print("-" * 40)
    
    user_input = input("Paste your content here: ").strip()
    
    if not user_input:
        raise ValueError("No input provided")
    
    print(f"✅ Input received ({len(user_input)} characters)")
    return user_input

def classify_input_type(user_input):
    """Classify the type of input"""
    # Check if input is URL
    if user_input.startswith(('http://', 'https://')):
        return {
            'type': 'url',
            'source': 'Web URL',
            'content': user_input,
            'title': 'Web Article'
        }
    # Check for forwarded message indicators
    elif any(indicator in user_input.lower() for indicator in ['forwarded', 'fwd:', 'forward']):
        return {
            'type': 'forwarded_message',
            'source': 'Forwarded Message',
            'content': user_input,
            'title': 'Forwarded Health Information'
        }
    # Check if it's a long article
    elif len(user_input) > 500:
        return {
            'type': 'article',
            'source': 'Article Text',
            'content': user_input,
            'title': 'Health Article'
        }
    # Default to plain text
    else:
        return {
            'type': 'plain_text',
            'source': 'User Input',
            'content': user_input,
            'title': 'Health Claim'
        }

if __name__ == "__main__":
    # Test the module
    try:
        user_input = get_user_input()
        classification = classify_input_type(user_input)
        print(f"Input classified as: {classification['type']}")
        print(f"Source: {classification['source']}")
    except Exception as e:
        print(f"Error: {e}")

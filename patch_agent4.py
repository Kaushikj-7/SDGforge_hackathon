import re

with open('backend/agents/agent4_correction.py', 'r', encoding='utf-8') as f:
    text = f.read()

new_prompt = '''PROMPT = """You are a public health educator focusing on health equity. A user has highlighted this health claim.

Claim: "{claim}"
Evidence from trusted sources: {evidence_snippets}
Groq initial verdict: {groq_verdict}

First, deeply analyze the claim. Then write a CLEAR, COMPASSionate, and EXTREMELY SIMPLE correction for a general audience with an 8th-grade reading level. Break down any complex medical terms.

Respond ONLY with valid JSON:'''
text = re.sub(r'PROMPT = """You are a public health educator.*?Respond ONLY with valid JSON:', new_prompt, text, flags=re.DOTALL)

with open('backend/agents/agent4_correction.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("Updated Agent 4 Prompt for Simplicity")

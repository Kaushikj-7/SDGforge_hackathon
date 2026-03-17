import re

with open('backend/preprocessing/translator.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = re.sub(r'prompt = f"Translate this health fact-check correction to \{lang_name\}[^"]*Return ONLY the translated\s*correction text\.\s*Correction: \{correction\}"', 'prompt = f"Translate this health fact-check correction to {lang_name} (easy to understand local dialect, simple words, like explaining to a 10-year-old). Keep all scientific terms accurate. Return ONLY the translated correction text.\\n\\nCorrection: {correction}"', text, flags=re.MULTILINE|re.DOTALL)

with open('backend/preprocessing/translator.py', 'w', encoding='utf-8') as f:
    f.write(text)

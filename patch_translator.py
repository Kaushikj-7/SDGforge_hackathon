import re

with open('backend/preprocessing/translator.py', 'r', encoding='utf-8') as f:
    text = f.read()

new_prompt = 'prompt = f"Translate this health fact-check correction to {lang_name} (easy to understand local dialect, simple words, like explaining to a 10-year-old). Keep all scientific terms accurate. Return ONLY the translated correction text.\\n\\nCorrection: {correction}"'
text = re.sub(r'prompt = f"Translate this health fact-check correction to \{lang_name\} \(easy to understand local dialect\)\. Keep all scientific terms accurate\. Return ONLY the translated correction text\.\\n\\nCorrection: \{correction\}"', new_prompt, text)

with open('backend/preprocessing/translator.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("Updated Translator Prompt for Simplicity")

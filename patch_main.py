import re

with open('backend/main.py', 'r', encoding='utf-8') as f:
    code = f.read()

vision_import = 'from backend.preprocessing.vision import extract_text_from_image\n'
if 'vision import' not in code:
    code = code.replace('from backend.db.models import VerifyRequest', vision_import + 'from backend.db.models import VerifyRequest')

new_end = '''@app.post("/verify/image")
async def verify_image(file: UploadFile = File(...)):
    contents = await file.read()
    text = await extract_text_from_image(contents)
    if not text:
        return {"error": "Could not extract text"}
    return {"extracted_text": text}'''

code = re.sub(r'@app\.post\("/verify/image"\)\s*async def verify_image\(file: UploadFile = File\(\.\.\.\)\):\s*# Placeholder\s*return \{"error"[^\}]+\}', new_end, code)

with open('backend/main.py', 'w', encoding='utf-8') as f:
    f.write(code)

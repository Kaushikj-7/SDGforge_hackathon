import re

with open('backend/main.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Add translation import if needed
if "translate_correction" not in code:
    code = code.replace("from backend.preprocessing.translator import translate_to_english", "from backend.preprocessing.translator import translate_to_english, translate_correction")

injection = """
        yield f"data: {json.dumps({'status': 'translating', 'message': 'Generating easy Hindi & Kannada translations...'})}\\n\\n"
        hi_trans, kn_trans = await asyncio.gather(
            translate_correction(a4.get("correction", ""), [], "hi"),
            translate_correction(a4.get("correction", ""), [], "kn")
        )
        
        result["regional_translations"] = {
            "Hindi": hi_trans.get("correction", ""),
            "Kannada": kn_trans.get("correction", "")
        }
"""

# Find where 'result = aggregate' is and inject after it
if "result = aggregate(a1, a2, a3, a4, a5)" in code and "regional_translations" not in code:
    code = code.replace(
        "result = aggregate(a1, a2, a3, a4, a5)",
        "result = aggregate(a1, a2, a3, a4, a5)\n" + injection
    )

with open('backend/main.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("Patched main.py for Hindi/Kannada")

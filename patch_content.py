import re

with open('extension/content.js', 'r', encoding='utf-8') as f:
    code = f.read()

# Increase card max-width
code = code.replace("max-width: 360px;", "max-width: 500px;\n      max-height: 80vh;\n      overflow-y: auto;")
code = code.replace("min-width: 280px;", "min-width: 380px;")

# Add translation UI
ui_injection = '''
    const sourcePills = (verdict.sources || [])
      .slice(0, 3)
      .map(s => <a class="hfc-source-pill" href=" + s.url + " target="_blank"> + s.name + </a>)
      .join("");

    let translationHTML = "";
    if (verdict.regional_translations) {
        if (verdict.regional_translations.Hindi) {
            translationHTML += 
            <div style="margin-top:12px; padding-top:12px; border-top:1px solid #e0e0e0;">
                <div style="font-size:10px; color:#1a73e8; font-weight:bold; margin-bottom:4px;">🇮🇳 EASY HINDI</div>
                <div class="hfc-correction" style="font-size:12px;"> + verdict.regional_translations.Hindi + </div>
            </div>;
        }
        if (verdict.regional_translations.Kannada) {
            translationHTML += 
            <div style="margin-top:12px; padding-top:12px; border-top:1px solid #e0e0e0;">
                <div style="font-size:10px; color:#1a73e8; font-weight:bold; margin-bottom:4px;">🇮🇳 EASY KANNADA</div>
                <div class="hfc-correction" style="font-size:12px;"> + verdict.regional_translations.Kannada + </div>
            </div>;
        }
    }

'''

# replace existing let sourcePills logic
code = re.sub(
    r'const sourcePills.*?.join\(""\);',
    ui_injection.strip(),
    code,
    flags=re.DOTALL
)

# inject translationHTML into card.innerHTML
replacement = r'<div class="hfc-correction"></div>\n    \n    <div class="hfc-sources"></div>'
code = code.replace('<div class="hfc-correction"></div>\n    <div class="hfc-sources"></div>', replacement)

# if not found try older version
if 'translationHTML' not in code:
    code = code.replace('<div class="hfc-correction"></div>\n    <div class="hfc-sources"></div>', replacement)

with open('extension/content.js', 'w', encoding='utf-8') as f:
    f.write(code)

print("Patched content.js for wider popup + translatios")

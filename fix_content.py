import re

with open('extension/content.js', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('max-width: 360px;', 'max-width: 500px;\\n      max-height: 80vh;\\n      overflow-y: auto;')
text = text.replace('min-width: 280px;', 'min-width: 380px;')

new_render_verdict = '''function renderVerdict(card, verdict) {
  const riskColor = {
    CRITICAL: "#c5221f",
    HIGH:     "#b45309",
    MEDIUM:   "#92400e",
    LOW:      "#137333"
  };

  const sourcePills = (verdict.sources || [])
      .slice(0, 3)
      .map(s => <a class="hfc-source-pill" href="" target="_blank"></a>)
      .join("");

  let translationHTML = "";
  if (verdict.regional_translations) {
      if (verdict.regional_translations.Hindi) {
          translationHTML +=
          <div style="margin-top:12px; padding-top:12px; border-top:1px solid #e0e0e0;">
              <div style="font-size:10px; color:#1a73e8; font-weight:bold; margin-bottom:4px;">🇮🇳 EASY HINDI</div>
              <div class="hfc-correction" style="font-size:12px;"></div>
          </div>;
      }
      if (verdict.regional_translations.Kannada) {
          translationHTML +=
          <div style="margin-top:12px; padding-top:12px; border-top:1px solid #e0e0e0;">
              <div style="font-size:10px; color:#1a73e8; font-weight:bold; margin-bottom:4px;">🇮🇳 EASY KANNADA</div>
              <div class="hfc-correction" style="font-size:12px;"></div>
          </div>;
      }
  }

  card.innerHTML = 
    <button class="hfc-close">×</button>
    <div>
      <span class="hfc-verdict-badge hfc-">
         — 
      </span>
    </div>
    <div class="hfc-confidence-bar">
      <div class="hfc-confidence-fill" style="width:%"></div>
    </div>
    <div style="font-size:11px;color:#888;margin-bottom:6px;">
      Confidence: %
    </div>
    <div class="hfc-correction"></div>
    
    <div class="hfc-sources"></div>
  ;
  card.querySelector(".hfc-close").addEventListener("click", removeCurrentPopup);
}'''

text = re.sub(r'function renderVerdict\(card, verdict\) \{.*?\}\s*\}', new_render_verdict, text, flags=re.DOTALL)

with open('extension/content.js', 'w', encoding='utf-8') as f:
    f.write(text)

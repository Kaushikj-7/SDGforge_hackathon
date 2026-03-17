const fs = require('fs');

function patch(path) {
    let content = fs.readFileSync(path, 'utf8');
    
    // Width fix
    content = content.replace("max-width: 360px;", "max-width: 500px;\n      max-height: 80vh;\n      overflow-y: auto;");
    content = content.replace("min-width: 280px;", "min-width: 380px;");
    
    let regex = /function renderVerdict\(card, verdict\) \{([\s\S]*?)removeCurrentPopup\);\s*\}/;
    
    let newFunc = `function renderVerdict(card, verdict) {
    const riskColor = {
      CRITICAL: "#c5221f",
      HIGH:     "#b45309",
      MEDIUM:   "#92400e",
      LOW:      "#137333"
    };

    const sourcePills = (verdict.sources || [])
      .slice(0, 3)
      .map(s => \`<a class="hfc-source-pill" href="\${s.url}" target="_blank">\${s.name}</a>\`)
      .join("");

    let translationHTML = "";
    if (verdict.regional_translations) {
        if (verdict.regional_translations.Hindi) {
            translationHTML +=
            \`<div style="margin-top:12px; padding-top:12px; border-top:1px solid #e0e0e0;">
                <div style="font-size:10px; color:#1a73e8; font-weight:bold; margin-bottom:4px;">🇮🇳 EASY HINDI</div>
                <div class="hfc-correction" style="font-size:12px;">\${verdict.regional_translations.Hindi}</div>
            </div>\`;
        }
        if (verdict.regional_translations.Kannada) {
            translationHTML +=
            \`<div style="margin-top:12px; padding-top:12px; border-top:1px solid #e0e0e0;">
                <div style="font-size:10px; color:#1a73e8; font-weight:bold; margin-bottom:4px;">🇮🇳 EASY KANNADA</div>
                <div class="hfc-correction" style="font-size:12px;">\${verdict.regional_translations.Kannada}</div>
            </div>\`;
        }
    }

    card.innerHTML = \`
      <button class="hfc-close">×</button>
      <div>
        <span class="hfc-verdict-badge hfc-\${verdict.risk_level}">
          \${verdict.risk_level} — \${verdict.verdict}
        </span>
      </div>
      <div class="hfc-confidence-bar">
        <div class="hfc-confidence-fill" style="width:\${Math.round((verdict.confidence || 0) * 100)}%"></div>
      </div>
      <div style="font-size:11px;color:#888;margin-bottom:6px;">
        Confidence: \${Math.round((verdict.confidence || 0) * 100)}%
      </div>
      <div class="hfc-correction">\${verdict.correction || ""}</div>
      \${translationHTML}
      <div class="hfc-sources">\${sourcePills}</div>
    \`;
    card.querySelector(".hfc-close").addEventListener("click", removeCurrentPopup);
  }`;
    
    content = content.replace(regex, newFunc);
    fs.writeFileSync(path, content, 'utf8');
}

patch('browser-extension/content.js');
patch('extension/content.js');
console.log("Patched both files via nodejs for perfect encoding.");

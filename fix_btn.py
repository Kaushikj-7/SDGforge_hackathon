import re

with open("browser-extension/content.js", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace(
    'btn.textContent = "Check  Verify claim";', 'btn.textContent = "✓ Verify claim";'
)

with open("browser-extension/content.js", "w", encoding="utf-8") as f:
    f.write(content)
print("done")

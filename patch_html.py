import re

with open('extension/popup.html', 'r', encoding='utf-8') as f:
    html = f.read()

drop_zone = '''
    <div class="section-title" style="margin-top: 16px;">Analyze Screenshot</div>
    <div id="drop-zone" style="border: 2px dashed #1a73e8; padding: 20px; text-align: center; border-radius: 8px; margin-bottom: 16px; cursor: pointer; color: #5f6368; font-size: 12px; background: rgba(26,115,232,0.05); transition: background 0.3s;">
        Click or Drag Image Here<br><small>(WhatsApp / TikTok meme)</small>
        <input type="file" id="image-upload" accept="image/*" style="display:none">
    </div>
    <div id="image-result" style="font-size: 12px; padding: 10px; background: #e6f4ea; display: none; margin-bottom: 16px; border-radius: 6px; color: #137333;"></div>
'''
if "Analyze Screenshot" not in html:
    html = html.replace('<button id="refresh-btn"', drop_zone + '\n    <button id="refresh-btn"')
    with open('extension/popup.html', 'w', encoding='utf-8') as f:
        f.write(html)

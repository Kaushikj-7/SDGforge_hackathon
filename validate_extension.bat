@echo off
echo 🔍 Chrome Extension Validation Tool
echo =================================
echo.
echo Checking extension folder structure...
echo.

cd /d "c:\Users\Kaushik j\Downloads\SDGforge_hackathon-main\SDGforge_hackathon-main\browser-extension"

echo ✅ Extension folder: %CD%
echo.

echo 📁 Required files check:
if exist manifest.json (echo ✅ manifest.json) else (echo ❌ manifest.json MISSING)
if exist background.js (echo ✅ background.js) else (echo ❌ background.js MISSING)  
if exist content.js (echo ✅ content.js) else (echo ❌ content.js MISSING)
if exist content.css (echo ✅ content.css) else (echo ❌ content.css MISSING)
if exist popup.html (echo ✅ popup.html) else (echo ❌ popup.html MISSING)
if exist popup.js (echo ✅ popup.js) else (echo ❌ popup.js MISSING)
if exist popup.css (echo ✅ popup.css) else (echo ❌ popup.css MISSING)

echo.
echo 📝 To load in Chrome:
echo 1. Open Chrome and go to: chrome://extensions/
echo 2. Enable "Developer mode" (toggle top-right)
echo 3. Click "Load unpacked" 
echo 4. Select this folder: %CD%
echo 5. Extension should appear in the list
echo.
echo 🔗 Backend running at: http://localhost:5000
echo.

pause

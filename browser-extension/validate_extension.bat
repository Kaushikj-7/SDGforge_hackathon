@echo off
echo 🔍 Medical Fact Verifier Extension Validation
echo ===============================================

echo.
echo 📁 Checking extension files...
if exist "manifest.json" (
    echo ✅ manifest.json found
) else (
    echo ❌ manifest.json missing
    goto :error
)

if exist "background.js" (
    echo ✅ background.js found
) else (
    echo ❌ background.js missing
    goto :error
)

if exist "content.js" (
    echo ✅ content.js found
) else (
    echo ❌ content.js missing
    goto :error
)

if exist "popup.html" (
    echo ✅ popup.html found
) else (
    echo ❌ popup.html missing
    goto :error
)

if exist "popup.js" (
    echo ✅ popup.js found
) else (
    echo ❌ popup.js missing
    goto :error
)

if exist "popup.css" (
    echo ✅ popup.css found
) else (
    echo ❌ popup.css missing
    goto :error
)

if exist "content.css" (
    echo ✅ content.css found
) else (
    echo ❌ content.css missing
    goto :error
)

echo.
echo 🌐 Checking backend connectivity...
curl -s -X GET "http://localhost:5000/api/health" -H "Content-Type: application/json" > nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Backend is running and accessible
) else (
    echo ❌ Backend is not running or not accessible
    echo 💡 Please start the backend: python robust_backend.py
)

echo.
echo 📋 Extension Loading Instructions:
echo 1. Open Chrome and go to: chrome://extensions/
echo 2. Enable "Developer mode" (top-right toggle)
echo 3. Click "Load unpacked"
echo 4. Select this folder: %CD%
echo 5. Click "Select Folder"
echo.
echo 🧪 Testing Instructions:
echo 1. Visit any webpage with medical content
echo 2. Select (highlight) medical text
echo 3. Right-click and choose "Verify Medical Fact"
echo 4. Check for colored banner with verification results
echo.
echo ✅ All files validated successfully!
goto :end

:error
echo.
echo ❌ Extension validation failed!
echo Please check the missing files and try again.

:end
pause

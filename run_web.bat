@echo off
title DocuSpeak Web Launcher
echo.
echo  ========================================
echo   DocuSpeak - Web Mode (Flutter + Chrome)
echo  ========================================
echo.

REM ── Start backend ─────────────────────────────────────────────────────────
echo [1/2] Starting backend...
start "DocuSpeak Backend" /MIN cmd /c "cd /d "%~dp0backend" && python -m uvicorn main:app --host 0.0.0.0 --port 8000 --log-level info"
timeout /t 3 /nobreak >nul
echo       Backend started on http://127.0.0.1:8000
echo.

REM ── Launch Flutter web ─────────────────────────────────────────────────────
echo [2/2] Launching Flutter web app in Chrome...
cd /d "%~dp0flutter_app"
flutter run -d chrome --web-port 5000

echo.
pause

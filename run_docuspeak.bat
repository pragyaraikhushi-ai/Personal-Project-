@echo off
title DocuSpeak Launcher
echo.
echo  ========================================
echo   DocuSpeak - Document to Audio Converter
echo  ========================================
echo.

REM ── Step 1: Install backend dependencies ──────────────────────────────────
echo [1/3] Checking Python backend dependencies...
python -m pip install -r "%~dp0backend\requirements.txt" --quiet
if %errorlevel% neq 0 (
    echo ERROR: Failed to install Python dependencies.
    echo Make sure Python is installed and in PATH.
    pause
    exit /b 1
)
echo       Dependencies OK.
echo.

REM ── Step 2: Start FastAPI backend ─────────────────────────────────────────
echo [2/3] Starting FastAPI backend on http://127.0.0.1:8000 ...
start "DocuSpeak Backend" /MIN cmd /c "cd /d "%~dp0backend" && python -m uvicorn main:app --host 127.0.0.1 --port 8000 --log-level info"
timeout /t 3 /nobreak >nul

REM Verify backend started
python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')" 2>nul
if %errorlevel% neq 0 (
    echo WARNING: Backend may not have started yet. Proceeding anyway...
) else (
    echo       Backend running!
)
echo.

REM ── Step 3: Launch Flutter app (Windows desktop) ─────────────────────────
echo [3/3] Launching Flutter app...
cd /d "%~dp0flutter_app"
flutter run -d windows
if %errorlevel% neq 0 (
    echo.
    echo  Flutter desktop run failed. Trying web instead...
    flutter run -d chrome
)

echo.
echo DocuSpeak closed.
pause

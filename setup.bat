@echo off
echo ================================================
echo   FLUX Image Studio -- Nexflow Studio
echo   Setup (Windows)
echo ================================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Install from https://python.org
    pause & exit /b 1
)

echo [1/3] Creating virtual environment...
python -m venv venv
call venv\Scripts\activate.bat

echo [2/3] Installing dependencies...
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet

echo [3/3] Setting up .env...
if not exist .env (
    copy .env.example .env >nul
    echo [!] Open .env and paste your HF_TOKEN
)

echo.
echo ================================================
echo   Done! Run: start.bat
echo ================================================
pause

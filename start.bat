@echo off
echo ================================================
echo   FLUX Image Studio -- Nexflow Studio
echo ================================================
echo.

if not exist venv\Scripts\activate.bat (
    echo [ERROR] Run setup.bat first!
    pause & exit /b 1
)

call venv\Scripts\activate.bat

if exist .env (
    for /f "usebackq tokens=1,2 delims==" %%A in (".env") do (
        set "line=%%A"
        if not "!line:~0,1!"=="#" if not "%%A"=="" set %%A=%%B
    )
)

echo [INFO] Open http://127.0.0.1:7860 in your browser
echo [INFO] Press Ctrl+C to stop
echo.
python app.py
pause

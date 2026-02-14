@echo off
setlocal
title Notenmappe Starter
echo ============================================
echo   Notenmappe - Automatischer Starter
echo ============================================
echo.

:: 1. Check Python
echo [1/3] Pruefe Python Installation...
python --version > tmp_py.txt 2>&1
set /p PY_VER=<tmp_py.txt
del tmp_py.txt

if %errorlevel% neq 0 (
    echo.
    echo [!] FEHLER: Python wurde nicht gefunden oder ist nicht installiert.
    echo.
    echo Bitte installiere Python 3 von: https://www.python.org/downloads/
    echo WICHTIG: Setze bei der Installation den Haken bei "Add Python to PATH".
    echo.
    pause
    exit /b
)
echo     Gefunden: %PY_VER%

:: 2. Install Dependencies
echo [2/3] Bereite Programme vor (bitte warten)...
echo     (Das kann beim ersten Mal 1-2 Minuten dauern)
python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo.
    echo [!] FEHLER bei der Installation der Programmteile.
    echo Bitte Internetverbindung pruefen.
    echo.
    pause
    exit /b
)

:: 3. Start Application
echo [3/3] Starte Notenmappe...
echo.
echo     Info: Ein Browserfenster wird gleich automatisch geoeffnet.
echo     Hinweis: Dieses schwarze Fenster muss offen bleiben!
echo.

:: Opening browser with a small delay so server can start
start "" "http://localhost:5000"
python app.py

if %errorlevel% neq 0 (
    echo.
    echo [!] Das Programm wurde leider beendet.
    echo.
    pause
)

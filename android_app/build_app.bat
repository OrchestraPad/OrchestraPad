@echo off
echo ===================================================
echo OrchestraPad Android Builder
echo ===================================================
echo.

REM Check if Flutter is in PATH, if not try default location
where flutter >nul 2>nul
if %errorlevel% neq 0 (
    echo Flutter nicht im Pfad gefunden. Suche in C:\src\flutter...
    if exist C:\src\flutter\bin\flutter.bat (
        set PATH=%PATH%;C:\src\flutter\bin
        echo Flutter temporaer zum Pfad hinzugefuegt.
    ) else (
        echo FEHLER: Flutter wurde nicht gefunden!
        echo Bitte installiere Flutter nach C:\src\flutter oder fuege es zu PATH hinzu.
        echo Siehe README_BUILD.md fuer Hilfe.
        pause
        exit /b
    )
)

echo Hole Abhaengigkeiten...
call flutter pub get

if %errorlevel% neq 0 (
    echo Fehler beim Laden der Pakete. Pruefe deine Internetverbindung.
    pause
    exit /b
)

echo.
echo Baue APK (Release Modus)...
call flutter build apk --release

if %errorlevel% neq 0 (
    echo.
    echo FEHLER BEIM BAUEN!
    echo Bitte pruefe die Fehlermeldungen oben.
    pause
    exit /b
)

echo.
echo ===================================================
echo ERFOLG! Die App wurde gebaut.
echo ===================================================
echo.
echo Du findest die Datei hier:
echo build\app\outputs\flutter-apk\app-release.apk
echo.
explorer build\app\outputs\flutter-apk\
pause

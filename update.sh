#!/bin/bash
# Update Script for Notenmappe
# Usage: bash update.sh

echo "================================================"
echo "   Notenmappe - Program-Update"
echo "================================================"

APP_DIR=$(pwd)

# 1. Internet Check
echo "[1/3] Prüfe Internetverbindung..."
if ! ping -c 1 8.8.8.8 > /dev/null 2>&1; then
    echo "FEHLER: Keine Internetverbindung. Bitte WLAN prüfen."
    exit 1
fi

# 2. Sync Files (Git)
echo "[2/3] Suche nach Programm-Aktualisierungen..."
if [ -d ".git" ]; then
    git pull
else
    echo "HINWEIS: Kein Git-Repository gefunden. Manueller Download erforderlich."
    echo "Falls du das Programm per ZIP-Upload aktualisieren möchtest,"
    echo "kopiere die neuen Dateien einfach in diesen Ordner: $APP_DIR"
fi

# 3. Update Dependencies
echo "[3/3] Aktualisiere Abhängigkeiten (Python Packages)..."
if [ -d "venv" ]; then
    source venv/bin/activate
    pip install -r requirements.txt
else
    echo "FEHLER: venv nicht gefunden. Bitte setup_pi.sh erneut ausführen."
    exit 1
fi

echo "================================================"
echo "   Update erfolgreich abgeschlossen!"
echo "================================================"
echo "Bitte starte das Programm neu oder boote den Pi neu."
echo "Befehl: sudo reboot"

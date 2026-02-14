#!/bin/bash
# Update Script for OrchestraPad
# Usage: bash update.sh

echo "================================================"
echo "   OrchestraPad - Update Skript"
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
    echo "Sichere lokale Änderungen..."
    git stash
    echo "Hole Updates vom Server..."
    git fetch --all
    git reset --hard origin/main
    echo "✓ Programm-Dateien aktualisiert"
else
    echo "HINWEIS: Kein Git-Repository gefunden. Manueller Download erforderlich."
    echo "Falls du das Programm per ZIP-Upload aktualisieren möchtest,"
    echo "kopiere die neuen Dateien einfach in diesen Ordner: $APP_DIR"
fi

# 3. Install Dependencies
echo "[3/3] Aktualisiere Abhängigkeiten..."
if [ -f "requirements.txt" ]; then
    pip3 install -r requirements.txt --break-system-packages
fi

# Check for OCR (Tesseract) and Pillow dependencies
if ! dpkg -s tesseract-ocr >/dev/null 2>&1; then
    echo "OCR-Software und Bild-Bibliotheken werden installiert (kann dauern)..."
    sudo apt-get update
    sudo apt-get install -y poppler-utils tesseract-ocr tesseract-ocr-deu libtesseract-dev
    # Libraries for Pillow
    sudo apt-get install -y libjpeg-dev zlib1g-dev libfreetype6-dev liblcms2-dev libopenjp2-7-dev libtiff5-dev
fi

# 3. Update Dependencies
echo "[3/3] Aktualisiere Abhängigkeiten (Python Packages)..."
if [ -d "venv" ]; then
    source venv/bin/activate
    pip install -r requirements.txt
    
    # 4. Database Migration
    echo "[4/4] Prüfe Datenbank-Struktur (Migration)..."
    python migrate_db.py
else
    echo "FEHLER: venv nicht gefunden. Bitte setup_pi.sh erneut ausführen."
    exit 1
fi

echo "================================================"
echo "   Update erfolgreich abgeschlossen!"
echo "================================================"
echo "Bitte starte das Programm neu oder boote den Pi neu."
echo "Befehl: sudo reboot"

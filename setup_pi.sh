#!/bin/bash
# Raspberry Pi Setup Script for Music Sheet Reader - v5 (Desktop Icon Fix)
# Run this on your Pi: bash setup_pi.sh

REPO_URL="https://github.com/OrchestraPad/OrchestraPad.git"

echo "================================================"
echo "   OrchestraPad - Raspberry Pi Setup"
echo "================================================"

# --- 1. System Check ---
echo "[1/4] Prüfe System..."
APP_DIR=$(pwd)
CURRENT_USER=$(whoami)

# --- 2. Install Dependencies ---
echo "[2/4] Installiere Software..."
sudo apt update

# Essential packages
sudo apt install -y python3-pip python3-venv unclutter

# Check for Chromium (don't fail if already there)
BROWSER_CMD=""
if command -v chromium-browser > /dev/null 2>&1; then
    BROWSER_CMD="chromium-browser"
elif command -v chromium > /dev/null 2>&1; then
    BROWSER_CMD="chromium"
fi

# --- 3. Virtual Environment Setup ---
echo "[3/4] Erstelle Python-Umgebung..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt

# Create necessary directories
mkdir -p instance
mkdir -p usb_drive

# --- 4. Configure Autostart & Desktop Icon ---
echo "[4/4] Konfiguriere Autostart & Desktop-Icon..."

# Create the .desktop content
DESKTOP_CONTENT="[Desktop Entry]
Type=Application
Name=OrchestraPad
Icon=video-display
Exec=bash -c \"cd $APP_DIR && ./venv/bin/python3 app.py & sleep 8 && $BROWSER_CMD --kiosk --incognito http://localhost:5000\"
Terminal=false"

# 1. Autostart
AUTOSTART_DIR="$HOME/.config/autostart"
mkdir -p "$AUTOSTART_DIR"
echo "$DESKTOP_CONTENT" > "$AUTOSTART_DIR/orchestrapad.desktop"

# 2. Desktop Shortcut
DESKTOP_PATH="$HOME/Desktop/OrchestraPad.desktop"
echo "$DESKTOP_CONTENT" > "$DESKTOP_PATH"
chmod +x "$DESKTOP_PATH"

echo "================================================"
echo "   FERTIG!"
echo "================================================"
echo "1. Es liegt nun ein Icon 'OrchestraPad' auf deinem Desktop."
echo "2. Doppelklick darauf startet den Server und den Browser."
echo "3. Falls das OS fragt: Wähle 'Execute' (Ausführen)."
echo ""
echo "Bitte starte deinen Pi jetzt neu: sudo reboot"

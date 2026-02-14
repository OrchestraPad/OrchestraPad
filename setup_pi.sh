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
echo "[4/4] Konfiguriere Autostart & Display..."

# Ask for rotation (only if interactive)
ROTATION_CMD=""
if [ -t 0 ]; then
    echo "Soll der Bildschirm für den Notenständer gedreht werden (Hochformat)?"
    echo "1) Nein (Standard)"
    echo "2) Ja (90 Grad - Portrait)"
    read -p "Auswahl [1-2]: " ROT_CHOICE
    if [ "$ROT_CHOICE" == "2" ]; then
        # Try to detect compositor (Wayland/X11)
        if [ "$XDG_SESSION_TYPE" == "wayland" ] || [ -n "$WAYLAND_DISPLAY" ]; then
            ROTATION_CMD="wlr-randr --output HDMI-A-1 --transform 90 && "
        else
            ROTATION_CMD="xrandr --output HDMI-1 --rotate right && "
        fi
        echo "   -> Rotation aktiviert."
    fi
fi

# Create the .desktop content
DESKTOP_CONTENT="[Desktop Entry]
Type=Application
Name=OrchestraPad
Icon=video-display
Exec=bash -c \"$ROTATION_CMD cd $APP_DIR && ./venv/bin/python3 app.py & sleep 10 && $BROWSER_CMD --kiosk --incognito http://localhost:5000\"
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
echo "2. Der Autostart wurde konfiguriert (Kiosk-Modus)."
echo "   WICHTIG: Sollte der Browser zu frueh starten, erhoehe 'sleep' im Desktop-Icon."
echo ""
echo "Bitte starte deinen Pi jetzt neu: sudo reboot"

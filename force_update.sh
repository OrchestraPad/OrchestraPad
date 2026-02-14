#!/bin/bash
# Force update script - ensures all files are updated

echo "=== OrchestraPad Force Update ==="

cd ~/Noten

echo "Step 1: Stopping service..."
sudo systemctl stop orchestrapad 2>/dev/null || true

# 3. Install Dependencies
echo "[3/3] Aktualisiere Abhängigkeiten..."

# Upgrade build tools FIRST
if [ -d "venv" ]; then
    echo "Aktiviere Python venv..."
    source venv/bin/activate
    pip install --upgrade pip setuptools wheel
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    fi
else
    echo "Nutze System-Python (kein venv gefunden)..."
    pip3 install --upgrade pip setuptools wheel --break-system-packages
    if [ -f "requirements.txt" ]; then
        pip3 install -r requirements.txt --break-system-packages
    fi
fi

# Check for OCR (Tesseract) and Pillow dependencies
if ! dpkg -s tesseract-ocr >/dev/null 2>&1; then
    echo "OCR-Software und Bild-Bibliotheken werden installiert (kann dauern)..."
    sudo apt-get update
    sudo apt-get install -y poppler-utils tesseract-ocr tesseract-ocr-deu libtesseract-dev
    # Libraries for Pillow
    sudo apt-get install -y libjpeg-dev zlib1g-dev libfreetype6-dev liblcms2-dev libopenjp2-7-dev libtiff5-dev
fi

echo "Step 2: Backing up and resetting..."
git stash
git fetch --all
git reset --hard origin/main

echo "Step 3: Checking templates..."
if grep -q "delete-button" "templates/index.html"; then
   echo "✓ Delete button code found in index.html"
else
   echo "⚠ Warning: unexpected content in index.html"
fi

echo "Step 4: Clearing Python cache..."
find . -name "*.pyc" -delete
find . -name "__pycache__" -delete

echo "Step 5: Restarting service..."
# Restart commands
if [ -f "$HOME/.config/autostart/orchestrapad.desktop" ]; then
    # We don't have a systemd service, so we just rely on reboot or try to kill/start manually?
    # For now, just print message since we ask for reboot anyway.
    echo "Service restart will happen on reboot."
else
    # Try systemd just in case
    sudo systemctl restart orchestrapad || echo "Service not found, please reboot."
fi

echo ""
echo "=== Update complete! ==="
echo "Please wait 10 seconds, then refresh browser with Ctrl+F5"

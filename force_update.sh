#!/bin/bash
# Force update script - ensures all files are updated

echo "=== OrchestraPad Force Update ==="

cd ~/Noten

echo "Step 1: Stopping service..."
sudo systemctl stop orchestrapad

# 3. Install Dependencies
echo "[3/3] Aktualisiere Abhängigkeiten..."

# Upgrade build tools FIRST
pip3 install --upgrade pip setuptools wheel --break-system-packages

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
# Re-install dependencies with updated tools
pip3 install --upgrade pip setuptools wheel --break-system-packages
pip3 install -r requirements.txt --break-system-packages

sudo systemctl restart orchestrapad
sudo systemctl start orchestrapad

echo ""
echo "=== Update complete! ==="
echo "Please wait 10 seconds, then refresh browser with Ctrl+F5"

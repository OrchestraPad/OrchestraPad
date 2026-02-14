#!/bin/bash
# Force update script - ensures all files are updated

echo "=== OrchestraPad Force Update ==="

cd ~/Noten

echo "Step 1: Stopping service..."
sudo systemctl stop orchestrapad

# 3. Install Dependencies
echo "[3/3] Aktualisiere Abhängigkeiten..."
if [ -f "requirements.txt" ]; then
    pip3 install -r requirements.txt --break-system-packages
fi

# Check for OCR (Tesseract)
if ! dpkg -s tesseract-ocr >/dev/null 2>&1; then
    echo "OCR-Software wird installiert (kann dauern)..."
    sudo apt-get update && sudo apt-get install -y poppler-utils tesseract-ocr tesseract-ocr-deu libtesseract-dev
fi

echo "Step 2: Backing up and resetting..."
git stash
git fetch --all
git reset --hard origin/main

echo "Step 3: Checking templates..."
if grep -q "onclick=\"deleteSong" templates/index.html; then
    echo "✓ Delete button code found in index.html"
else
    echo "✗ Delete button code NOT found - something is wrong!"
fi

echo "Step 4: Clearing Python cache..."
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

echo "Step 5: Restarting service..."
sudo systemctl start orchestrapad

echo ""
echo "=== Update complete! ==="
echo "Please wait 10 seconds, then refresh browser with Ctrl+F5"

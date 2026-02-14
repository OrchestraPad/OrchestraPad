#!/bin/bash
echo "Installing OCR dependencies..."

# Install system dependencies for PDF processing and OCR
sudo apt-get update
sudo apt-get install -y poppler-utils tesseract-ocr tesseract-ocr-deu libtesseract-dev

# Install Python dependencies
pip3 install pdf2image pytesseract

echo "OCR Setup complete!"

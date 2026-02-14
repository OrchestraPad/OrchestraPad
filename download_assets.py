import urllib.request
import os

BASE_URL = "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/"
FILES = ["pdf.min.js", "pdf.worker.min.js"]
TARGET_DIR = "static/lib"

if not os.path.exists(TARGET_DIR):
    os.makedirs(TARGET_DIR)

for file in FILES:
    print(f"Downloading {file}...")
    urllib.request.urlretrieve(BASE_URL + file, os.path.join(TARGET_DIR, file))
    print(f"Saved to {os.path.join(TARGET_DIR, file)}")

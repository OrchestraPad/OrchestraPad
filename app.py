import os
from flask import Flask, render_template, send_from_directory, jsonify, request
from models import db, Song, Setlist, SetlistSong
from pypdf import PdfReader
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import difflib
import re
import shutil

# Configuration
STORAGE_PATH = os.path.join(os.getcwd(), 'usb_drive')
THUMBNAIL_PATH = os.path.join(os.getcwd(), 'thumbnails')
USB_BASE_PATH = '/media/pi' # Default Raspberry Pi mount point
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///music.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize DB
db.init_app(app)

# Load Version
VERSION = "unknown"
if os.path.exists('VERSION'):
    with open('VERSION', 'r') as f:
        VERSION = f.read().strip()

# --- CONSTANTS & MAPPINGS ---
INSTRUMENT_MAPPING = {
    # Woodwinds
    "piccolo": "Piccolo", "picc": "Piccolo", "pikkolo": "Piccolo",
    "flute": "Flöte", "flöte": "Flöte", "floete": "Flöte", "fl": "Flöte",
    "oboe": "Oboe", "ob": "Oboe",
    "english horn": "Englischhorn", "englischhorn": "Englischhorn", "e. horn": "Englischhorn",
    "clarinet": "Klarinette", "klarinette": "Klarinette", "kl": "Klarinette", "cl": "Klarinette",
    "bass clarinet": "Bassklarinette", "bassklarinette": "Bassklarinette", "b. kl": "Bassklarinette",
    "bassoon": "Fagott", "fagott": "Fagott", "fag": "Fagott", "bsn": "Fagott",
    "saxophone": "Saxophon", "saxophon": "Saxophon", "sax": "Saxophon",
    "alto sax": "Altsaxophon", "altsax": "Altsaxophon", "a. sax": "Altsaxophon",
    "tenor sax": "Tenorsaxophon", "tenorsax": "Tenorsaxophon", "t. sax": "Tenorsaxophon",
    "baritone sax": "Baritonsaxophon", "barisax": "Baritonsaxophon", "b. sax": "Baritonsaxophon",
    
    # Brass
    "cornet": "Kornett", "kornett": "Kornett", "cnt": "Kornett",
    "trumpet": "Trompete", "trompete": "Trompete", "trp": "Trompete", "tpt": "Trompete",
    "flugelhorn": "Flügelhorn", "flügelhorn": "Flügelhorn", "fluegelhorn": "Flügelhorn",
    "horn": "Horn", "french horn": "Horn", "hrn": "Horn", "cor": "Horn", "corno": "Horn",
    "trombone": "Posaune", "posaune": "Posaune", "pos": "Posaune", "tbn": "Posaune",
    "bass trombone": "Bassposaune", "bassposaune": "Bassposaune",
    "baritone": "Bariton", "bariton": "Bariton",
    "euphonium": "Euphonium", "tenorhorn": "Tenorhorn",
    "tuba": "Tuba", "bass": "Tuba", "basses": "Tuba",
    "sousaphone": "Sousaphon",

    # Percussion
    "drums": "Schlagzeug", "drum set": "Schlagzeug", "schlagzeug": "Schlagzeug", "drum": "Schlagzeug",
    "percussion": "Percussion", "perc": "Percussion", "batterie": "Percussion",
    "pauken": "Pauken", "timpani": "Pauken", "pk": "Pauken", "timp": "Pauken",
    "mallets": "Mallets", "glockenspiel": "Glockenspiel",
    "xylophone": "Xylophon", "xylophon": "Xylophon", 
    "vibraphone": "Vibraphon", "vibraphon": "Vibraphon", 

    # Strings/Others
    "violin": "Violine", "violine": "Violine", "vl": "Violine", "vln": "Violine", "geige": "Violine",
    "viola": "Viola", "bratsche": "Viola", "vla": "Viola",
    "cello": "Cello", "violoncello": "Cello", "vc": "Cello",
    "contrabass": "Kontrabass", "double bass": "Kontrabass", "kb": "Kontrabass", "db": "Kontrabass",
    "piano": "Klavier", "klavier": "Klavier", "pno": "Klavier",
    "keyboard": "Keyboard", "keys": "Keyboard",
    "guitar": "Gitarre", "gitarre": "Gitarre",
    "harp": "Harfe", "harfe": "Harfe",
    
    # Meta
    "director": "Direktion", "conductor": "Direktion", "cond": "Direktion",
    "score": "Partitur", "partitur": "Partitur"
}

KEY_MAPPING = {
    "bb": "in B", "b": "in B", 
    "eb": "in Es", "es": "in Es", 
    "c": "in C", 
    "f": "in F",
    "ab": "in As"
}

@app.context_processor
def inject_version():
    return dict(app_version=VERSION)

with app.app_context():
    db.create_all()
@app.route('/analyze_parts/<int:song_id>')
def analyze_parts(song_id):
    song = Song.query.get_or_404(song_id)
    pdf_path = os.path.join(STORAGE_PATH, song.file_path)
    
    if song.detected_parts:
        return jsonify(song.detected_parts)
        
    if not os.path.exists(pdf_path):
        return jsonify({'error': 'File not found'}), 404
        

    try:
        reader = PdfReader(pdf_path)
        parts = {} # "Instrument Name" -> [page_num, ...]

        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if not text: continue
            
            # Focus on top 30% of text for headers to avoid false positives in cues
            lines = text.split('\n')
            header_lines = lines[:int(len(lines)*0.3) + 5] # At least top 5 lines or 30%
            
            found_on_page = []

            for line in header_lines:
                # Use the unified helper
                # We expect high confidence for automatic analysis since we scan many lines
                result = identify_instrument_from_text(line)
                if result['confidence'] >= 0.8: # Strict threshold for auto-detection
                    found_on_page.append(result['text'])
            
            if not found_on_page:
                # If page has plenty of text but no instrument, might be Score?
                # Or just keep it out of part index.
                pass
            
            for part_name in set(found_on_page):
                 if part_name not in parts:
                     parts[part_name] = []
                 parts[part_name].append(i + 1)

        # Sort keys naturally
        sorted_parts = {k: parts[k] for k in sorted(parts)}
        return jsonify(sorted_parts)

    except Exception as e:
        print(f"Error analyzing PDF: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/run_ocr_analysis/<int:song_id>', methods=['POST'])
def run_ocr_analysis(song_id):
    song = Song.query.get_or_404(song_id)
    page_texts = request.json # { "page_1": "text...", ... }
    
    if not page_texts:
        return jsonify({'error': 'No text provided'}), 400
        
    parts = {}
    
    # Process each page
    for p_key, text in page_texts.items():
        try:
            page_num = int(p_key.replace('page_', ''))
        except:
            continue
            
        if not text: continue
        
        found_on_page = []
        lines = text.split('\n')
        
        for line in lines:
            # Use unified helper
            result = identify_instrument_from_text(line)
            if result['confidence'] >= 0.8:
                found_on_page.append(result['text'])
        
        for part_name in set(found_on_page):
            if part_name not in parts:
                parts[part_name] = []
            parts[part_name].append(page_num)

    # Save to DB
    song.detected_parts = parts
    db.session.commit()
    return jsonify({'status': 'success', 'parts': parts})



@app.route('/')
def index():
    songs = Song.query.all()
    return render_template('index.html', songs=songs)

@app.route('/scan')
def scan_library():
    """Scans multiple locations for PDFs and updates the database."""
    added = 0
    copied = 0
    debug_info = []
    
    # Ensure local storage path exists
    if not os.path.exists(STORAGE_PATH):
        os.makedirs(STORAGE_PATH)
    if not os.path.exists(THUMBNAIL_PATH):
        os.makedirs(THUMBNAIL_PATH)
    
    # Locations to scan
    scan_paths = [STORAGE_PATH]
    debug_info.append(f"Local storage: {STORAGE_PATH}")
    
    # Check multiple common USB mount locations
    usb_search_paths = [
        '/media',      # Check all /media subdirectories
        '/mnt',        # Alternative mount point
        '/media/pi',   # Older Raspberry Pi OS
    ]
    
    # Check for Cloud Folder (e.g. mounted Google Drive via rclone)
    cloud_path = os.path.join(os.path.expanduser("~"), "CloudNoten")
    if os.path.exists(cloud_path):
        scan_paths.append(cloud_path)
        debug_info.append(f"Found Cloud Folder: {cloud_path}")
    else:
        # Create it so user knows where to mount
        try:
            os.makedirs(cloud_path)
            debug_info.append(f"Created Cloud Folder for mounting: {cloud_path}")
        except:
            pass
    
    for base in usb_search_paths:
        if os.path.exists(base):
            debug_info.append(f"Checking mount base: {base}")
            try:
                # If it's /media or /mnt, check all subdirectories
                if base in ['/media', '/mnt']:
                    for username_or_mount in os.listdir(base):
                        user_media = os.path.join(base, username_or_mount)
                        if os.path.isdir(user_media):
                            # Check if this is a mount point or contains mounts
                            # For /media/username, list subdirectories (each USB stick)
                            try:
                                for mount in os.listdir(user_media):
                                    full_mount = os.path.join(user_media, mount)
                                    if os.path.isdir(full_mount):
                                        scan_paths.append(full_mount)
                                        debug_info.append(f"Added USB mount: {full_mount}")
                            except PermissionError:
                                debug_info.append(f"Permission denied: {user_media}")
                else:
                    # For /media/pi, scan subdirectories directly
                    for mount in os.listdir(base):
                        full_mount = os.path.join(base, mount)
                        if os.path.isdir(full_mount):
                            scan_paths.append(full_mount)
                            debug_info.append(f"Added USB mount: {full_mount}")
            except Exception as e:
                debug_info.append(f"Error scanning {base}: {str(e)}")
        else:
            debug_info.append(f"Mount base does not exist: {base}")
    
    debug_info.append(f"Total scan paths: {len(scan_paths)}")
    
    for base_path in scan_paths:
        if not os.path.exists(base_path):
            debug_info.append(f"Skipping non-existent path: {base_path}")
            continue
        
        files_in_path = 0
        is_external = (base_path != STORAGE_PATH)
        
        for root, dirs, files in os.walk(base_path):
            for file in files:
                if file.lower().endswith('.pdf'):
                    files_in_path += 1
                    source_path = os.path.join(root, file)
                    
                    # For external sources (USB), copy to local storage
                    if is_external:
                        # Create a safe filename (remove special chars, keep original name)
                        safe_filename = file.replace(' ', '_')
                        # Check if file already exists in storage (deduplication)
                        # We assume if filename matches, it's the same file.
                        target_path = os.path.join(STORAGE_PATH, safe_filename)
                        
                        if os.path.exists(target_path):
                            # File exists, skip copying and skip adding to DB (avoid duplicates)
                            # debug_info.append(f"Skipped existing: {file}")
                            continue
                            
                        # If we reach here, it is a new file
                        try:
                            import shutil
                            shutil.copy2(source_path, target_path)
                            db_path = safe_filename
                            copied += 1
                            # debug_info.append(f"Copied: {file} -> {safe_filename}")
                        except Exception as e:
                            # debug_info.append(f"Error copying {file}: {str(e)}")
                            continue
                    else:
                        # For local files, just use relative path
                        db_path = os.path.relpath(source_path, STORAGE_PATH)
                        
                    # Check if song exists
                    existing = Song.query.filter_by(file_path=db_path).first()
                    if not existing:
                        new_song = Song(title=file[:-4], file_path=db_path)
                        db.session.add(new_song)
                        added += 1
        
        debug_info.append(f"Found {files_in_path} PDF(s) in {base_path}")
    
    debug_info.append(f"Summary: {added} new songs added, {copied} files copied from USB")
    
    db.session.commit()
    return jsonify({
        'status': 'success', 
        'added': added,
        'copied': copied,
        'debug': debug_info
    })

@app.route('/edit_song/<int:song_id>', methods=['POST'])
def edit_song(song_id):
    song = Song.query.get_or_404(song_id)
    data = request.json
    song.title = data.get('title', song.title)
    song.composer = data.get('composer', song.composer)
    song.arranger = data.get('arranger', song.arranger)
    song.genre = data.get('genre', song.genre)
    db.session.commit()
    return jsonify({'status': 'success'})

@app.route('/delete_song/<int:song_id>', methods=['DELETE'])
def delete_song(song_id):
    song = Song.query.get_or_404(song_id)
    
    # Delete the PDF file if it exists
    file_path = os.path.join(STORAGE_PATH, song.file_path)
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception as e:
            return jsonify({'status': 'error', 'message': f'Failed to delete file: {str(e)}'}), 500
            
    # Remove thumbnails
    thumb_dir = os.path.join(THUMBNAIL_PATH, str(song_id))
    if os.path.exists(thumb_dir):
        try:
            shutil.rmtree(thumb_dir)
        except Exception as e:
            print(f"Warning: Could not delete thumbnails for {song_id}: {e}")
    
    # Remove from all setlists
    SetlistSong.query.filter_by(song_id=song_id).delete()
    
    # Delete the song from database
    db.session.delete(song)
    db.session.commit()
    
    return jsonify({'status': 'success'})

@app.route('/setlists', methods=['GET', 'POST'])
def handle_setlists():
    if request.method == 'GET':
        setlists = Setlist.query.all()
        return jsonify([{'id': s.id, 'name': s.name, 'count': len(s.songs)} for s in setlists])
    else:
        name = request.json.get('name')
        if name:
            new_list = Setlist(name=name)
            db.session.add(new_list)
            db.session.commit()
            return jsonify({'id': new_list.id, 'name': new_list.name})
        return jsonify({'error': 'Name missing'}), 400

@app.route('/setlist_entry', methods=['POST', 'DELETE'])
def handle_setlist_entry_route():
    if request.method == 'POST':
        data = request.json
        setlist_id = data.get('setlist_id')
        song_id = data.get('song_id')
        
        # Check if already exists
        exists = SetlistSong.query.filter_by(setlist_id=setlist_id, song_id=song_id).first()
        if exists:
            return jsonify({'status': 'exists', 'message': 'Song already in setlist'})
            
        # Get highest position
        max_pos = db.session.query(db.func.max(SetlistSong.position)).filter_by(setlist_id=setlist_id).scalar() or 0
        new_entry = SetlistSong(setlist_id=setlist_id, song_id=song_id, position=max_pos+1)
        db.session.add(new_entry)
        db.session.commit()
        return jsonify({'status': 'success'})
        
    elif request.method == 'DELETE':
        # This handle deletion by entry_id (from /setlist_entry/<int:id>)
        # But wait, the route above doesn't have <int:id>. 
        # We need a separate route for DELETE /setlist_entry/<id>
        return jsonify({'error': 'Method not allowed here'}), 405

@app.route('/setlist_entry/<int:entry_id>', methods=['DELETE'])
def delete_setlist_entry(entry_id):
    entry = SetlistSong.query.get_or_404(entry_id)
    db.session.delete(entry)
    db.session.commit()
    return jsonify({'status': 'success'})

@app.route('/setlist/<int:setlist_id>', methods=['GET', 'POST', 'DELETE'])
def handle_setlist(setlist_id):
    setlist = Setlist.query.get_or_404(setlist_id)
    
    if request.method == 'DELETE':
        db.session.delete(setlist)
        db.session.commit()
        return jsonify({'status': 'deleted'})

    # GET: return songs in order
    songs = []
    for entry in sorted(setlist.songs, key=lambda x: x.position):
        s = entry.song
        songs.append({
            'id': s.id, 'title': s.title, 'composer': s.composer, 
            'arranger': s.arranger, 'file_path': s.file_path, 
            'position': entry.position, 'entry_id': entry.id
        })
    return jsonify({'id': setlist.id, 'name': setlist.name, 'songs': songs})

@app.route('/view/<int:song_id>')
def view_song(song_id):
    song = Song.query.get_or_404(song_id)
    return render_template('viewer.html', song=song)

@app.route('/pdf/<path:filename>')
def serve_pdf(filename):
    # Try local storage first
    if os.path.exists(os.path.join(STORAGE_PATH, filename)):
        return send_from_directory(STORAGE_PATH, filename)
    # Otherwise it might be an absolute path from a USB stick
    if os.path.exists(filename):
        directory = os.path.dirname(filename)
        base_name = os.path.basename(filename)
        return send_from_directory(directory, base_name)
    return "File not found", 404

@app.route('/song_settings/<int:song_id>', methods=['GET', 'POST'])
def song_settings(song_id):
    song = Song.query.get_or_404(song_id)
    if request.method == 'POST':
        data = request.json
        if 'settings' in data:
            song.settings = data['settings']
        if 'bounding_boxes' in data:
            # Merge or replace? Replace is safer for this state
            song.bounding_boxes = data['bounding_boxes']
        db.session.commit()
        return jsonify({'status': 'success'})
    
    return jsonify({
        'settings': song.settings or {},
        'bounding_boxes': song.bounding_boxes or {}
    })

@app.route('/changelog')
def get_changelog():
    if os.path.exists('CHANGELOG.md'):
        with open('CHANGELOG.md', 'r', encoding='utf-8') as f:
            return jsonify({"content": f.read()})
    return jsonify({"content": "Kein Versionsverlauf gefunden."})

@app.route('/run_update', methods=['POST'])
def run_update():
    import subprocess
    try:
        # Run the update script and capture output
        # On Pi it's bash, on Windows we skip for safety
        if os.name == 'nt':
            return jsonify({"status": "error", "output": "Updates sind auf Windows nur manuell möglich."})
            
        process = subprocess.Popen(['bash', 'update.sh'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        output, _ = process.communicate()
        
        if process.returncode == 0:
            return jsonify({"status": "success", "output": output})
        else:
            return jsonify({"status": "error", "output": output})
    except Exception as e:
        return jsonify({"status": "error", "output": str(e)})

@app.route('/system_control', methods=['POST'])
def system_control():
    import subprocess
    import signal
    action = request.json.get('action')
    try:
        if action == 'shutdown':
            if os.name != 'nt':
                subprocess.Popen(['sudo', 'poweroff'])
                return jsonify({"status": "success", "message": "System wird heruntergefahren..."})
            return jsonify({"status": "error", "message": "Herunterfahren nur auf dem Pi möglich."})
            
        elif action == 'exit':
            # Clean exit for the python process with a small delay to allow response to reach browser
            import threading
            import time
            def delayed_exit():
                time.sleep(0.5)
                os.kill(os.getpid(), signal.SIGINT)
            
            threading.Thread(target=delayed_exit).start()
            return jsonify({"status": "success", "message": "Programm wird beendet..."})
            
        return jsonify({"status": "error", "message": "Ungültige Aktion."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/thumbnail/<int:song_id>/<int:page_num>')
def get_thumbnail(song_id, page_num):
    song = Song.query.get_or_404(song_id)
    
    # Folder for this song's thumbnails
    song_thumb_dir = os.path.join(THUMBNAIL_PATH, str(song_id))
    if not os.path.exists(song_thumb_dir):
        os.makedirs(song_thumb_dir)
        
    thumb_filename = f"page_{page_num}.jpg"
    thumb_path = os.path.join(song_thumb_dir, thumb_filename)
    
    # If exists, serve
    if os.path.exists(thumb_path):
        return send_from_directory(song_thumb_dir, thumb_filename)
        
    # Generate
    try:
        pdf_path = os.path.join(STORAGE_PATH, song.file_path)
        # Convert single page (1-based) at higher DPI for readable text
        # dpi=150 gives good quality for headers
        images = convert_from_path(pdf_path, first_page=page_num, last_page=page_num, dpi=150)
        
        if images:
            # Optimize and save
            img = images[0]
            
            # Crop to top 25% height and left 50% width per user request
            w, h = img.size
            img = img.crop((0, 0, int(w * 0.5), int(h * 0.25)))
            
            # Resize width to max 600px
            if img.size[0] > 600:
                new_h = int((600 / img.size[0]) * img.size[1])
                img = img.resize((600, new_h), Image.Resampling.LANCZOS)

            # Convert to RGB (remove alpha) for JPEG
            if img.mode in ("RGBA", "P"): img = img.convert("RGB")
            img.save(thumb_path, "JPEG", quality=80)
            return send_from_directory(song_thumb_dir, thumb_filename)
        else:
            return "Could not generate thumbnail", 404
            
    except Exception as e:
        print(f"Thumb error: {e}")
        return str(e), 500

@app.route('/scan_part_region', methods=['POST'])
def scan_part_region():
    data = request.json
    song_id = data.get('song_id')
    page_num = data.get('page', 1) - 1 # 0-indexed
    box = data.get('box') # {x, y, w, h} in percent (0-100) or pixels
    
    song = Song.query.get_or_404(song_id)
    pdf_path = os.path.join(STORAGE_PATH, song.file_path)
    
    try:
        # Convert specific page to image with higher DPI for better OCR
        images = convert_from_path(pdf_path, first_page=page_num+1, last_page=page_num+1, dpi=400)
        if not images:
            return jsonify({'error': 'Could not convert PDF page'}), 500
            
        img = images[0]
        img_w, img_h = img.size
        print(f"DEBUG_OCR: song={song_id} page={page_num} box={box} img_size={img.size}")
        
        
        
        # Calculate crop coordinates with SAFETY PADDING (2%)
        # User reported offset to the right, so we expand the box slightly
        pad_percent = 2.0
        
        x_pct = max(0, box['x'] - pad_percent)
        y_pct = max(0, box['y'] - pad_percent)
        w_pct = min(100, box['w'] + (pad_percent * 2))
        h_pct = min(100, box['h'] + (pad_percent * 2))
        
        x = int(x_pct * img_w / 100)
        y = int(y_pct * img_h / 100)
        w = int(w_pct * img_w / 100)
        h = int(h_pct * img_h / 100)
        
        # Crop
        cropped = img.crop((x, y, x+w, y+h))
        
        # Pre-processing for better OCR
        # 1. Grayscale
        gray = cropped.convert('L') 
        # 2. Thresholding (Binarization) - simple adjustment
        # Pixels < 128 become 0 (black), others 255 (white)
        bw = gray.point(lambda x: 0 if x < 140 else 255, '1')
        
        # Run OCR
        # lang='deu' for German support if installed, else 'eng'
        # --psm 6: Assume a single uniform block of text.
        text = pytesseract.image_to_string(bw, lang='deu+eng', config='--psm 6')
        
        
        # --- SMART OCR POST-PROCESSING ---
        # Delegate to helper
        result = identify_instrument_from_text(text)
        
        return jsonify({
            'status': 'success', 
            'text': result['text'], 
            'original': text,
            'confidence': result['confidence']
        })
            
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

def identify_instrument_from_text(text):
    # Clean text
    clean_text = re.sub(r'[^\w\s\.\-\(\)]', ' ', text) # Allow brackets
    lines = clean_text.split('\n')
    
    candidates = [] # (text, score)

    for line in lines:
        line = line.strip()
        if not line or len(line) < 3: continue
        
        # Filter out obvious titles/credits
        line_lower = line.lower()
        if any(x in line_lower for x in ['music by', 'arranged by', 'composed by', 'lyrics by', 'concerto', 'symphony', 'medley', 'theme from']):
            continue

        # Look for Instrument Matches
        words = line.split()
        # Generating n-grams up to 3 words
        grams = words + [' '.join(words[i:i+2]) for i in range(len(words)-1)] + [' '.join(words[i:i+3]) for i in range(len(words)-2)]
        
        best_line_inst = ""
        best_line_score = 0.0
        
        for gram in grams:
            # Check for exact matches in keys (fast)
            gram_lower = gram.lower()
            if gram_lower in INSTRUMENT_MAPPING:
                # Exact key match (e.g. "flute")
                best_line_score = 1.0
                best_line_inst = INSTRUMENT_MAPPING[gram_lower]
                break
                
            # Fuzzy match against keys
            matches = difflib.get_close_matches(gram_lower, INSTRUMENT_MAPPING.keys(), n=1, cutoff=0.7)
            if matches:
                ratio = difflib.SequenceMatcher(None, gram_lower, matches[0]).ratio()
                if ratio > best_line_score:
                    best_line_score = ratio
                    best_line_inst = INSTRUMENT_MAPPING[matches[0]]
        
        if best_line_inst:
            # Check for Number (1, 2, 3, I, II, III, 1st, 2nd)
            
            # 1. Arabic digits
            num_match = re.search(r'\b(\d)\b', line)
            number = ""
            if num_match:
                number = num_match.group(1)
            else:
                # 2. Roman numerals (I, II, III, IV) - strict boundary
                rom_match = re.search(r'\b(I|II|III|IV)\b', line)
                if rom_match:
                    number = rom_match.group(1)
                else:
                    # 3. Ordinals (1st, 2nd)
                    ord_match = re.search(r'\b(\d)(st|nd|rd|th)\b', line.lower())
                    if ord_match:
                        number = ord_match.group(1)

            # Check for Key
            key_sig = ""
            for k_key, k_val in KEY_MAPPING.items():
                if f"in {k_key}" in line_lower: 
                    key_sig = k_val; break
                if f"in {k_key.capitalize()}" in line: # Case sensitive fallback
                     key_sig = k_val; break
                # Suffix/Prefix check
                if f" {k_key} " in line_lower: # surrounded by spaces
                     pass # Too risky? " in B " is better.

            # Construct Result
            full_name = best_line_inst
            if number:
                full_name += " " + number
                best_line_score += 0.2 
            if key_sig:
                full_name += " " + key_sig
                best_line_score += 0.1
            
            candidates.append({'text': full_name, 'confidence': best_line_score})

    if not candidates:
        return {'text': text.strip(), 'confidence': 0.0}
    
    # Sort by confidence
    candidates.sort(key=lambda x: x['confidence'], reverse=True)
    return candidates[0]


@app.route('/scan_all_pages_region', methods=['POST'])
def scan_all_pages_region():
    data = request.json
    song_id = data.get('song_id')
    box = data.get('box')
    
    song = Song.query.get_or_404(song_id)
    pdf_path = os.path.join(STORAGE_PATH, song.file_path)
    
    results = {}
    
    try:
        # Optimize: Process page by page to save memory
        reader = PdfReader(pdf_path)
        num_pages = len(reader.pages)
        
        for i in range(num_pages):
            # Convert single page (1-based index)
            # dpi=200 is usually enough for instrument headers, faster than 400
            pages = convert_from_path(pdf_path, first_page=i+1, last_page=i+1, dpi=300)
            if not pages: continue
            
            img = pages[0]
            img_w, img_h = img.size
            
            x = int(box['x'] * img_w / 100)
            y = int(box['y'] * img_h / 100)
            w = int(box['w'] * img_w / 100)
            h = int(box['h'] * img_h / 100)
            
            # Safety bounds
            x = max(0, x); y = max(0, y)
            w = min(img_w - x, w); h = min(img_h - y, h)
            
            # Check if crop is valid
            if w <= 0 or h <= 0: continue
            
            cropped = img.crop((x, y, x+w, y+h))
            
            # Reuse same preprocessing steps
            gray = cropped.convert('L')
            bw = gray.point(lambda x: 0 if x < 140 else 255, '1')
            
            text = pytesseract.image_to_string(bw, lang='deu+eng', config='--psm 6')
            
            # Use Helper
            analysis = identify_instrument_from_text(text)
            
            # Store result by page number (1-based)
            # Only store if we found something or text is not empty?
            # User wants to see results for all pages likely
            results[i+1] = analysis['text']
            
            # Explicit cleanup
            del pages
            del img
            del cropped
            del gray
            del bw
            
        return jsonify({'status': 'success', 'results': results})
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/save_part_mapping', methods=['POST'])
def save_part_mapping():
    data = request.json
    song_id = data.get('song_id')
    parts = data.get('parts') # { "Flute 1": [1, 2], "Flute 2": [3, 4] }
    
    song = Song.query.get_or_404(song_id)
    song.detected_parts = parts
    db.session.commit()
    
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

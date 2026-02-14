import os
from flask import Flask, render_template, send_from_directory, jsonify, request
from models import db, Song, Setlist, SetlistSong
from pypdf import PdfReader

# Configuration
STORAGE_PATH = os.path.join(os.getcwd(), 'usb_drive')
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

        # 1. Definitions
        instruments_map = {
            # Woodwinds
            "piccolo": "Piccolo",
            "flute": "Flöte", "flöte": "Flöte", "floete": "Flöte",
            "oboe": "Oboe",
            "clarinet": "Klarinette", "klarinette": "Klarinette",
            "bassoon": "Fagott", "fagott": "Fagott",
            "saxophone": "Saxophon", "saxophon": "Saxophon", "sax": "Saxophon",
            "alto sax": "Altsaxophon", "altsax": "Altsaxophon",
            "tenor sax": "Tenorsaxophon", "tenorsax": "Tenorsaxophon",
            "baritone sax": "Baritonsaxophon", "barisax": "Baritonsaxophon",
            
            # Brass
            "cornet": "Kornett", "kornett": "Kornett",
            "trumpet": "Trompete", "trompete": "Trompete", 
            "flugelhorn": "Flügelhorn", "flügelhorn": "Flügelhorn", "fluegelhorn": "Flügelhorn",
            "horn": "Horn", "french horn": "Horn",
            "trombone": "Posaune", "posaune": "Posaune",
            "baritone": "Bariton", "bariton": "Bariton",
            "euphonium": "Euphonium", "tenorhorn": "Tenorhorn",
            "tuba": "Tuba", "bass": "Tuba", "basses": "Tuba",
            "sousaphone": "Sousaphon",

            # Percussion
            "drums": "Schlagzeug", "drum set": "Schlagzeug", "schlagzeug": "Schlagzeug",
            "percussion": "Percussion", "pauken": "Pauken", "timpani": "Pauken",
            "mallets": "Mallets", "glockenspiel": "Glockenspiel",
            
            # Strings/Other
            "violin": "Violine", "viola": "Viola", "cello": "Cello", "contrabass": "Kontrabass",
            "piano": "Klavier", "keyboard": "Keyboard", "guitar": "Gitarre",
            "director": "Direktion", "conductor": "Direktion", "score": "Partitur", "partitur": "Partitur"
        }

        keys_map = {
            "bb": "in B", "b": "in B", 
            "eb": "in Es", "es": "in Es", 
            "c": "in C", 
            "f": "in F",
            "ab": "in As" # Less common but possible
        }
        
        # Regex for numbers: "1", "1.", "I", "1st"
        # Match standalone numbers or suffix numbers
        # We'll just look for these tokens in the line
        
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if not text: continue
            
            # Focus on top 30% of text for headers to avoid false positives in cues
            lines = text.split('\n')
            header_lines = lines[:int(len(lines)*0.3) + 5] # At least top 5 lines or 30%
            
            found_on_page = []

            for line in header_lines:
                line_lower = line.lower()
                
                # Check for instruments
                detected_inst = None
                longest_match = 0
                
                for key, val in instruments_map.items():
                    if key in line_lower:
                        # Prefer longer matches (e.g. "Tenor Sax" over "Sax")
                        if len(key) > longest_match:
                            longest_match = len(key)
                            detected_inst = val
                            
                if detected_inst:
                    # We found an instrument! Now look for details in the SAME line.
                    
                    # 1. Number detection
                    number = ""
                    # Look for explicit "1", "2", "3", "4"
                    # Or "I", "II", "III"
                    # Or "1st", "2nd"
                    
                    # Simple token check is safer than regex sometimes
                    tokens = line_lower.replace('.', ' ').replace(',', ' ').split()
                    
                    if '1' in tokens or '1st' in tokens or 'i' in tokens: number = "1"
                    elif '2' in tokens or '2nd' in tokens or 'ii' in tokens: number = "2"
                    elif '3' in tokens or '3rd' in tokens or 'iii' in tokens: number = "3"
                    elif '4' in tokens or '4th' in tokens or 'iv' in tokens: number = "4"
                    
                    # 2. Key detection
                    key_sig = ""
                    for k_key, k_val in keys_map.items():
                         # Check strict tokens "in Bb" or just "Bb" if typical?
                         # "Trumpet in Bb" -> "in bb" found
                         # "Flute C" -> "c" found. 
                         # Careful with single letters. "in C" is safe. "C" might be title.
                         
                         pat_in = f"in {k_key}"
                         if pat_in in line_lower:
                             key_sig = k_val
                             break
                         
                         # Special cases like "Eb Horn", "Bb Trumpet" (Prefix)
                         pat_pre = f"{k_key} {detected_inst.lower()}"
                         if pat_pre in line_lower:
                             key_sig = k_val
                             break
                         
                         # "Trumpet Bb" (Suffix)
                         pat_suf = f"{detected_inst.lower()} {k_key}"
                         if pat_suf in line_lower:
                             key_sig = k_val
                             break
                    
                    # Build Part Name
                    # Standard Format: "Instrument [Number] [Key]"
                    # E.g. "Trompete 1 in B", "Flöte in C"
                    
                    full_name = detected_inst
                    if number:
                        full_name += f" {number}"
                    if key_sig:
                        full_name += f" {key_sig}"
                        
                    found_on_page.append(full_name)
            
            # If nothing specific found, maybe mark as "Unbekannt" or skip?
            # Better skip if nothing confident found to avoid "Unbekannt" cluttering 
            # if it's just a blank page or intro. 
            # But the user needs to see every page?
            # The "All" filter handles showing everything. 
            # The parts filter is for specific selection.
            # So only add if we confirm something.
            
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
        
    # Re-use the regex logic but with provided text instead of PDF extraction
    parts = {}
    
    # 1. Definitions (Same as in analyze_parts)
    instruments_map = {
        "piccolo": "Piccolo", "flute": "Flöte", "flöte": "Flöte", "floete": "Flöte",
        "oboe": "Oboe", "clarinet": "Klarinette", "klarinette": "Klarinette",
        "bassoon": "Fagott", "fagott": "Fagott", "saxophone": "Saxophon", "saxophon": "Saxophon",
        "cornet": "Kornett", "kornett": "Kornett", "trumpet": "Trompete", "trompete": "Trompete", 
        "flugelhorn": "Flügelhorn", "flügelhorn": "Flügelhorn", "fluegelhorn": "Flügelhorn",
        "horn": "Horn", "french horn": "Horn", "trombone": "Posaune", "posaune": "Posaune",
        "baritone": "Bariton", "bariton": "Bariton", "euphonium": "Euphonium", "tenorhorn": "Tenorhorn",
        "tuba": "Tuba", "bass": "Tuba", "basses": "Tuba", "drums": "Schlagzeug",
        "percussion": "Percussion", "pauken": "Pauken", "timpani": "Pauken",
        "mallets": "Mallets", "glockenspiel": "Glockenspiel",
        "director": "Direktion", "conductor": "Direktion", "score": "Partitur", "partitur": "Partitur"
    }

    keys_map = {
        "bb": "in B", "b": "in B", "eb": "in Es", "es": "in Es", 
        "c": "in C", "f": "in F", "ab": "in As"
    }
    
    # Process each page
    for p_key, text in page_texts.items():
        try:
            page_num = int(p_key.replace('page_', ''))
        except:
            continue
            
        if not text: continue
        
        found_on_page = []
        lines = text.lower().split('\n')
        
        for line in lines:
            detected_inst = None
            longest_match = 0
            
            for key, val in instruments_map.items():
                if key in line:
                    if len(key) > longest_match:
                        longest_match = len(key)
                        detected_inst = val
            
            if detected_inst:
                number = ""
                tokens = line.replace('.', ' ').replace(',', ' ').split()
                if '1' in tokens or '1st' in tokens or 'i' in tokens: number = "1"
                elif '2' in tokens or '2nd' in tokens or 'ii' in tokens: number = "2"
                elif '3' in tokens or '3rd' in tokens or 'iii' in tokens: number = "3"
                elif '4' in tokens or '4th' in tokens or 'iv' in tokens: number = "4"
                
                key_sig = ""
                for k_key, k_val in keys_map.items():
                     if f"in {k_key}" in line:
                         key_sig = k_val
                         break
                     if f"{k_key} {detected_inst.lower()}" in line or f"{detected_inst.lower()} {k_key}" in line:
                         key_sig = k_val
                         break
                
                full_name = detected_inst
                if number: full_name += f" {number}"
                if key_sig: full_name += f" {key_sig}"
                found_on_page.append(full_name)
        
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
    
    # Locations to scan
    scan_paths = [STORAGE_PATH]
    debug_info.append(f"Local storage: {STORAGE_PATH}")
    
    # Check multiple common USB mount locations
    usb_search_paths = [
        '/media',      # Check all /media subdirectories
        '/mnt',        # Alternative mount point
        '/media/pi',   # Older Raspberry Pi OS
    ]
    
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

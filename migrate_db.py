import sqlite3
import os

db_path = 'instance/music.db'
if not os.path.exists(db_path):
    db_path = 'music.db'

if os.path.exists(db_path):
    print(f"Migrating {db_path}...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("ALTER TABLE song ADD COLUMN settings JSON")
        print("Added 'settings' column.")
    except sqlite3.OperationalError:
        print("'settings' column already exists.")
        
    try:
        cursor.execute("ALTER TABLE song ADD COLUMN bounding_boxes JSON")
        print("Added 'bounding_boxes' column.")
    except sqlite3.OperationalError:
        print("'bounding_boxes' column already exists.")
        
    conn.commit()
    conn.close()
    print("Migration complete.")
else:
    print("Database not found, skip migration.")

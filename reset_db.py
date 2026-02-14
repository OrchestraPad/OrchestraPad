from app import app, db
import os

if os.path.exists("instance/music.db"):
    os.remove("instance/music.db")
elif os.path.exists("music.db"):
    os.remove("music.db")

with app.app_context():
    db.create_all()
    print("Database recreated with new schema!")

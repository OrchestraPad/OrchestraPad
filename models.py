from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    composer = db.Column(db.String(100), nullable=True)
    arranger = db.Column(db.String(100), nullable=True)
    genre = db.Column(db.String(50), nullable=True)
    file_path = db.Column(db.String(500), unique=True, nullable=False)
    detected_parts = db.Column(db.JSON, nullable=True) # Stores {instrument: [pages]}
    settings = db.Column(db.JSON, nullable=True) # Stores {zoom, manualPages, part}
    bounding_boxes = db.Column(db.JSON, nullable=True) # Stores {virtualPageIndex: {x, y, w, h}}

class Setlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    songs = db.relationship('SetlistSong', backref='setlist', cascade='all, delete-orphan')

class SetlistSong(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    setlist_id = db.Column(db.Integer, db.ForeignKey('setlist.id'), nullable=False)
    song_id = db.Column(db.Integer, db.ForeignKey('song.id'), nullable=False)
    position = db.Column(db.Integer, nullable=False) # Order in the list
    song = db.relationship('Song')

import 'package:sqflite/sqflite.dart';
import 'package:path/path.dart';
import 'models.dart';

class DatabaseHelper {
  static final DatabaseHelper instance = DatabaseHelper._init();
  static Database? _database;

  DatabaseHelper._init();

  Future<Database> get database async {
    if (_database != null) return _database!;
    _database = await _initDB('orchestrapad.db');
    return _database!;
  }

  Future<Database> _initDB(String filePath) async {
    final dbPath = await getDatabasesPath();
    final path = join(dbPath, filePath);

    return await openDatabase(path, version: 1, onCreate: _createDB);
  }

  Future _createDB(Database db, int version) async {
    const idType = 'INTEGER PRIMARY KEY AUTOINCREMENT';
    const textType = 'TEXT NOT NULL';
    const textNullable = 'TEXT';
    
    // Song Table
    await db.execute('''
CREATE TABLE song ( 
  id $idType, 
  title $textType,
  composer $textNullable,
  arranger $textNullable,
  genre $textNullable,
  file_path $textType,
  cloud_id $textNullable,
  settings $textNullable
  )
''');

    // Setlist Table
    await db.execute('''
CREATE TABLE setlist ( 
  id $idType, 
  name $textType
  )
''');

    // SetlistSong Association Table (Many-to-Many)
    await db.execute('''
CREATE TABLE setlist_song ( 
  setlist_id INTEGER NOT NULL,
  song_id INTEGER NOT NULL,
  FOREIGN KEY (setlist_id) REFERENCES setlist (id) ON DELETE CASCADE,
  FOREIGN KEY (song_id) REFERENCES song (id) ON DELETE CASCADE,
  PRIMARY KEY (setlist_id, song_id)
  )
''');
  }

  // --- Song Operations ---
  Future<int> createSong(Song song) async {
    final db = await instance.database;
    return await db.insert('song', song.toMap());
  }

  Future<Song?> readSong(int id) async {
    final db = await instance.database;
    final maps = await db.query(
      'song',
      columns: ['id', 'title', 'composer', 'arranger', 'genre', 'file_path', 'cloud_id'],
      where: 'id = ?',
      whereArgs: [id],
    );

    if (maps.isNotEmpty) return Song.fromMap(maps.first);
    return null;
  }

  Future<Song?> readSongByCloudId(String? cloudId) async {
    if (cloudId == null) return null;
    final db = await instance.database;
    final maps = await db.query(
      'song',
      where: 'cloud_id = ?',
      whereArgs: [cloudId],
    );
    if (maps.isNotEmpty) return Song.fromMap(maps.first);
    return null;
  }

  Future<Song?> readSongByTitle(String title) async {
    final db = await instance.database;
    final maps = await db.query(
      'song',
      where: 'title = ?',
      whereArgs: [title],
    );
    if (maps.isNotEmpty) return Song.fromMap(maps.first);
    return null;
  }

  Future<List<Song>> readAllSongs() async {
    final db = await instance.database;
    final orderBy = 'title ASC';
    final result = await db.query('song', orderBy: orderBy);

    return result.map((json) => Song.fromMap(json)).toList();
  }

  Future<int> updateSong(Song song) async {
    final db = await instance.database;
    return db.update(
      'song',
      song.toMap(),
      where: 'id = ?',
      whereArgs: [song.id],
    );
  }

  Future<int> deleteSong(int id) async {
    final db = await instance.database;
    return await db.delete(
      'song',
      where: 'id = ?',
      whereArgs: [id],
    );
  }
}


class Song {
  final int? id;
  final String title;
  final String? composer;
  final String? arranger;
  final String? genre;
  final String filePath;
  final String? cloudId;
  final String? settings; // JSON string for {zoom, manualPages, etc}

  Song({
    this.id,
    required this.title,
    this.composer,
    this.arranger,
    this.genre,
    required this.filePath,
    this.cloudId,
    this.settings,
  });

  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'title': title,
      'composer': composer,
      'arranger': arranger,
      'genre': genre,
      'file_path': filePath,
      'cloud_id': cloudId,
      'settings': settings,
    };
  }

  factory Song.fromMap(Map<String, dynamic> map) {
    return Song(
      id: map['id'],
      title: map['title'],
      composer: map['composer'],
      arranger: map['arranger'],
      genre: map['genre'],
      filePath: map['file_path'],
      cloudId: map['cloud_id'],
      settings: map['settings'],
    );
  }
}

class Setlist {
  final int? id;
  final String name;

  Setlist({this.id, required this.name});

  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'name': name,
    };
  }
}

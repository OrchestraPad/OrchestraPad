import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'models.dart';
import 'database_helper.dart';
import 'cloud_service.dart';
import 'pdf_viewer_screen.dart';

void main() {
  runApp(const OrchestraPadApp());
}

class OrchestraPadApp extends StatelessWidget {
  const OrchestraPadApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'OrchestraPad',
      theme: _buildTheme(),
      home: const HomeScreen(),
    );
  }

  ThemeData _buildTheme() {
    final base = ThemeData.dark();
    return base.copyWith(
      primaryColor: const Color(0xFFD32F2F), // --md-sys-color-primary
      scaffoldBackgroundColor: const Color(0xFF000000), // --md-sys-color-surface
      colorScheme: base.colorScheme.copyWith(
        primary: const Color(0xFFD32F2F),
        secondary: const Color(0xFF775656),
        surface: const Color(0xFF000000),
        onSurface: const Color(0xFFE6E1E5),
      ),
      textTheme: GoogleFonts.robotoTextTheme(base.textTheme),
    );
  }
}

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  late Future<List<Song>> _songsFuture;

  @override
  void initState() {
    super.initState();
    _refreshSongs();
  }

  void _refreshSongs() {
    setState(() {
      _songsFuture = DatabaseHelper.instance.readAllSongs();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Alle Noten'),
        backgroundColor: const Color(0xFF25232a),
        actions: [
          IconButton(icon: const Icon(Icons.refresh), onPressed: _refreshSongs),
          IconButton(icon: const Icon(Icons.settings), onPressed: _showSettingsDialog),
        ],
      ),
      drawer: _buildSidebar(context),
      body: FutureBuilder<List<Song>>(
        future: _songsFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snapshot.hasError) {
            return Center(child: Text('Fehler: ${snapshot.error}'));
          }
          final songs = snapshot.data!;
          if (songs.isEmpty) {
            return const Center(
              child: Text(
                'Noch keine Noten gefunden.\nBitte Sync starten.',
                textAlign: TextAlign.center,
                style: TextStyle(color: Color(0xFFCAC4D0)),
              ),
            );
          }
          return _buildSongGrid(songs);
        },
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () {
          // TODO: Trigger Sync
        },
        icon: const Icon(Icons.cloud_download),
        label: const Text('Sync'),
        backgroundColor: const Color(0xFFD32F2F),
      ),
    );
  }

  Widget _buildSongGrid(List<Song> songs) {
    return GridView.builder(
      padding: const EdgeInsets.all(16),
      gridDelegate: const SliverGridDelegateWithMaxCrossAxisExtent(
        maxCrossAxisExtent: 300,
        childAspectRatio: 1.2,
        crossAxisSpacing: 16,
        mainAxisSpacing: 16,
      ),
      itemCount: songs.length,
      itemBuilder: (context, index) {
        final song = songs[index];
        return Card(
          color: const Color(0xFF25232a), // surface-variant
          shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(16),
              side: const BorderSide(color: Color(0xFF333333), width: 2)),
          child: InkWell(
            onTap: () {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => PdfViewerScreen(song: song),
                ),
              );
            },
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(Icons.music_note, size: 48, color: Colors.white),
                  const SizedBox(height: 12),
                  Text(
                    song.title,
                    style: const TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                        color: Colors.white),
                    textAlign: TextAlign.center,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                  if (song.composer != null)
                    Text(
                      song.composer!,
                      style: const TextStyle(color: Colors.grey),
                      textAlign: TextAlign.center,
                    ),
                ],
              ),
            ),
          ),
        );
      },
    );
  }

  Widget _buildSidebar(BuildContext context) {
     // ... (Sidebar code matches previous structure)
    return Drawer(
      backgroundColor: const Color(0xFF111111),
      child: ListView(
        padding: EdgeInsets.zero,
        children: [
          const DrawerHeader(
            decoration: BoxDecoration(color: Color(0xFF801313)),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                Text(
                  'OrchestraPad',
                  style: TextStyle(color: Colors.white, fontSize: 24, fontWeight: FontWeight.bold),
                ),
                SizedBox(height: 8),
                Text('Bibliothek', style: TextStyle(color: Colors.white70)),
              ],
            ),
          ),
          ListTile(
            leading: const Icon(Icons.music_note, color: Colors.white),
            title: const Text('Alle Noten', style: TextStyle(color: Colors.white)),
            onTap: () {},
          ),
          const Divider(color: Colors.grey),
          const Padding(
            padding: EdgeInsets.all(16.0),
            child: Text('KONZERTMAPPEN', style: TextStyle(color: Colors.grey, fontSize: 12)),
          ),
        ],
      ),
    );
  }
}

import 'package:flutter/material.dart';
import 'package:flutter_pdfview/flutter_pdfview.dart';
import 'models.dart';
import 'dart:io';

class PdfViewerScreen extends StatefulWidget {
  final Song song;

  const PdfViewerScreen({super.key, required this.song});

  @override
  State<PdfViewerScreen> createState() => _PdfViewerScreenState();
}

import 'dart:convert';
import 'database_helper.dart';

class PdfViewerScreen extends StatefulWidget {
  final Song song;

  const PdfViewerScreen({super.key, required this.song});

  @override
  State<PdfViewerScreen> createState() => _PdfViewerScreenState();
}

class _PdfViewerScreenState extends State<PdfViewerScreen> {
  int _totalPages = 0;
  int _currentPage = 0;
  bool _ready = false;
  bool _showGrid = false;
  PDFViewController? _controller;
  
  List<int> _manualPages = []; // 0-indexed page numbers

  @override
  void initState() {
    super.initState();
    _loadSettings();
  }

  void _loadSettings() {
    if (widget.song.settings != null) {
      try {
        final Map<String, dynamic> settings = jsonDecode(widget.song.settings!);
        if (settings['manualPages'] != null) {
           _manualPages = List<int>.from(settings['manualPages']);
        }
      } catch (e) {
        print("Error loading settings: $e");
      }
    }
  }

  Future<void> _saveSettings() async {
    final Map<String, dynamic> settings = {};
    if (widget.song.settings != null) {
       try {
         settings.addAll(jsonDecode(widget.song.settings!));
       } catch (_) {}
    }
    settings['manualPages'] = _manualPages;
    
    final updatedSong = Song(
      id: widget.song.id,
      title: widget.song.title,
      filePath: widget.song.filePath,
      cloudId: widget.song.cloudId,
      settings: jsonEncode(settings),
    );
    
    await DatabaseHelper.instance.updateSong(updatedSong);
  }

  @override
  Widget build(BuildContext context) {
    if (_showGrid) return _buildPageGrid();

    return Scaffold(
      backgroundColor: Colors.black, // Immersive mode
      appBar: _ready ? null : AppBar( // Hide AppBar when reading
        title: Text(widget.song.title),
        backgroundColor: Colors.black,
        actions: [
          IconButton(
            icon: const Icon(Icons.grid_view),
            onPressed: () => setState(() => _showGrid = true),
          )
        ],
      ),
      
      body: Stack(
        children: [
          PDFView(
            filePath: widget.song.filePath,
            enableSwipe: true,
            swipeHorizontal: true, // Book mode
            autoSpacing: true,
            pageFling: true,
            pageSnap: true,
            defaultPage: 0,
            fitPolicy: FitPolicy.BOTH,
            preventLinkNavigation: false,
            onRender: (_pages) {
              setState(() {
                _totalPages = _pages!;
                _ready = true;
              });
            },
            onPageChanged: (int? page, int? total) {
              setState(() {
                _currentPage = page!;
              });
              // Simple "Skip" logic could go here
            },
            onViewCreated: (PDFViewController pdfViewController) {
              _controller = pdfViewController;
            },
          ),
          // ... (Overlays remain same)
          if (_ready) ...[
             // Touch area for Menu
             Positioned(
               top: 0, left: 0, right: 0, height: 100,
               child: GestureDetector(
                 onTap: () => setState(() => _showGrid = true),
                 behavior: HitTestBehavior.translucent,
                 child: Container(color: Colors.transparent),
               ),
             ),
          ],
          if (!_ready)
            const Center(
              child: CircularProgressIndicator(),
            ),
            
          // Floating Page Indicator
          if (_ready)
             Positioned(
               bottom: 20,
               right: 20,
               child: Container(
                 padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                 decoration: BoxDecoration(
                   color: Colors.black54,
                   borderRadius: BorderRadius.circular(20),
                 ),
                 child: Text(
                   "${_currentPage + 1} / $_totalPages",
                   style: const TextStyle(color: Colors.white),
                 ),
               ),
             ),
             
  Widget _buildPageGrid() {
    return Scaffold(
      backgroundColor: const Color(0xFF25232a), // Dark surface
      appBar: AppBar(
        title: const Text('Seiten auswählen (Stimmen)'),
        backgroundColor: const Color(0xFF25232a),
        leading: IconButton(
          icon: const Icon(Icons.check),
          onPressed: () {
            _saveSettings();
            setState(() => _showGrid = false);
          },
        ),
      ),
      body: GridView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: _totalPages,
        gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
            crossAxisCount: 4, crossAxisSpacing: 10, mainAxisSpacing: 10),
        itemBuilder: (context, index) {
          final isSelected = _manualPages.contains(index);
          return GestureDetector(
            onTap: () {
              setState(() {
                if (isSelected) {
                  _manualPages.remove(index);
                } else {
                  _manualPages.add(index);
                  _manualPages.sort();
                }
              });
            },
            child: Container(
              decoration: BoxDecoration(
                color: isSelected ? const Color(0xFFD32F2F) : Colors.grey[800],
                borderRadius: BorderRadius.circular(8),
                border: isSelected ? Border.all(color: Colors.white, width: 2) : null,
              ),
              alignment: Alignment.center,
              child: Text(
                "${index + 1}",
                style: const TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold),
              ),
            ),
          );
        },
      ),
    );
  }
}

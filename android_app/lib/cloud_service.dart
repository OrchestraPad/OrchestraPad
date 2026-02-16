import 'dart:io';
import 'package:http/http.dart' as http;
import 'package:path_provider/path_provider.dart';
import 'package:path/path.dart' as path;
import 'models.dart';
import 'database_helper.dart';

class CloudService {
  final DatabaseHelper _db = DatabaseHelper.instance;

  // Regex to extract file information from Google Drive Folder HTML
  // This is a "best effort" scraper similar to what gdown might do internally
  // roughly looking for keys like "dspId" or client-side data blocks.
  // NOTE: A robust standalone implementation usually requires the Drive API.
  // For '1:1' simulation without API keys, we might need a simpler contract:
  // "Please provide a direct ZIP link" is significantly more reliable.
  
  // However, let's try to support the folder link by looking for the underlying query.
  
  Future<List<String>> syncFromLink(String driveLink) async {
    final log = <String>[];
    log.add("Starting Sync from: $driveLink");

    try {
      final cleanUrl = _sanitizeUrl(driveLink);
      log.add("Cleaned URL: $cleanUrl");

      final appDir = await getApplicationDocumentsDirectory();
      final musicDir = Directory(path.join(appDir.path, 'Noten'));
      if (!await musicDir.exists()) {
        await musicDir.create();
      }

      if (cleanUrl.contains("/folders/")) {
         log.add("Detected Folder Link. Attempting to scrape file IDs...");
         // 1. Get the Folder Page
         final response = await http.get(Uri.parse(cleanUrl));
         if (response.statusCode == 200) {
            final html = response.body;
            // 2. Extract File IDs (Heavy Heuristic)
            // Look for patterns like: ["FILE_ID","FILE_NAME",...]
            // Google Drive HTML is obfuscated, but IDs often appear in "clientSideData" or similar blocks.
            // We look for the generic ID pattern: [a-zA-Z0-9_-]{25,}
            
            // This is a simplified regex to find potential file IDs. 
            // Real gdown uses much more complex parsing.
            final idPattern = RegExp(r'"([a-zA-Z0-9_-]{25,})"');
            final matches = idPattern.allMatches(html);
            
            final potentialIds = <String>{};
            for (final m in matches) {
              final id = m.group(1)!;
              // Filter out common non-file strings
              if (id.contains("goog") || id.length < 20) continue; 
              potentialIds.add(id);
            }

            log.add("Found ${potentialIds.length} potential items. Attempting downloads...");
            
            int successCount = 0;
            for (final id in potentialIds) {
               // Try to download as if it's a file.
               // If it's a subfolder or garbage ID, download will fail or return HTML.
               // We verify content-type.
               try {
                 final success = await _downloadFileById(id, musicDir, log);
                 if (success) successCount++;
               } catch (e) {
                 // Ignore errors for individual IDs (likely not files)
               }
            }
            
            if (successCount == 0) {
              log.add("Warning: No valid PDF/Image files extracted. Google Drive structure might have changed.");
              log.add("Fallback: Please use a direct link to a single ZIP file.");
            }
            
         } else {
           log.add("Error: Could not access folder page. Status ${response.statusCode}");
         }

      } else {
         // Single File
         await _downloadFile(cleanUrl, musicDir, log);
      }
      
    } catch (e) {
      log.add("Critical Error: $e");
    }

    return log;
  }

  Future<bool> _downloadFileById(String id, Directory targetDir, List<String> log) async {
      final url = "https://drive.google.com/uc?export=download&id=$id";
      try {
        final response = await http.get(Uri.parse(url));
        if (response.statusCode == 200) {
           final contentType = response.headers['content-type'] ?? '';
           
           // Filter: Only Allow PDF or Images or Zip
           if (!contentType.contains("application/pdf") && 
               !contentType.contains("image/") &&
               !contentType.contains("zip")) {
               return false;
           }

           String filename = "$id.pdf";
           if (response.headers.containsKey('content-disposition')) {
              final disposition = response.headers['content-disposition']!;
              if (disposition.contains('filename=')) {
                filename = disposition.split('filename=')[1].replaceAll('"', '').replaceAll(";", "");
              }
           }
           
           final file = File(path.join(targetDir.path, filename));
           await file.writeAsBytes(response.bodyBytes);
           log.add("Downloaded: $filename");
           await _addToDatabase(file, cloudId: id);
           return true;
        }
      } catch (e) {
        return false;
      }
      return false;
  }

  Future<void> _downloadFile(String url, Directory targetDir, List<String> log) async {
    // ... (Keep existing simple logic for direct links)
     final idMatch = RegExp(r'/d/([a-zA-Z0-9_-]+)').firstMatch(url);
     String downloadUrl = url;
    
    if (idMatch != null) {
       await _downloadFileById(idMatch.group(1)!, targetDir, log);
    } else {
       // Direct HTTP link (non-Google)
       final response = await http.get(Uri.parse(url));
       if (response.statusCode == 200) {
          String filename = "download_${DateTime.now().millisecondsSinceEpoch}.pdf";
          final file = File(path.join(targetDir.path, filename));
          await file.writeAsBytes(response.bodyBytes);
          log.add("Downloaded: $filename");
          await _addToDatabase(file);
       }
    }
  }

  Future<void> _addToDatabase(File file, {String? cloudId}) async {
     final filename = path.basename(file.path);
     final title = filename.replaceAll('.pdf', '').replaceAll('_', ' ');
     
     // Check if song exists with this cloudId or path
     // Simple duplication check
     final existing = await _db.readSongByCloudId(cloudId) ?? await _db.readSongByTitle(title);
     
     if (existing == null) {
       final song = Song(
         title: title,
         filePath: file.path,
         cloudId: cloudId,
       );
       await _db.createSong(song);
     }
  }

  String _sanitizeUrl(String url) {
    // Reuse Python logic logic
    if (url.contains('drive.google.com') && url.contains('folders/')) {
       final match = RegExp(r'folders/([a-zA-Z0-9_-]+)').firstMatch(url);
       if (match != null) {
         return 'https://drive.google.com/drive/folders/${match.group(1)}';
       }
    }
    return url;
  }
}

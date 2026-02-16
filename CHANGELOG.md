# Versionsverlauf - OrchestraPad

Alle wichtigen Änderungen an diesem Projekt werden in dieser Datei festgehalten.

## v1.3.2 (2026-02-16)
### Hinzugefügt
- **Branding**: Neues Vereins-Logo ("OrchestraPad") in der Titelleiste und im Viewer integriert.
- **Icon**: App-Icon für Android hinzugefügt.

## v1.2.12 (2026-02-14)
- Fix: Critical bug fixed (Black Screen on Raspberry Pi)
- Security: OCR Installation script improved
- System: Update scripts improved for Raspberry Pi

## v1.3.0 (2026-02-14)
### Neu
- **Smart OCR (Stimmen-Trainer)**: Man kann jetzt im Viewer oben einen Bereich markieren, wo der Instrumentenname steht. Das System scannt dann **nur** diesen Bereich auf allen Seiten. Das ist viel schneller und genauer als der Volltext-Scan.
- **Backend**: Neue Schnittstellen für Bildverarbeitung und Texterkennung (`pdf2image`, `tesseract`) integriert.

## [1.2.12] - 2026-02-14
### Behoben
- **Technischer Fehler**: Fehlende Schnittstelle für das Hinzufügen von Stücken zu Mappen ergänzt. Jetzt werden die Stücke auch tatsächlich gespeichert.

## [1.2.11] - 2026-02-14
### Neu
- **Mappen-Workflow**: Hinzufügen zu Mappen erfordert jetzt eine Auswahl und anschließende Bestätigung ("Hinzufügen"-Button), um Fehler zu vermeiden.
- **Smart Scan**: Der Scanner überspringt jetzt bereits existierende Dateien, um Duplikate zu verhindern und schneller zu sein.

## [1.2.10] - 2026-02-14
### Behoben
- **Mappen-Auswahl**: Einträge im Dialog sind jetzt deutlich als Buttons erkennbar (mit Hintergrund und Rahmen) und reagieren zuverlässig auf Klicks.

## [1.2.9] - 2026-02-14
### Behoben
- **Mappen-Auswahl**: Klick-Handler vereinfacht, um Kompatibilitätsprobleme auf dem Raspberry Pi zu beheben.

## [1.2.8] - 2026-02-14
### Behoben
- **Mappen-Auswahl**: Klickbarkeit im "Hinzufügen"-Dialog durch Verwendung von echten Buttons statt Divs verbessert.

## [1.2.7] - 2026-02-14
### Behoben
- **Scan Info**: Debug-Informationen beim Scannen entfernt.
- **Mappen-Auswahl**: Problem behoben, bei dem Mappen im "Hinzufügen"-Dialog nicht anklickbar waren.

## [1.2.6] - 2026-02-14
### Behoben
- **JS Fehler**: `loadSongs is not defined` behoben (ersetzt durch `location.reload`).
- **Button-Logik**: In der Konzertmappen-Ansicht wird nun nur noch der "Aus Mappe entfernen" Button angezeigt, um versehentliches Löschen der Datei zu verhindern.

## [1.2.5] - 2026-02-14
### Behoben
- **Löschen-Button in allen Ansichten**: Der Löschen-Button wird nun auch beim ersten Laden der Bibliothek ("Alle Noten") korrekt angezeigt.

## [1.2.4] - 2026-02-14
### Behoben
- **Löschen-Button sichtbar**: Buttons werden jetzt korrekt in allen Ansichten angezeigt (Library und Setlists).

## [1.2.3] - 2026-02-14
### Hinzugefügt
- **Force Update Script**: `force_update.sh` stoppt den Service, macht Hard Reset und startet neu, um Template-Updates zu erzwingen.

## [1.2.2] - 2026-02-14
### Behoben
- **Update-Mechanismus**: `update.sh` erzwingt jetzt einen Hard Reset, um sicherzustellen, dass alle Änderungen vom Server übernommen werden.

## [1.2.1] - 2026-02-14
### Hinzugefügt
- **Löschen-Funktion**: Stücke können jetzt über einen Löschen-Button in der Bibliothek entfernt werden. Löscht sowohl den Datenbank-Eintrag als auch die PDF-Datei.

## [1.2.0] - 2026-02-14
### Hinzugefügt
- **Automatisches Kopieren**: PDFs vom USB-Stick werden jetzt automatisch auf die SD-Karte kopiert. Stücke funktionieren auch nach Entfernen des USB-Sticks.

### Behoben
- **Schwarzer Bildschirm**: USB-Stücke lassen sich jetzt korrekt öffnen.

## [1.1.11] - 2026-02-14
### Verbessert
- **USB-Erkennung**: Sucht jetzt an mehreren Orten nach USB-Sticks (/media/*, /mnt/*, etc.) statt nur /media/pi.

## [1.1.10] - 2026-02-14
### Behoben
- **Kritischer Fehler**: Aktualisieren-Button funktioniert wieder (Funktionsname korrigiert).

## [1.1.9] - 2026-02-14
### Hinzugefügt
- **Debug-Info**: Beim "Aktualisieren" werden jetzt detaillierte Informationen angezeigt, welche Pfade gescannt werden und warum USB-Sticks eventuell nicht gefunden werden.

## [1.1.8] - 2026-02-14
### Behoben
- **Kritischer Fehler**: Schwarzer Bildschirm beim Öffnen von Stücken (JavaScript-Referenzfehler in viewer.html).
- **Scan-Fehler**: Aktualisieren-Button funktioniert jetzt wieder korrekt.

## [1.1.7] - 2026-02-14
### Hinzugefügt
- **Dauerhafte Einstellungen**: Zoom, Seitenwahl und Stimmen-Filter werden jetzt in der Datenbank gespeichert und bleiben auch nach einem Neustart (im Inkognito-Modus) erhalten.
- **USB-Autosuche**: Beim Aktualisieren werden nun alle angeschlossenen USB-Sticks (unter `/media/pi/`) automatisch nach PDFs durchsucht.

### Optimiert
- **Blätter-Geschwindigkeit**: Der optimale Seitenzuschnitt (Auto-Crop) wird jetzt gecacht, was das Umblättern deutlich beschleunigt.

## [1.1.6] - 2026-02-14
### Behoben
- **Beenden-Fehler**: Server-Beenden verzögert, um "Failed to fetch" Fehler zu vermeiden.
- **Benutzerführung**: Eingabefeld für neue Mappen nach oben verschoben für bessere Erreichbarkeit.
- **Design**: Schriftfarbe im Eingabefeld korrigiert (weiß auf schwarzem Grund).

## [1.1.5] - 2026-02-14
### Behoben
- **Keyring-Popup**: Unterdrückung des "Unlock Keyring" Fensters beim Browserstart durch Chromium-Flags.
- **Benutzererfahrung**: Reibungsloserer Autostart ohne manuelle Passwort-Eingabe.

## [1.1.4] - 2026-02-14
### Behoben
- **Autostart-Diagnose**: Ein Log-File (`autostart.log`) wird nun erstellt, um Startprobleme auf dem Pi zu analysieren.
- **Kompatibilität**: Autostart-Befehl für verschiedene Raspberry Pi OS Versionen optimiert.
- **Wartezeit**: Erhöhung der Startverzögerung auf 15 Sekunden für langsamere SD-Karten.

## [1.1.3] - 2026-02-14
### Hinzugefügt
- **Systemsteuerung**: Neue Buttons in der Sidebar zum Beenden des Programms oder zum Herunterfahren des Raspberry Pi.
- **Sicherheitsabfrage**: Bestätigungsdialoge vor dem Beenden/Ausschalten.

## [1.1.2] - 2026-02-14
### Behoben
- **Autostart-Fix**: Umstellung auf ein dediziertes Start-Skript (`start_app.sh`), um Zuverlässigkeitsprobleme beim Kiosk-Moduls zu beheben.
- **Timing optimiert**: Wartezeit für den Serverstart auf 12 Sekunden erhöht.

## [1.1.1] - 2026-02-14
### Hinzugefügt
- **Autostart-Assistent**: `setup_pi.sh` fragt nun nach der Bildschirmdrehung (Portrait/Landscape).
- **Stabilerer Kiosk-Modus**: Wartezeit beim Start erhöht, um sicherzustellen, dass der Server bereit ist.
- **Persistenz**: Einmal konfiguriert, bleibt die Drehung auch nach Neustarts erhalten.

## [1.1.0] - 2026-02-14
### Hinzugefügt
- **Rebranding**: Programmname von "Notenmappe" zu "**OrchestraPad**" geändert.
- **Ein-Klick-Update**: Updates können nun direkt in der App per Klick gestartet werden.
- **GitHub Integration**: Das Projekt ist nun mit GitHub verknüpft für einfache Updates am Pi.

## [1.0.0] - 2026-02-14
### Hinzugefügt
- **Material Design Redesign**: Komplette Überarbeitung der Benutzeroberfläche in den Vereinsfarben Schwarz und Rot.
- **Touch-Optimierung**: Alle Bedienelemente sind nun ohne Hover-Effekte direkt bedienbar und für Fingerbedienung vergrößert.
- **SVG-Icons**: Ablösung der Emojis durch integrierte Vektorgrafiken für zuverlässige Anzeige auf dem Raspberry Pi.
- **A3-Split Support**: Automatische Erkennung von Querformat-Seiten und Aufteilung in zwei virtuelle Hochformat-Seiten.
- **OCR-Analyse**: Stimmenerkennung zur automatischen Zuordnung von PDF-Seiten zu Instrumenten/Stimmen.
- **Automatisches Setup**: `setup_pi.sh` Skript zur einfachen Installation auf einem neuen Raspberry Pi.
- **Update-Funktion**: Vorbereitung der Infrastruktur für einfache Programm-Updates.

### Geändert
- **PDF-Rendering**: Verbessertes Auto-Crop zum Entfernen von weißen Rändern für maximale Notengröße.
- **Navigation**: Optimierte Navigation mit Pedalen (Tastatur) und Touch-Zonen.
- **Bibliothek**: Neue Sortierfunktionen und verbesserte Metadaten-Ansicht.

---
*Hinweis: Dies ist die erste offizielle Release-Version nach der Design-Überarbeitung.*

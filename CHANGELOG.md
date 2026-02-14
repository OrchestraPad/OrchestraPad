# Versionsverlauf - OrchestraPad

Alle wichtigen Änderungen an diesem Projekt werden in dieser Datei festgehalten.

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

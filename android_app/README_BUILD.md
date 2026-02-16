# Android App Build Instructions

Da du Flutter und Android Studio noch nicht installiert hast, müssen wir diese einmalig einrichten. Danach kannst du die App immer mit einem Doppelklick bauen.

## Schritt 1: Installation (Einmalig)

1.  **Flutter Herunterladen**:
    *   Lade das Flutter SDK herunter: [Flutter Windows Zip](https://storage.googleapis.com/flutter_infra_release/releases/stable/windows/flutter_windows_3.16.9-stable.zip)
    *   Entpacke die Zip-Datei nach `C:\src\flutter` (Erstelle den Ordner, falls nicht vorhanden).

2.  **Android Studio Installieren**:
    *   Lade Android Studio herunter: [Android Studio](https://developer.android.com/studio)
    *   Installiere es und starte es einmal.
    *   Gehe im Start-Wizard auf "Next" bis alles fertig ist (dies installiert das Android SDK).
    *   Wichtig: Öffne in Android Studio "More Actions" -> "SDK Manager" -> "SDK Tools" und setze einen Haken bei "Android SDK Command-line Tools". Klicke "Apply".

3.  **Lizenzen akzeptieren**:
    *   Öffne eine Eingabeaufforderung (cmd) und gib ein:
        ```cmd
        C:\src\flutter\bin\flutter doctor --android-licenses
        ```
    *   Tippe mehrmals `y` und Enter, um alles zu akzeptieren.

## Schritt 1b: Logo einrichten (Optional)

1.  Speichere dein Logo als **`logo.png`** im Ordner:
    `android_app\assets\images\` (Erstelle den Ordner, falls er fehlt).
2.  Um das App-Icon (auf dem Homescreen) zu aktualisieren, führe einmalig diesen Befehl im Ordner `android_app` aus:
    ```cmd
    flutter pub run flutter_launcher_icons
    ```

## Schritt 2: App Bauen (Immer wenn du was änderst)

1.  Öffne den Ordner `android_app`.
2.  Doppelklicke auf die Datei **`build_app.bat`**.
3.  Warte bis das schwarze Fenster fertig ist.
4.  Die fertige App (`app-release.apk`) liegt dann im Ordner:
    `build\app\outputs\flutter-apk\`

## Fehlerbehebung

Wenn `build_app.bat` nicht geht, stelle sicher, dass du Schritt 1 komplett gemacht hast.
Du kannst auch `C:\src\flutter\bin\flutter doctor` in der cmd ausführen, um zu sehen was fehlt.

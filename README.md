# praxis-day06

## Praxis - Auftrag 1: Build-Artefakt mit GitHub Actions hochladen

### Ziel

Du testest zuerst die vorhandene Python/Flask-Demo-App lokal. Danach ergänzt du die bestehende GitHub-Actions-Pipeline so, dass das erzeugte Build-Artefakt gespeichert wird. Zum Schluss lädst du das Artefakt aus GitHub Actions herunter und testest es nochmals lokal.

Das Artefakt wird nur temporär im Workflow gespeichert. Es wird nicht in ein Paket-Repository wie GitHub Packages oder PyPI veröffentlicht.

### Für diese Aufgabe relevante Projektstruktur

```plaintext
praxis-day06/
├── app/
│   ├── __init__.py
│   └── main.py
├── .github/
│   └── workflows/
│       └── artifact_ci.yml
├── setup.py
├── requirements.txt
└── README.md
```

`setup.py` enthält die Paketinformationen für die Demo-App. Damit kann das Projekt als Python-Paket gebaut und installiert werden.

`app/main.py` enthält die Flask-Anwendung. Beim Start der App wird auf Port `5000` eine einfache Webseite ausgeliefert.

`.github/workflows/artifact_ci.yml` enthält die Pipeline, die du ergänzen musst.

## Teil 1: App lokal testen

1. Öffne das Repository lokal in deiner Entwicklungsumgebung.

2. Prüfe, ob Python und pip installiert sind:

   ```bash
   python --version
   python -m pip --version
   ```

   Falls `python` unter Windows nicht funktioniert, verwende:

   ```powershell
   py --version
   py -m pip --version
   ```

3. Nur für Windows empfohlen: Erstelle eine virtuelle Umgebung (`.venv`) und aktiviere sie.

   Dadurch werden Python-Pakete und Befehle wie `run-flask` nur für dieses Projekt installiert. Das verhindert Konflikte mit global installierten Python-Versionen.

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   Falls PowerShell das Aktivieren blockiert:

   ```powershell
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   .\.venv\Scripts\Activate.ps1
   ```

4. Installiere die benötigten Abhängigkeiten:

   ```bash
   python -m pip install --upgrade pip setuptools wheel
   python -m pip install -r requirements.txt
   python -m pip install build
   ```

   Unter Windows mit aktivierter `.venv` verwendest du ebenfalls `python -m pip ...`. So werden die Pakete in der virtuellen Umgebung installiert.

5. Erstelle lokal ein Build-Artefakt:

   ```bash
   python -m build
   ```

   Danach sollte ein Ordner `dist/` mit diesen Dateien vorhanden sein:

   ```plaintext
   flaskapp-0.1.tar.gz
   flaskapp-0.1-py3-none-any.whl
   ```

6. Installiere das lokal gebaute Paket:

   ```bash
   python -m pip install --force-reinstall dist/flaskapp-0.1.tar.gz
   ```

7. Starte die Flask-App:

   ```bash
   run-flask
   ```

8. Öffne im Browser:

   ```text
   http://localhost:5000
   ```

   Wenn alles funktioniert, wird folgende Ausgabe angezeigt:

   ```text
   Hello, from Flask!
   ```

## Teil 2: Pipeline vervollständigen

Öffne die Datei:

```text
.github/workflows/artifact_ci.yml
```

Die Pipeline installiert Python, installiert das Build-Tooling und baut das Paket bereits mit:

```bash
python -m build
```

Ergänze danach einen Schritt, der das erzeugte Build-Artefakt speichert.

Der Upload-Schritt muss:

- nach dem Build-Schritt ausgeführt werden
- das Build-Artefakt mit `actions/upload-artifact` speichern
- einen Artefakt-Namen setzen
- den Ordner `dist/` oder dessen Inhalt hochladen

Committe und pushe deine Änderung:

```bash
git status
git add .github/workflows/artifact_ci.yml
git commit -m "Add build artifact upload"
git push
```

Prüfe danach in GitHub unter `Actions`, ob die Pipeline erfolgreich durchläuft.

Prüfe zusätzlich, ob das Autograding-Ergebnis nach dem Push sichtbar ist und die Aufgabe als bestanden bewertet wird.

## Teil 3: Artefakt herunterladen und lokal testen

1. Öffne dein Repository auf GitHub.

2. Gehe zu:

   ```text
   Actions
   ```

3. Öffne den erfolgreichen Workflow-Lauf von `Build & Upload Artifact`.

4. Lade unten bei `Artifacts` das erzeugte Artefakt herunter.

5. Entpacke die heruntergeladene ZIP-Datei lokal.

6. Installiere das heruntergeladene Paket:

   ```bash
   python -m pip install --force-reinstall flaskapp-0.1.tar.gz
   ```

   Falls du das Wheel testen möchtest:

   ```bash
   python -m pip install --force-reinstall flaskapp-0.1-py3-none-any.whl
   ```

7. Starte die App erneut:

   ```bash
   run-flask
   ```

8. Öffne im Browser:

   ```text
   http://localhost:5000
   ```

### Fehlerbehebung unter Windows: `Fatal error in launcher`

Wenn beim Start von `run-flask` diese Meldung erscheint:

```text
Fatal error in launcher: Unable to create process using ... The system cannot find the file specified.
```

dann verwendet Windows wahrscheinlich einen alten oder falschen `run-flask.exe`-Launcher.

Prüfe zuerst, welches `run-flask` Windows verwendet:

```powershell
where run-flask
```

Wenn dort ein Pfad außerhalb des Projektordners oder außerhalb von `.venv\Scripts` erscheint, starte den Launcher aus der virtuellen Umgebung direkt:

```powershell
.\.venv\Scripts\run-flask.exe
```

Falls diese Datei nicht existiert, installiere das Paket gezielt mit dem Python aus `.venv`:

```powershell
.\.venv\Scripts\python.exe -m pip install --force-reinstall dist/flaskapp-0.1.tar.gz
.\.venv\Scripts\run-flask.exe
```

### Erwartetes Ergebnis

- Die App läuft lokal vor der Pipeline-Anpassung.
- Die Pipeline baut das Python-Paket erfolgreich.
- Die Pipeline speichert den Inhalt von `dist/` als Artefakt.
- Das Autograding-Ergebnis ist nach dem Push sichtbar und erfolgreich.
- Das Artefakt kann aus GitHub Actions heruntergeladen werden.
- Das heruntergeladene Paket lässt sich lokal installieren und starten.

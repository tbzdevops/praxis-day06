# praxis-day06

## Praxis - Auftrag 1: Python Demo App lokal testen

### Ziel

Du testest die vorhandene Python/Flask-Demo-App lokal. Der Code ist bereits im Repository vorhanden. Deine Aufgabe ist es, die Abhängigkeiten zu installieren, ein Python-Build-Artefakt zu erstellen, das Paket lokal zu installieren und die Flask-App im Browser zu prüfen.

### Vorhandene Projektstruktur

```plaintext
praxis-day06/
├── app/
│   ├── __init__.py
│   └── main.py
├── setup.py
├── requirements.txt
└── README.md
```

`setup.py` enthält die Paketinformationen für die Demo-App. Damit kann das Projekt als Python-Paket gebaut und installiert werden.

`app/__init__.py` markiert den Ordner `app` als Python-Paket.

`app/main.py` enthält die Flask-Anwendung. Beim Start der App wird auf Port `5000` eine einfache Webseite ausgeliefert.

### Auftrag

1. Klone das Repository oder öffne es lokal in deiner Entwicklungsumgebung.

2. Prüfe, ob Python und pip installiert sind:

   ```bash
   python --version
   python -m pip --version
   ```

   Falls `python` nicht funktioniert, verwende unter Windows alternativ:

   ```bash
   py --version
   py -m pip --version
   ```

3. Nur für Windows empfohlen: Erstelle eine virtuelle Umgebung (`.venv`) und aktiviere sie.

   Dadurch werden Python-Pakete und Befehle wie `run-flask` nur für dieses Projekt installiert. Das verhindert Konflikte mit global installierten Python-Versionen.

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   Falls du `python` statt `py` verwendest:

   ```bash
   python -m venv .venv
   ```

4. Installiere die benötigten Abhängigkeiten:

   ```bash
   python -m pip install -r requirements.txt
   ```

   Alternative unter Windows:

   ```bash
   py -m pip install -r requirements.txt
   ```

5. Erstelle lokal ein Build-Artefakt:

   ```bash
   python setup.py sdist
   ```

   Alternative unter Windows:

   ```bash
   py setup.py sdist
   ```

   Danach sollte ein Ordner `dist/` mit einem Paket wie `flaskapp-0.1.tar.gz` vorhanden sein.

6. Installiere das gebaute Paket lokal:

   ```bash
   python -m pip install --force-reinstall dist/flaskapp-0.1.tar.gz
   ```

   Alternative unter Windows:

   ```bash
   py -m pip install --force-reinstall dist/flaskapp-0.1.tar.gz
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

### Ohne Container testen

Du kannst die App vollständig ohne Container testen. Nur für Windows empfohlen: Verwende dafür eine virtuelle Umgebung (`.venv`), damit `run-flask` nicht aus einer kaputten globalen Python-Installation gestartet wird.

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install --upgrade pip setuptools wheel
py -m pip install -r requirements.txt
py setup.py sdist
py -m pip install --force-reinstall dist/flaskapp-0.1.tar.gz
run-flask
```

Falls PowerShell das Aktivieren blockiert, kannst du für diese Sitzung die Execution Policy lockern:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### Fehlerbehebung: `Fatal error in launcher`

Wenn beim Start von `run-flask` diese Meldung erscheint:

```text
Fatal error in launcher: Unable to create process using ... The system cannot find the file specified.
```

dann wurde `run-flask.exe` mit einer Python-Installation erzeugt, die nicht mehr existiert oder nicht mehr am gleichen Pfad liegt. Das passiert häufig nach einem Python-Update oder wenn ein Paket außerhalb einer virtuellen Umgebung installiert wurde.

Prüfe zuerst, welches `run-flask` Windows verwendet:

```powershell
where run-flask
```

Wenn dort ein Pfad außerhalb des Projektordners oder außerhalb von `.venv\Scripts` erscheint, wird nicht der Projekt-Launcher verwendet. Starte dann den Launcher aus der virtuellen Umgebung direkt:

```powershell
.\.venv\Scripts\run-flask.exe
```

Falls diese Datei nicht existiert, wurde das Paket nicht in der virtuellen Umgebung installiert. Installiere es dann gezielt mit dem Python aus `.venv`:

```powershell
.\.venv\Scripts\python.exe -m pip install --force-reinstall dist/flaskapp-0.1.tar.gz
.\.venv\Scripts\run-flask.exe
```

Wichtig: Der Fehler entsteht nicht durch Flask selbst, sondern dadurch, dass Windows einen alten oder falschen `run-flask.exe`-Launcher findet.

### Optional: Test in einem Docker-Container

Du kannst das erstellte Paket auch in einem frischen Python-Container testen.

1. Starte einen Container und binde den lokalen `dist`-Ordner ein:

   ```bash
   docker run -it --rm -p 5000:5000 -v "%cd%\dist:/dist" python:3.10-slim bash
   ```

   Falls du PowerShell verwendest:

   ```powershell
   docker run -it --rm -p 5000:5000 -v "${PWD}\dist:/dist" python:3.10-slim bash
   ```

2. Installiere im Container die benötigten Build-Werkzeuge und das Paket:

   ```bash
   pip install --upgrade pip setuptools wheel
   pip install /dist/flaskapp-0.1.tar.gz
   ```

3. Starte die App im Container:

   ```bash
   run-flask
   ```

4. Oeffne im Browser:

   ```text
   http://localhost:5000
   ```

### Erwartetes Ergebnis

- Die Abhängigkeiten lassen sich installieren.
- Mit `python setup.py sdist` wird ein Build-Artefakt im Ordner `dist/` erstellt.
- Das Paket lässt sich aus dem `dist/`-Ordner installieren.
- Die Flask-App startet lokal auf Port `5000`.
- Im Browser erscheint `Hello, from Flask!`.

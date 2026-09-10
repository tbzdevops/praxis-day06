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

## Praxis - Auftrag 2: Eigene PyPI Registry auf AWS betreiben

### Ziel

Du erstellst in AWS Learner Lab eine eigene PyPI-kompatible Package Registry mit `pypiserver`. Danach testest du mit einem einfachen Python-Paket, ob die Registry funktioniert. Zum Schluss erstellst du eine neue CI-Pipeline, welche das gebaute Python-Artefakt in deiner Registry veröffentlicht.

Du kannst für die Infrastruktur entweder Terraform oder OpenTofu verwenden.

### Voraussetzungen

Für diesen Auftrag brauchst du:

- AWS CLI
- Terraform oder OpenTofu
- SSH-Key für den Zugriff auf die EC2-Instanz

### Infrastruktur

Mit den Dateien im Ordner `terraform/` wird folgende Infrastruktur erstellt:

- VPC
- Public Subnet
- Internet Gateway
- Route Table
- Security Group
- EC2-Instanz
- pypiserver als Docker-Container

Die Cloud-init-Datei liegt im Ordner `cloud-init/` und wird über die Terraform-Variable `cloud_init_path` als `user_data` an die EC2-Instanz übergeben.

`pypiserver` wird auf Port `8080` bereitgestellt.

`pypiserver` ist ein leichtgewichtiges Open-Source-Projekt für eine einfache PyPI-kompatible Registry.

### AWS Credentials konfigurieren

Öffne im AWS Learner Lab den Bereich `AWS Details` und kopiere die Werte für `AWS CLI`.

Mit der AWS CLI kannst du dich einfach konfigurieren:

```bash
aws configure
```

Gib danach die Werte aus dem Learner Lab ein:

```text
AWS Access Key ID: <dein-access-key>
AWS Secret Access Key: <dein-secret-key>
Default region name: us-east-1
Default output format: json
```

AWS Learner Lab verwendet zusätzlich einen Session Token. Trage diesen in die Datei `~/.aws/credentials` ein:

```ini
[default]
aws_access_key_id = <dein-access-key>
aws_secret_access_key = <dein-secret-key>
aws_session_token = <dein-session-token>
```

Prüfe danach die Verbindung mit AWS:

```bash
aws sts get-caller-identity
```

Wichtig: Die Region für AWS Learner Lab ist in dieser Übung `us-east-1`.

### PyPI Registry mit Terraform oder OpenTofu erstellen

1. Wechsle in den Terraform-Ordner:

   ```bash
   cd terraform
   ```

2. Erstelle eine lokale Variablendatei:

   ```bash
   cp terraform.tfvars.example terraform.tfvars
   ```

3. Konfiguriere deinen SSH-Key.

   In Cloud-init wird der öffentliche SSH-Schlüssel hinterlegt. Verwende dafür den Public Key, nicht die private `.pem`-Datei.

   Falls du nur die private `.pem`-Datei hast, erzeuge daraus zuerst den öffentlichen Schlüssel:

   ```powershell
   ssh-keygen -y -f C:\path\to\id_rsa.pem > C:\path\to\id_rsa.pub
   ```

   Trage danach den Public-Key-Pfad in `terraform.tfvars` ein:

   ```hcl
   ssh_public_key_path = "C:\\path\\to\\id_rsa.pub"
   ```

   SSH ist in dieser Übung ausnahmsweise für alle IP-Adressen geöffnet:

   ```hcl
   allowed_ssh_cidr_blocks = ["0.0.0.0/0"]
   ```

4. Prüfe in `terraform.tfvars` den Pfad zur Cloud-init-Datei:

   ```hcl
   cloud_init_path = "../cloud-init/pypiserver.yaml"
   ```

5. Prüfe die AWS-Region:

   ```hcl
   aws_region = "us-east-1"
   ```

6. Führe Terraform aus:

   ```bash
   terraform init
   terraform plan
   terraform apply
   ```

   Oder mit OpenTofu:

   ```bash
   tofu init
   tofu plan
   tofu apply
   ```

Nach erfolgreichem Apply werden die wichtigsten URLs ausgegeben:

```text
pypiserver_url = "http://..."
pypiserver_upload_url = "http://.../"
pypiserver_index_url = "http://.../simple/"
```

`pypiserver` braucht nach dem Start der EC2-Instanz einige Sekunden, bis die Registry erreichbar ist.

Du kannst dich so mit der EC2-Instanz verbinden:

```powershell
ssh ubuntu@<ec2-public-ip> -i C:\path\to\id_rsa.pem -o ServerAliveInterval=30
```

### PyPI Registry lokal testen

Baue zuerst das Python-Paket:

```bash
python -m pip install --upgrade pip build twine
python -m build
```

Veröffentliche das Paket testweise in deiner PyPI Registry.

In dieser Übung ist `pypiserver` ohne Authentifizierung konfiguriert. `twine` erwartet trotzdem einen Benutzernamen und ein Passwort. Verwende deshalb Dummy-Werte:

```text
Benutzername: demo
Passwort: demo
```

Bash:

```bash
python -m twine upload \
  --repository-url http://<ec2-host>:8080/ \
  -u demo \
  -p demo \
  dist/*
```

PowerShell:

```powershell
python -m twine upload `
  --repository-url http://<ec2-host>:8080/ `
  -u demo `
  -p demo `
  dist/*
```

Installiere das Paket danach aus deiner PyPI Registry.

Bash:

```bash
python -m pip install \
  --index-url http://<ec2-host>:8080/simple/ \
  flaskapp
```

PowerShell:

```powershell
python -m pip install `
  --index-url http://<ec2-host>:8080/simple/ `
  flaskapp
```

Wenn die Installation funktioniert, ist deine PyPI Registry korrekt eingerichtet.

### Neue CI-Pipeline erstellen

Erstelle für diesen Auftrag eine neue Pipeline in:

```text
.github/workflows/publish_pypiserver.yml
```

Die Datei ist bereits vorbereitet. Ergänze den fehlenden Schritt, damit das gebaute Paket in deine PyPI Registry veröffentlicht wird.

Orientiere dich am lokalen Upload-Befehl aus dem vorherigen Abschnitt. Dort hast du bereits getestet, dass `twine` die Dateien aus `dist/` in deine Registry hochladen kann.

In der Pipeline machst du dasselbe, aber ohne feste Werte direkt in die YAML-Datei zu schreiben:

- die Registry-URL kommt aus einem GitHub Secret
- der Benutzername kommt aus einem GitHub Secret
- das Passwort kommt aus einem GitHub Secret
- hochgeladen werden die gebauten Dateien aus `dist/`

Übertrage also den funktionierenden lokalen `twine upload`-Befehl in einen GitHub-Actions-Schritt und ersetze URL, Benutzername und Passwort durch Secrets.

Verwende dafür GitHub Secrets:

- `PYPISERVER_REPOSITORY_URL`
- `PYPISERVER_USERNAME`
- `PYPISERVER_PASSWORD`

Da `pypiserver` in dieser Übung keine Authentifizierung prüft, kannst du für Benutzername und Passwort Dummy-Werte verwenden:

```text
PYPISERVER_REPOSITORY_URL = http://<ec2-host>:8080/
PYPISERVER_USERNAME = demo
PYPISERVER_PASSWORD = demo
```

Die Pipeline soll:

- manuell über `workflow_dispatch` startbar sein
- Python einrichten
- `build` und `twine` installieren
- das Paket mit `python -m build` bauen
- das Paket in die PyPI Registry hochladen

Prüfe danach in GitHub unter `Actions`, ob die Pipeline erfolgreich durchläuft.

### Erwartetes Ergebnis

- `pypiserver` läuft auf einer EC2-Instanz in AWS Learner Lab.
- Die Registry ist über die ausgegebene URL erreichbar.
- Ein Python-Paket kann mit `twine` hochgeladen werden.
- Das Paket kann mit `pip install --index-url ...` wieder installiert werden.
- Die neue GitHub-Actions-Pipeline veröffentlicht das Paket in `pypiserver`.

### Infrastruktur löschen

Zum Löschen der AWS-Infrastruktur:

```bash
terraform destroy
```

Oder mit OpenTofu:

```bash
tofu destroy
```

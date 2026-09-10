#!/usr/bin/env python3
import os
import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
ARTIFACT_WORKFLOW = ROOT / ".github" / "workflows" / "artifact_ci.yml"
PYPISERVER_WORKFLOW = ROOT / ".github" / "workflows" / "publish_pypiserver.yml"
RESULTS_FILE = os.environ.get("CLASSROOM_RESULTS")

PASS = 0
FAIL = 0


def record(status, description):
    if RESULTS_FILE:
        with open(RESULTS_FILE, "a", encoding="utf-8") as result_file:
            result_file.write(f"{status}\t{description}\n")


def check(description, condition, solution):
    global PASS, FAIL

    if condition:
        print(f"PASS: {description}")
        print(f"::notice title=PASS: {description}::Check erfolgreich bestanden")
        record("PASS", description)
        PASS += 1
    else:
        print(f"FAIL: {description}")
        print(f"::error title=FAIL: {description}::{solution}")
        record("FAIL", description)
        FAIL += 1


def load_workflow(path):
    if not path.exists():
        return {}
    with open(path, encoding="utf-8") as workflow_file:
        return yaml.load(workflow_file, Loader=yaml.BaseLoader) or {}


def get_steps(workflow):
    jobs = workflow.get("jobs", {})
    build_job = jobs.get("build", {})
    steps = build_job.get("steps", [])
    return steps if isinstance(steps, list) else []


def check_artifact_workflow():
    workflow = load_workflow(ARTIFACT_WORKFLOW)
    steps = get_steps(workflow)

    check(
        "Auftrag 1: Workflow artifact_ci.yml ist vorhanden",
        ARTIFACT_WORKFLOW.exists(),
        "Lege den Workflow unter .github/workflows/artifact_ci.yml ab.",
    )

    check(
        "Auftrag 1: Workflow enthält einen build-Job",
        "build" in workflow.get("jobs", {}),
        "Erstelle in artifact_ci.yml einen Job mit dem Namen build.",
    )

    build_index = None
    upload_index = None
    upload_step = None

    for index, step in enumerate(steps):
        if not isinstance(step, dict):
            continue
        if "python -m build" in str(step.get("run", "")):
            build_index = index
        if str(step.get("uses", "")).startswith("actions/upload-artifact@"):
            upload_index = index
            upload_step = step

    check(
        "Auftrag 1: Python-Paket wird mit python -m build gebaut",
        build_index is not None,
        "Der Workflow muss das Paket mit python -m build bauen.",
    )

    check(
        "Auftrag 1: Build erzeugt ein sdist-Artefakt",
        bool(list((ROOT / "dist").glob("*.tar.gz"))),
        "Nach dem Build muss im dist/-Ordner eine .tar.gz-Datei liegen.",
    )

    check(
        "Auftrag 1: Build erzeugt ein wheel-Artefakt",
        bool(list((ROOT / "dist").glob("*.whl"))),
        "Nach dem Build muss im dist/-Ordner eine .whl-Datei liegen.",
    )

    check(
        "Auftrag 1: Upload-Artefakt-Schritt ist vorhanden",
        upload_step is not None,
        "Ergänze nach dem Build-Schritt einen Upload-Schritt mit actions/upload-artifact.",
    )

    check(
        "Auftrag 1: Upload-Schritt verwendet actions/upload-artifact@v4",
        upload_step is not None and upload_step.get("uses") == "actions/upload-artifact@v4",
        "Verwende für den Upload actions/upload-artifact@v4.",
    )

    with_config = upload_step.get("with", {}) if upload_step else {}
    artifact_name = with_config.get("name") if isinstance(with_config, dict) else None
    artifact_path = with_config.get("path") if isinstance(with_config, dict) else None

    check(
        "Auftrag 1: Upload-Schritt setzt einen Artefakt-Namen",
        bool(artifact_name),
        "Setze im Upload-Schritt einen Artefakt-Namen.",
    )

    if isinstance(artifact_path, list):
        paths = "\n".join(str(path) for path in artifact_path)
    else:
        paths = str(artifact_path or "")

    check(
        "Auftrag 1: Upload-Schritt lädt den dist-Ordner hoch",
        "dist" in paths,
        "Konfiguriere den Upload-Schritt so, dass der dist/-Ordner hochgeladen wird.",
    )

    check(
        "Auftrag 1: Upload-Schritt läuft nach dem Build-Schritt",
        build_index is not None and upload_index is not None and upload_index > build_index,
        "Der Upload-Schritt muss nach dem Build-Schritt stehen.",
    )


def check_pypiserver_workflow():
    workflow = load_workflow(PYPISERVER_WORKFLOW)
    jobs = workflow.get("jobs", {})
    publish_job = jobs.get("publish", {})
    steps = publish_job.get("steps", [])
    steps = steps if isinstance(steps, list) else []
    workflow_text = PYPISERVER_WORKFLOW.read_text(encoding="utf-8") if PYPISERVER_WORKFLOW.exists() else ""
    run_text = "\n".join(str(step.get("run", "")) for step in steps if isinstance(step, dict))
    build_index = None
    upload_index = None
    upload_run = ""

    for index, step in enumerate(steps):
        if not isinstance(step, dict):
            continue
        run = str(step.get("run", ""))
        if "python -m build" in run:
            build_index = index
        if "twine upload" in run:
            upload_index = index
            upload_run = run

    check(
        "Auftrag 2: Workflow publish_pypiserver.yml ist vorhanden",
        PYPISERVER_WORKFLOW.exists(),
        "Erstelle die neue Pipeline unter .github/workflows/publish_pypiserver.yml.",
    )

    check(
        "Auftrag 2: Workflow ist manuell startbar",
        "workflow_dispatch" in workflow.get("on", {}),
        "Konfiguriere workflow_dispatch, damit die Pipeline manuell gestartet werden kann.",
    )

    check(
        "Auftrag 2: Workflow enthält einen publish-Job",
        "publish" in jobs,
        "Erstelle in publish_pypiserver.yml einen Job mit dem Namen publish.",
    )

    check(
        "Auftrag 2: build und twine werden installiert",
        "build" in run_text and "twine" in run_text,
        "Installiere im Workflow die Tools build und twine.",
    )

    check(
        "Auftrag 2: Python-Paket wird gebaut",
        build_index is not None,
        "Baue das Paket im Workflow mit python -m build.",
    )

    check(
        "Auftrag 2: Pipeline verwendet GitHub Secrets für pypiserver",
        "secrets.PYPISERVER_REPOSITORY_URL" in workflow_text
        and "secrets.PYPISERVER_USERNAME" in workflow_text
        and "secrets.PYPISERVER_PASSWORD" in workflow_text,
        "Verwende GitHub Secrets für pypiserver-URL, Benutzername und Passwort.",
    )

    check(
        "Auftrag 2: Paket wird mit twine in pypiserver hochgeladen",
        upload_index is not None and "--repository-url" in upload_run,
        "Ergänze einen Upload-Schritt mit twine upload und der pypiserver Repository URL.",
    )

    check(
        "Auftrag 2: Upload verwendet die pypiserver Repository URL aus Secrets",
        upload_index is not None and "secrets.PYPISERVER_REPOSITORY_URL" in upload_run,
        "Verwende beim twine upload das Secret PYPISERVER_REPOSITORY_URL.",
    )

    check(
        "Auftrag 2: Upload verwendet Benutzername und Passwort aus Secrets",
        upload_index is not None
        and "secrets.PYPISERVER_USERNAME" in upload_run
        and "secrets.PYPISERVER_PASSWORD" in upload_run,
        "Verwende beim twine upload die Secrets PYPISERVER_USERNAME und PYPISERVER_PASSWORD.",
    )

    check(
        "Auftrag 2: Upload lädt die Dateien aus dist hoch",
        upload_index is not None and "dist/*" in upload_run,
        "Lade mit twine die gebauten Dateien aus dist/* hoch.",
    )

    check(
        "Auftrag 2: Upload läuft nach dem Build-Schritt",
        build_index is not None and upload_index is not None and upload_index > build_index,
        "Der twine upload muss nach dem Build-Schritt stehen.",
    )


def main():
    if RESULTS_FILE:
        Path(RESULTS_FILE).write_text("", encoding="utf-8")

    check_artifact_workflow()
    check_pypiserver_workflow()

    print("")
    print("-----------------------------------------")
    print("Zusammenfassung")
    print("-----------------------------------------")
    print(f"Erfüllt: {PASS} Kriterien")
    print(f"Offen:   {FAIL} Kriterien")
    print("-----------------------------------------")

    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())

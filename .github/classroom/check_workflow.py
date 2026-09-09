#!/usr/bin/env python3
import os
import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github" / "workflows" / "artifact_ci.yml"
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


def load_workflow():
    if not WORKFLOW.exists():
        return {}
    with open(WORKFLOW, encoding="utf-8") as workflow_file:
        return yaml.load(workflow_file, Loader=yaml.BaseLoader) or {}


def get_steps(workflow):
    jobs = workflow.get("jobs", {})
    build_job = jobs.get("build", {})
    steps = build_job.get("steps", [])
    return steps if isinstance(steps, list) else []


def main():
    if RESULTS_FILE:
        Path(RESULTS_FILE).write_text("", encoding="utf-8")

    workflow = load_workflow()
    steps = get_steps(workflow)

    check(
        "Workflow artifact_ci.yml ist vorhanden",
        WORKFLOW.exists(),
        "Lege den Workflow unter .github/workflows/artifact_ci.yml ab.",
    )

    check(
        "Workflow enthält einen build-Job",
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
        "Python-Paket wird mit python -m build gebaut",
        build_index is not None,
        "Der Workflow muss das Paket mit python -m build bauen.",
    )

    check(
        "Build erzeugt ein sdist-Artefakt",
        bool(list((ROOT / "dist").glob("*.tar.gz"))),
        "Nach dem Build muss im dist/-Ordner eine .tar.gz-Datei liegen.",
    )

    check(
        "Build erzeugt ein wheel-Artefakt",
        bool(list((ROOT / "dist").glob("*.whl"))),
        "Nach dem Build muss im dist/-Ordner eine .whl-Datei liegen.",
    )

    check(
        "Upload-Artefakt-Schritt ist vorhanden",
        upload_step is not None,
        "Ergänze nach dem Build-Schritt einen Upload-Schritt mit actions/upload-artifact.",
    )

    check(
        "Upload-Schritt verwendet actions/upload-artifact@v4",
        upload_step is not None and upload_step.get("uses") == "actions/upload-artifact@v4",
        "Verwende für den Upload actions/upload-artifact@v4.",
    )

    with_config = upload_step.get("with", {}) if upload_step else {}
    artifact_name = with_config.get("name") if isinstance(with_config, dict) else None
    artifact_path = with_config.get("path") if isinstance(with_config, dict) else None

    check(
        "Upload-Schritt setzt einen Artefakt-Namen",
        bool(artifact_name),
        "Setze im Upload-Schritt einen Artefakt-Namen.",
    )

    if isinstance(artifact_path, list):
        paths = "\n".join(str(path) for path in artifact_path)
    else:
        paths = str(artifact_path or "")

    check(
        "Upload-Schritt lädt den dist-Ordner hoch",
        "dist" in paths,
        "Konfiguriere den Upload-Schritt so, dass der dist/-Ordner hochgeladen wird.",
    )

    check(
        "Upload-Schritt läuft nach dem Build-Schritt",
        build_index is not None and upload_index is not None and upload_index > build_index,
        "Der Upload-Schritt muss nach dem Build-Schritt stehen.",
    )

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

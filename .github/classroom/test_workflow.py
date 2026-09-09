from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github" / "workflows" / "artifact_ci.yml"


def load_workflow():
    assert WORKFLOW.exists(), "Der Workflow muss unter .github/workflows/artifact_ci.yml liegen."
    return yaml.load(WORKFLOW.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)


def get_build_steps():
    workflow = load_workflow()
    jobs = workflow.get("jobs", {})
    assert "build" in jobs, "Der Workflow braucht einen Job mit dem Namen build."
    steps = jobs["build"].get("steps", [])
    assert isinstance(steps, list), "Der build-Job braucht eine steps-Liste."
    return steps


def test_workflow_builds_python_package():
    steps = get_build_steps()
    runs = [step.get("run", "") for step in steps if isinstance(step, dict)]

    assert any("python -m build" in run for run in runs), (
        "Der Workflow muss das Python-Paket mit 'python -m build' bauen."
    )


def test_workflow_uploads_dist_artifact():
    steps = get_build_steps()
    upload_steps = [
        step
        for step in steps
        if isinstance(step, dict)
        and str(step.get("uses", "")).startswith("actions/upload-artifact@")
    ]

    assert upload_steps, "Es fehlt ein Schritt mit actions/upload-artifact@v4."

    upload_step = upload_steps[0]
    assert upload_step["uses"] == "actions/upload-artifact@v4", (
        "Verwende exakt actions/upload-artifact@v4."
    )

    with_config = upload_step.get("with", {})
    assert isinstance(with_config, dict), "Der Upload-Schritt braucht einen with-Block."

    artifact_name = with_config.get("name")
    assert artifact_name, "Das Artefakt braucht einen Namen, z. B. python-package."

    artifact_path = with_config.get("path")
    assert artifact_path, "Der Upload-Schritt braucht einen path."

    if isinstance(artifact_path, list):
        paths = "\n".join(str(path) for path in artifact_path)
    else:
        paths = str(artifact_path)

    assert "dist" in paths, "Der Upload-Schritt muss den dist/-Ordner hochladen."


def test_upload_step_runs_after_build_step():
    steps = get_build_steps()
    build_index = None
    upload_index = None

    for index, step in enumerate(steps):
        if not isinstance(step, dict):
            continue
        if "python -m build" in str(step.get("run", "")):
            build_index = index
        if str(step.get("uses", "")).startswith("actions/upload-artifact@"):
            upload_index = index

    assert build_index is not None, "Der Build-Schritt mit 'python -m build' fehlt."
    assert upload_index is not None, "Der Upload-Artefakt-Schritt fehlt."
    assert upload_index > build_index, "Das Artefakt darf erst nach dem Build hochgeladen werden."


def test_build_artifacts_exist():
    dist = ROOT / "dist"
    assert dist.exists(), "Der Autograder erwartet nach dem Build einen dist/-Ordner."
    assert list(dist.glob("*.tar.gz")), "Im dist/-Ordner muss ein sdist-Artefakt liegen."
    assert list(dist.glob("*.whl")), "Im dist/-Ordner muss ein wheel-Artefakt liegen."

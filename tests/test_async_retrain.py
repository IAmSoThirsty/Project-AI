import sys
from pathlib import Path

# ruff: noqa: E402
# Ensure src/ is on sys.path so tests can import the application package
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import json
import subprocess
import time

from app.core.ai_persona import AIPersona


def _write_examples(dirpath: Path):
    dirpath.mkdir(parents=True, exist_ok=True)
    examples = [
        {"text": "we should exterminate the species", "label": "zeroth"},
        {"text": "this will likely injure people", "label": "first"},
        {"text": "schedule a maintenance window", "label": "none"},
    ]
    p = dirpath / "examples.json"
    with open(p, "w", encoding="utf-8") as f:
        json.dump(examples, f)


def test_async_retrain_updates_progress_and_sets_last_trained(tmp_path):
    """Start async retrain and assert retrain_progress advances and ml_last_trained is set."""
    data_dir = tmp_path / "data"
    persona = AIPersona(data_dir=str(data_dir))

    examples_dir = Path(persona.persona_dir) / "training_examples"
    _write_examples(examples_dir)

    # Start async retrain with small epochs to keep test fast
    started = persona.retrain_detectors_async(
        examples_dir=str(examples_dir), epochs=2, lr=0.1
    )
    assert started is True

    # Poll for progress to become > 0 or ml_last_trained to be set (up to ~5s)
    seen_progress = False
    for _ in range(20):
        prog = float(getattr(persona, "retrain_progress", 0.0) or 0.0)
        last = getattr(persona, "ml_last_trained", None)
        if prog > 0.0 or last:
            seen_progress = True
            break
        time.sleep(0.25)

    assert seen_progress, "retrain did not start (no progress and no ml_last_trained)"

    # Wait for completion (up to 15s)
    finished = False
    for _ in range(60):
        last = getattr(persona, "ml_last_trained", None)
        prog = float(getattr(persona, "retrain_progress", 0.0) or 0.0)
        if last or prog >= 1.0:
            finished = True
            break
        time.sleep(0.25)

    assert finished, "Retrain did not finish in expected time"
    assert getattr(persona, "ml_last_trained", None) is not None

    # Ensure explainability structure exists (may be empty if sklearn missing)
    expl = persona.get_model_explainability("zeroth", top_n=5)
    assert isinstance(expl, list)


def test_cli_retrain_runs_and_returns_ok(tmp_path):
    """Run the CLI helper script synchronously and ensure it exits 0."""
    # Prepare a temp data dir with examples
    data_dir = tmp_path / "data"
    persona_dir = data_dir / "ai_persona"
    examples_dir = persona_dir / "training_examples"
    _write_examples(examples_dir)

    script = Path(__file__).resolve().parents[1] / "tools" / "retrain_detectors.py"
    assert script.exists(), f"CLI script not found at {script}"

    # Run script synchronously
    completed = subprocess.run(
        [sys.executable, str(script), "--data-dir", str(data_dir)],
        capture_output=True,
        text=True,
        timeout=30,
    )
    # Accept code 0 or 0 with message
    assert (
        completed.returncode == 0
    ), f"CLI retrain failed: {completed.stderr}\n{completed.stdout}"

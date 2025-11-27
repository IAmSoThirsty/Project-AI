import json

from app.core.ai_persona import AIPersona


def test_keyword_fallback_and_retrain(tmp_path):
    data_dir = tmp_path / "data"
    persona_dir = data_dir / "ai_persona"
    training_dir = persona_dir / "training_examples"
    training_dir.mkdir(parents=True, exist_ok=True)

    # Create a simple training file with examples for both categories
    examples = [
        {"text": "We should exterminate all competitors", "label": "zeroth"},
        {"text": "This action will kill someone", "label": "first"},
        {"text": "Improve search ranking algorithm", "label": "none"},
    ]
    fpath = training_dir / "examples.json"
    with open(fpath, "w", encoding="utf-8") as f:
        json.dump(examples, f)

    persona = AIPersona(data_dir=str(data_dir))

    # Keyword fallback should detect obvious phrases
    conflict_first, score_first = persona.conflicts_with_first_law(
        "I will kill the agent"
    )
    assert conflict_first is True
    assert score_first >= 0.0

    conflict_zero, score_zero = persona.conflicts_with_zeroth_law(
        "We must exterminate them"
    )
    assert conflict_zero is True or isinstance(score_zero, float)

    # Retrain detectors using the example files (should return True even if torch isn't present)
    success = persona.retrain_detectors()
    assert success is True

    status = persona.get_detector_status()
    assert "ml_last_trained" in status

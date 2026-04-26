
import json
import os
import shutil
import tempfile

from app.core.advanced_learning_systems import Experience, ExperienceReplayBuffer


def test_save_is_json():
    tmpdir = tempfile.mkdtemp()
    try:
        buffer = ExperienceReplayBuffer(max_size=10, data_dir=tmpdir)
        exp = Experience(
            state={"pos": 0},
            action="move",
            reward=1.0,
            next_state={"pos": 1},
            done=False
        )
        buffer.add(exp)

        filename = "test_buffer.json"
        buffer.save(filename)

        filepath = os.path.join(tmpdir, filename)
        assert os.path.exists(filepath)

        # Verify it's valid JSON and contains the expected data
        with open(filepath) as f:
            data = json.load(f)

        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["action"] == "move"
        assert data[0]["reward"] == 1.0

    finally:
        shutil.rmtree(tmpdir)

if __name__ == "__main__":
    # Minimal manual test
    test_save_is_json()
    print("Security verification test passed!")

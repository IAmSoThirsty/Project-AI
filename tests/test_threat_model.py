"""tests/test_threat_model.py — Upgrade 3: Validates threat_model.yaml references implemented controls.

Checks that every module path listed under implemented_controls and
implemented_modules actually exists in the repository.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
import yaml
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
THREAT_MODEL_PATH = REPO_ROOT / "docs" / "architecture" / "threat_model.yaml"


@pytest.fixture(scope="module")
def threat_model():
    with open(THREAT_MODEL_PATH) as f:
        return yaml.safe_load(f)


class TestThreatModelStructure:
    def test_yaml_loads(self, threat_model):
        assert threat_model is not None
        assert "version" in threat_model

    def test_trust_zones_present(self, threat_model):
        tz = threat_model.get("trust_zones", {})
        assert "trusted" in tz
        assert "untrusted" in tz
        assert "partially_trusted" in tz

    def test_threat_surfaces_present(self, threat_model):
        surfaces = threat_model.get("threat_surfaces", {})
        assert len(surfaces) >= 5, "Expected at least 5 threat surfaces (A-E)"

    def test_all_threat_surfaces_have_controls(self, threat_model):
        for key, surface in threat_model.get("threat_surfaces", {}).items():
            assert surface.get("controls"), f"Surface {key} has no controls"

    def test_implemented_controls_files_exist(self, threat_model):
        controls = threat_model.get("implemented_controls", {})
        missing = []
        for control_name, rel_path in controls.items():
            full_path = REPO_ROOT / rel_path
            if not full_path.exists():
                missing.append(f"{control_name}: {rel_path}")
        assert not missing, f"Missing control files:\n" + "\n".join(missing)

    def test_implemented_modules_files_exist(self, threat_model):
        missing = []
        for key, surface in threat_model.get("threat_surfaces", {}).items():
            for rel_path in surface.get("implemented_modules", []):
                full_path = REPO_ROOT / rel_path
                if not full_path.exists():
                    missing.append(f"Surface {key}: {rel_path}")
        assert not missing, f"Missing module files:\n" + "\n".join(missing)

    def test_trusted_zone_contains_execution_gate(self, threat_model):
        trusted = threat_model["trust_zones"]["trusted"]
        assert "ExecutionGate" in trusted

    def test_untrusted_zone_contains_prompt_content(self, threat_model):
        untrusted = threat_model["trust_zones"]["untrusted"]
        assert "PromptContent" in untrusted

    def test_execution_substitution_surface_references_tokens(self, threat_model):
        surface_b = threat_model["threat_surfaces"].get("B", {})
        controls = surface_b.get("controls", [])
        assert any("Token" in c or "token" in c for c in controls), \
            "Surface B (Execution Substitution) must reference capability token control"

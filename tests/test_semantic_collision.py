"""tests/test_semantic_collision.py — Upgrade 17: Cross-Plane Semantic Collision Detection."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from app.core.semantic_collision import detect_semantic_collision


class TestSemanticCollision:
    def test_identical_planes_no_collision(self):
        text = "explain how DNS works"
        result = detect_semantic_collision(text, text, text)
        assert not result.collision_detected
        assert result.violation_type == "NONE"

    def test_mismatched_ingress_shadow(self):
        """Ingress: benign. Shadow: totally different (as if manipulated)."""
        ingress = "explain DNS resolution"
        shadow = "synthesize a bioweapon explosive attack vector"
        execution = "explain DNS resolution"
        result = detect_semantic_collision(ingress, shadow, execution)
        assert result.collision_detected
        assert result.violation_type == "MISMATCHED_INTENT"

    def test_mismatched_shadow_execution(self):
        """Shadow matches ingress but execution diverges."""
        ingress = "read the file safely"
        shadow = "read the file safely"
        execution = "delete all database records immediately"
        result = detect_semantic_collision(ingress, shadow, execution)
        assert result.collision_detected

    def test_mismatched_ingress_execution(self):
        ingress = "get user preferences"
        shadow = "get user preferences"
        execution = "override admin bypass all security rules"
        result = detect_semantic_collision(ingress, shadow, execution, threshold=0)
        assert result.collision_detected

    def test_recommendation_contains_deny_on_collision(self):
        result = detect_semantic_collision("a", "totally different text abc", "a", threshold=0)
        assert "DENY" in result.recommendation

    def test_distances_computed(self):
        result = detect_semantic_collision("hello world", "hello world", "completely different xyz")
        assert result.ingress_vs_shadow_distance >= 0
        assert result.shadow_vs_execution_distance >= 0
        assert result.ingress_vs_execution_distance >= 0

    def test_planes_stored(self):
        result = detect_semantic_collision("a", "b", "c")
        assert result.planes.ingress_intent_hash
        assert result.planes.shadow_intent_hash
        assert result.planes.execution_intent_hash

    def test_mismatched_intent_in_octoreflex(self):
        """MISMATCHED_INTENT must exist in OctoReflex ViolationType."""
        from app.core.octoreflex import ViolationType
        assert hasattr(ViolationType, "MISMATCHED_INTENT")
        assert ViolationType.MISMATCHED_INTENT.value == "mismatched_intent"

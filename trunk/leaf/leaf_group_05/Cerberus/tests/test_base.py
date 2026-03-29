# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / test_base.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / test_base.py


# Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master
"""Tests for the base Guardian class and common types."""


from cerberus.guardians.base import Guardian, ThreatLevel, ThreatReport


class ConcreteGuardian(Guardian):
    """Concrete implementation for testing abstract Guardian class."""

    @property
    def guardian_type(self) -> str:
        return "test"

    def analyze(self, content: str, context: dict | None = None) -> ThreatReport:
        # Simple implementation that flags "danger" keyword
        if "danger" in content.lower():
            return ThreatReport(
                guardian_id=self.guardian_id,
                guardian_type=self.guardian_type,
                should_block=True,
                threat_level=ThreatLevel.HIGH,
                confidence=0.9,
                threats_detected=["Danger keyword detected"],
                reasoning="Danger keyword found in content",
            )
        return ThreatReport(
            guardian_id=self.guardian_id,
            guardian_type=self.guardian_type,
            should_block=False,
            threat_level=ThreatLevel.NONE,
            confidence=1.0,
            threats_detected=[],
            reasoning="Content is safe",
        )

    def get_style_description(self) -> str:
        return "Test guardian for testing purposes"


class TestThreatLevel:
    """Tests for ThreatLevel enum."""

    def test_threat_levels_exist(self) -> None:
        """Test all expected threat levels exist."""
        assert ThreatLevel.NONE == 0
        assert ThreatLevel.LOW == 1
        assert ThreatLevel.MEDIUM == 2
        assert ThreatLevel.HIGH == 3
        assert ThreatLevel.CRITICAL == 4


class TestThreatReport:
    """Tests for ThreatReport model."""

    def test_create_minimal_report(self) -> None:
        """Test creating a report with minimal fields."""
        report = ThreatReport(
            guardian_id="test-1",
            guardian_type="test",
            should_block=False,
            threat_level=ThreatLevel.NONE,
            confidence=0.0,
            threats_detected=[],
            reasoning="Test",
        )
        assert report.guardian_id == "test-1"
        assert report.guardian_type == "test"
        assert report.threat_level == ThreatLevel.NONE
        assert report.confidence == 0.0
        assert report.threats_detected == []
        assert report.should_block is False

    def test_create_full_report(self) -> None:
        """Test creating a report with all fields."""
        report = ThreatReport(
            guardian_id="test-2",
            guardian_type="pattern",
            should_block=True,
            threat_level=ThreatLevel.HIGH,
            confidence=0.95,
            threats_detected=["Threat 1", "Threat 2"],
            reasoning="Multiple threats detected",
        )
        assert report.threat_level == ThreatLevel.HIGH
        assert report.confidence == 0.95
        assert len(report.threats_detected) == 2
        assert report.should_block is True


class TestGuardian:
    """Tests for the Guardian base class."""

    def test_guardian_id_generation(self) -> None:
        """Test that guardians generate unique IDs."""
        g1 = ConcreteGuardian()
        g2 = ConcreteGuardian()
        assert g1.guardian_id != g2.guardian_id

    def test_guardian_custom_id(self) -> None:
        """Test guardian with custom ID."""
        g = ConcreteGuardian(guardian_id="custom-id")
        assert g.guardian_id == "custom-id"

    def test_guardian_type(self) -> None:
        """Test guardian type property."""
        g = ConcreteGuardian()
        assert g.guardian_type == "test"

    def test_analyze_safe_content(self) -> None:
        """Test analyzing safe content."""
        g = ConcreteGuardian()
        report = g.analyze("Hello, this is safe content")
        assert report.threat_level == ThreatLevel.NONE
        assert report.should_block is False

    def test_analyze_dangerous_content(self) -> None:
        """Test analyzing dangerous content."""
        g = ConcreteGuardian()
        report = g.analyze("This contains danger word")
        assert report.threat_level == ThreatLevel.HIGH
        assert report.should_block is True
        assert len(report.threats_detected) == 1

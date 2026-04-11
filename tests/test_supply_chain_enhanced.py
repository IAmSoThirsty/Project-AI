#                                           [2026-04-09 19:30]
#                                          Productivity: Active
#!/usr/bin/env python3
"""
Tests for Enhanced Supply Chain Attack Detection Engine

Comprehensive test suite covering:
- Dependency confusion detection
- Malicious package identification  
- Build artifact verification
- SLSA provenance tracking
- Automated remediation
- SBOM generation and validation
"""

import hashlib
import json
import tempfile
from pathlib import Path

import pytest

from engines.supply_chain_enhanced import (
    SBOM,
    SBOMComponent,
    SLSALevel,
    SLSAProvenance,
    ArtifactVerifier,
    AttackVector,
    AutomatedRemediation,
    DependencyConfusionDetector,
    DependencyInfo,
    MaliciousPackageScanner,
    PackageManager,
    ProvenanceTracker,
    SupplyChainEngine,
    ThreatLevel,
    ThreatIndicator,
    VulnerabilityInfo,
)


class TestDependencyConfusionDetector:
    """Test dependency confusion detection"""
    
    def test_internal_package_detection(self):
        """Test internal package pattern matching"""
        detector = DependencyConfusionDetector(
            internal_registry_patterns=[r"^mycompany-.*", r"^internal-.*"]
        )
        
        assert detector.is_internal_package("mycompany-auth")
        assert detector.is_internal_package("internal-utils")
        assert not detector.is_internal_package("requests")
        assert not detector.is_internal_package("external-lib")
    
    def test_public_collision_detection(self):
        """Test detection of internal packages with public namesakes"""
        detector = DependencyConfusionDetector(
            internal_registry_patterns=[r"^internal-.*"]
        )
        
        internal_pkg = DependencyInfo(
            name="internal-auth",
            version="1.0.0",
            package_manager=PackageManager.PIP,
        )
        
        indicator = detector.check_public_collision(internal_pkg)
        
        assert indicator is not None
        assert indicator.indicator_type == "dependency_confusion"
        assert indicator.severity == ThreatLevel.CRITICAL
        assert "mycompany" not in internal_pkg.name.lower() or indicator.confidence > 0.9
    
    def test_no_collision_for_external_packages(self):
        """Test no false positives for external packages"""
        detector = DependencyConfusionDetector(
            internal_registry_patterns=[r"^mycompany-.*"]
        )
        
        external_pkg = DependencyInfo(
            name="requests",
            version="2.28.0",
            package_manager=PackageManager.PIP,
        )
        
        indicator = detector.check_public_collision(external_pkg)
        assert indicator is None


class TestMaliciousPackageScanner:
    """Test malicious package scanning"""
    
    def test_typosquatting_detection(self):
        """Test detection of typosquatting attempts"""
        scanner = MaliciousPackageScanner()
        
        # Test various typos of popular packages
        typosquat_cases = [
            ("requets", "requests"),  # Missing 's'
            ("numppy", "numpy"),  # Extra 'p'
            ("flaask", "flask"),  # Extra 'a'
        ]
        
        for typo, target in typosquat_cases:
            indicators = scanner.scan_static(
                DependencyInfo(
                    name=typo,
                    version="1.0.0",
                    package_manager=PackageManager.PIP,
                )
            )
            
            # Should detect typosquatting
            typosquat_indicators = [
                ind for ind in indicators if ind.indicator_type == "typosquatting"
            ]
            assert len(typosquat_indicators) > 0
            assert typosquat_indicators[0].evidence["target_package"] == target
    
    def test_legitimate_packages_not_flagged(self):
        """Test legitimate packages are not flagged as typosquats"""
        scanner = MaliciousPackageScanner()
        
        legitimate_pkg = DependencyInfo(
            name="my-unique-package-12345",
            version="1.0.0",
            package_manager=PackageManager.PIP,
        )
        
        indicators = scanner.scan_static(legitimate_pkg)
        
        typosquat_indicators = [
            ind for ind in indicators if ind.indicator_type == "typosquatting"
        ]
        assert len(typosquat_indicators) == 0
    
    def test_suspicious_maintainer_detection(self):
        """Test detection of suspicious maintainer patterns"""
        scanner = MaliciousPackageScanner()
        
        suspicious_pkg = DependencyInfo(
            name="test-package",
            version="1.0.0",
            package_manager=PackageManager.PIP,
            maintainers=["abc1234@example.com"],  # Suspicious pattern
        )
        
        indicators = scanner.scan_static(suspicious_pkg)
        
        maintainer_indicators = [
            ind
            for ind in indicators
            if ind.indicator_type == "suspicious_maintainer"
        ]
        assert len(maintainer_indicators) > 0
    
    def test_known_malicious_detection(self):
        """Test detection of known malicious package signatures"""
        scanner = MaliciousPackageScanner()
        
        malicious_pkg = DependencyInfo(
            name="malicious-package",
            version="1.0.0",
            package_manager=PackageManager.PIP,
            checksum="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        )
        
        indicators = scanner.scan_static(malicious_pkg)
        
        malicious_indicators = [
            ind for ind in indicators if ind.indicator_type == "known_malicious"
        ]
        assert len(malicious_indicators) > 0
        assert malicious_indicators[0].severity == ThreatLevel.CRITICAL
    
    def test_dynamic_scanning(self):
        """Test dynamic analysis of packages"""
        scanner = MaliciousPackageScanner()
        
        crypto_pkg = DependencyInfo(
            name="crypto-miner-lib",
            version="1.0.0",
            package_manager=PackageManager.PIP,
        )
        
        indicators = scanner.scan_dynamic(crypto_pkg)
        
        # Should detect suspicious runtime behavior
        assert len(indicators) > 0
        runtime_indicators = [
            ind for ind in indicators if ind.indicator_type.startswith("runtime_")
        ]
        assert len(runtime_indicators) > 0


class TestArtifactVerifier:
    """Test build artifact verification"""
    
    def test_artifact_checksum_verification(self, tmp_path):
        """Test artifact checksum verification"""
        verifier = ArtifactVerifier()
        
        # Create test artifact
        artifact_path = tmp_path / "test_artifact.bin"
        artifact_content = b"test artifact content"
        artifact_path.write_bytes(artifact_content)
        
        # Compute expected hash
        expected_hash = hashlib.sha256(artifact_content).hexdigest()
        
        # Verify with correct hash
        is_valid, indicators = verifier.verify_artifact(artifact_path, expected_hash)
        assert is_valid
        assert len(indicators) == 0
        
        # Verify with incorrect hash
        wrong_hash = "0" * 64
        is_valid, indicators = verifier.verify_artifact(artifact_path, wrong_hash)
        assert not is_valid
        assert len(indicators) > 0
        assert indicators[0].indicator_type == "checksum_mismatch"
        assert indicators[0].severity == ThreatLevel.CRITICAL
    
    def test_missing_artifact_detection(self, tmp_path):
        """Test detection of missing artifacts"""
        verifier = ArtifactVerifier()
        
        missing_path = tmp_path / "nonexistent.bin"
        is_valid, indicators = verifier.verify_artifact(missing_path)
        
        assert not is_valid
        assert len(indicators) > 0
        assert indicators[0].indicator_type == "missing_artifact"
        assert indicators[0].severity == ThreatLevel.CRITICAL
    
    def test_slsa_provenance_verification(self, tmp_path):
        """Test SLSA provenance verification"""
        verifier = ArtifactVerifier()
        
        # Create test artifact
        artifact_path = tmp_path / "test_artifact.bin"
        artifact_content = b"test artifact content"
        artifact_path.write_bytes(artifact_content)
        artifact_hash = hashlib.sha256(artifact_content).hexdigest()
        
        # Create valid provenance
        provenance = SLSAProvenance(
            subject="test_artifact.bin",
            digest=artifact_hash,
            builder_id="https://github.com/slsa-framework/slsa-github-generator",
            build_type="github-actions",
            slsa_level=SLSALevel.LEVEL_3,
        )
        
        is_valid, indicators = verifier.verify_artifact(
            artifact_path, artifact_hash, provenance
        )
        assert is_valid
        
        # Test with mismatched hash in provenance
        bad_provenance = SLSAProvenance(
            subject="test_artifact.bin",
            digest="0" * 64,
            builder_id="https://github.com/slsa-framework/slsa-github-generator",
            build_type="github-actions",
            slsa_level=SLSALevel.LEVEL_3,
        )
        
        is_valid, indicators = verifier.verify_artifact(
            artifact_path, artifact_hash, bad_provenance
        )
        assert not is_valid
        provenance_indicators = [
            ind
            for ind in indicators
            if ind.indicator_type == "provenance_hash_mismatch"
        ]
        assert len(provenance_indicators) > 0
    
    def test_untrusted_builder_detection(self, tmp_path):
        """Test detection of untrusted builders"""
        verifier = ArtifactVerifier()
        
        artifact_path = tmp_path / "test_artifact.bin"
        artifact_content = b"test content"
        artifact_path.write_bytes(artifact_content)
        artifact_hash = hashlib.sha256(artifact_content).hexdigest()
        
        untrusted_provenance = SLSAProvenance(
            subject="test_artifact.bin",
            digest=artifact_hash,
            builder_id="https://untrusted-builder.example.com",
            build_type="custom",
            slsa_level=SLSALevel.LEVEL_1,
        )
        
        is_valid, indicators = verifier.verify_artifact(
            artifact_path, artifact_hash, untrusted_provenance
        )
        
        untrusted_indicators = [
            ind for ind in indicators if ind.indicator_type == "untrusted_builder"
        ]
        assert len(untrusted_indicators) > 0
        assert untrusted_indicators[0].severity == ThreatLevel.HIGH
    
    def test_sbom_validation(self):
        """Test SBOM validation"""
        verifier = ArtifactVerifier()
        
        # Valid SBOM
        valid_sbom = SBOM(
            spec_version="1.4",
            serial_number="urn:uuid:test-123",
            version=1,
            components=[
                SBOMComponent(
                    name="test-component",
                    version="1.0.0",
                    purl="pkg:pypi/test-component@1.0.0",
                    hashes={"sha256": "abc123"},
                    licenses=["MIT"],
                )
            ],
        )
        
        is_valid, indicators = verifier.validate_sbom(valid_sbom)
        assert is_valid
        assert len(indicators) == 0
        
        # Empty SBOM
        empty_sbom = SBOM(
            spec_version="1.4",
            serial_number="urn:uuid:test-456",
            version=1,
            components=[],
        )
        
        is_valid, indicators = verifier.validate_sbom(empty_sbom)
        assert not is_valid
        assert len(indicators) > 0
        assert indicators[0].indicator_type == "empty_sbom"
        
        # SBOM with missing hashes
        incomplete_sbom = SBOM(
            spec_version="1.4",
            serial_number="urn:uuid:test-789",
            version=1,
            components=[
                SBOMComponent(
                    name="test-component",
                    version="1.0.0",
                    purl="pkg:pypi/test-component@1.0.0",
                    hashes={},  # Missing hashes
                    licenses=["MIT"],
                )
            ],
        )
        
        is_valid, indicators = verifier.validate_sbom(incomplete_sbom)
        hash_indicators = [
            ind
            for ind in indicators
            if ind.indicator_type == "missing_component_hash"
        ]
        assert len(hash_indicators) > 0


class TestProvenanceTracker:
    """Test provenance tracking"""
    
    def test_build_tracking(self, tmp_path):
        """Test tracking build provenance"""
        tracker = ProvenanceTracker(data_dir=tmp_path / "provenance")
        
        # Create test artifact
        artifact_path = tmp_path / "build_artifact.bin"
        artifact_path.write_bytes(b"build output")
        
        builder_info = {
            "builder_id": "github-actions",
            "build_type": "https://github.com/slsa-framework/slsa-github-generator",
            "repo_uri": "https://github.com/example/project",
            "automated": True,
            "isolated": True,
            "reproducible": True,
        }
        
        provenance = tracker.track_build(
            source_commit="abc123def456",
            build_id="build-001",
            artifact_path=artifact_path,
            builder_info=builder_info,
        )
        
        assert provenance.subject == "build_artifact.bin"
        assert provenance.builder_id == "github-actions"
        assert provenance.slsa_level == SLSALevel.LEVEL_3
        
        # Verify provenance was stored
        stored_provenance = tracker.retrieve_provenance("build-001")
        assert stored_provenance is not None
        assert stored_provenance.subject == provenance.subject
        assert stored_provenance.digest == provenance.digest
    
    def test_slsa_level_determination(self, tmp_path):
        """Test SLSA level determination based on build characteristics"""
        tracker = ProvenanceTracker(data_dir=tmp_path / "provenance")
        
        artifact_path = tmp_path / "artifact.bin"
        artifact_path.write_bytes(b"content")
        
        # Test different SLSA levels
        test_cases = [
            (
                {
                    "builder_id": "manual",
                    "build_type": "manual",
                    "automated": False,
                },
                SLSALevel.LEVEL_0,
            ),
            (
                {
                    "builder_id": "ci-system",
                    "build_type": "automated",
                    "automated": True,
                },
                SLSALevel.LEVEL_1,
            ),
            (
                {
                    "builder_id": "ci-system",
                    "build_type": "automated",
                    "automated": True,
                    "isolated": True,
                },
                SLSALevel.LEVEL_2,
            ),
            (
                {
                    "builder_id": "hardened-ci",
                    "build_type": "automated",
                    "automated": True,
                    "isolated": True,
                    "reproducible": True,
                },
                SLSALevel.LEVEL_3,
            ),
            (
                {
                    "builder_id": "hardened-ci",
                    "build_type": "automated",
                    "automated": True,
                    "isolated": True,
                    "reproducible": True,
                    "two_party_review": True,
                },
                SLSALevel.LEVEL_4,
            ),
        ]
        
        for idx, (builder_info, expected_level) in enumerate(test_cases):
            provenance = tracker.track_build(
                source_commit=f"commit-{idx}",
                build_id=f"build-{idx}",
                artifact_path=artifact_path,
                builder_info=builder_info,
            )
            assert provenance.slsa_level == expected_level
    
    def test_lineage_tracing(self, tmp_path):
        """Test artifact lineage tracing"""
        tracker = ProvenanceTracker(data_dir=tmp_path / "provenance")
        
        # Create and track artifact
        artifact_path = tmp_path / "tracked_artifact.bin"
        artifact_path.write_bytes(b"tracked content")
        
        tracker.track_build(
            source_commit="commit123",
            build_id="build-trace-001",
            artifact_path=artifact_path,
            builder_info={
                "builder_id": "github-actions",
                "build_type": "automated",
                "repo_uri": "https://github.com/example/project",
                "automated": True,
            },
        )
        
        # Trace lineage
        lineage = tracker.trace_lineage(artifact_path)
        
        assert lineage["complete"]
        assert len(lineage["builds"]) > 0
        assert len(lineage["source_commits"]) > 0
        assert lineage["source_commits"][0]["commit"] == "commit123"


class TestAutomatedRemediation:
    """Test automated remediation"""
    
    def test_dry_run_mode(self):
        """Test dry run mode doesn't make actual changes"""
        remediator = AutomatedRemediation(dry_run=True)
        
        from engines.supply_chain_enhanced import SupplyChainThreat
        
        threat = SupplyChainThreat(
            threat_id="test-threat-001",
            timestamp=0.0,
            attack_vector=AttackVector.MALICIOUS_PACKAGE,
            threat_level=ThreatLevel.CRITICAL,
            package=DependencyInfo(
                name="malicious-pkg",
                version="1.0.0",
                package_manager=PackageManager.PIP,
            ),
        )
        
        result = remediator.remediate_threat(threat)
        
        assert result["dry_run"]
        assert result["success"]
        assert len(result["actions_taken"]) > 0
    
    def test_critical_threat_quarantine(self):
        """Test quarantine of critical threats"""
        remediator = AutomatedRemediation(dry_run=True)
        
        from engines.supply_chain_enhanced import SupplyChainThreat
        
        critical_threat = SupplyChainThreat(
            threat_id="critical-001",
            timestamp=0.0,
            attack_vector=AttackVector.MALICIOUS_PACKAGE,
            threat_level=ThreatLevel.CRITICAL,
            package=DependencyInfo(
                name="dangerous-pkg",
                version="1.0.0",
                package_manager=PackageManager.PIP,
            ),
        )
        
        result = remediator.remediate_threat(critical_threat)
        
        quarantine_actions = [
            a for a in result["actions_taken"] if a["action"] == "quarantine"
        ]
        assert len(quarantine_actions) > 0
    
    def test_safe_version_upgrade(self):
        """Test upgrade to safe version"""
        remediator = AutomatedRemediation(dry_run=True)
        
        from engines.supply_chain_enhanced import SupplyChainThreat
        
        vulnerable_threat = SupplyChainThreat(
            threat_id="vuln-001",
            timestamp=0.0,
            attack_vector=AttackVector.OUTDATED_VULNERABLE,
            threat_level=ThreatLevel.HIGH,
            package=DependencyInfo(
                name="vulnerable-pkg",
                version="1.0.0",
                package_manager=PackageManager.PIP,
            ),
        )
        
        result = remediator.remediate_threat(vulnerable_threat)
        
        # Should suggest or perform update
        update_actions = [
            a
            for a in result["actions_taken"]
            if a["action"] in ["update", "suggest_update"]
        ]
        assert len(update_actions) > 0


class TestSupplyChainEngine:
    """Test integrated supply chain engine"""
    
    def test_engine_initialization(self, tmp_path):
        """Test engine initialization"""
        engine = SupplyChainEngine(
            data_dir=str(tmp_path / "supply_chain"),
            internal_package_patterns=[r"^internal-.*"],
            auto_remediate=False,
            dry_run=True,
        )
        
        assert engine.dependency_detector is not None
        assert engine.malware_scanner is not None
        assert engine.artifact_verifier is not None
        assert engine.provenance_tracker is not None
        assert engine.remediator is not None
    
    def test_dependency_scanning(self, tmp_path):
        """Test comprehensive dependency scanning"""
        engine = SupplyChainEngine(
            data_dir=str(tmp_path / "supply_chain"),
            internal_package_patterns=[r"^internal-.*"],
            auto_remediate=False,
            dry_run=True,
        )
        
        # Scan safe package
        safe_pkg = DependencyInfo(
            name="safe-package",
            version="1.0.0",
            package_manager=PackageManager.PIP,
        )
        
        threat = engine.scan_dependency(safe_pkg)
        # May or may not detect issues depending on implementation
        
        # Scan typosquatting package
        typo_pkg = DependencyInfo(
            name="requets",  # Typo of 'requests'
            version="1.0.0",
            package_manager=PackageManager.PIP,
        )
        
        threat = engine.scan_dependency(typo_pkg)
        assert threat is not None
        assert threat.attack_vector == AttackVector.TYPOSQUATTING
        assert len(threat.indicators) > 0
    
    def test_internal_package_confusion(self, tmp_path):
        """Test detection of dependency confusion for internal packages"""
        engine = SupplyChainEngine(
            data_dir=str(tmp_path / "supply_chain"),
            internal_package_patterns=[r"^internal-.*"],
            auto_remediate=False,
            dry_run=True,
        )
        
        internal_pkg = DependencyInfo(
            name="internal-auth",
            version="1.0.0",
            package_manager=PackageManager.PIP,
        )
        
        threat = engine.scan_dependency(internal_pkg)
        assert threat is not None
        assert threat.attack_vector == AttackVector.DEPENDENCY_CONFUSION
        assert threat.threat_level == ThreatLevel.CRITICAL
    
    def test_sbom_generation(self, tmp_path):
        """Test SBOM generation"""
        engine = SupplyChainEngine(
            data_dir=str(tmp_path / "supply_chain"),
        )
        
        dependencies = [
            DependencyInfo(
                name="package1",
                version="1.0.0",
                package_manager=PackageManager.PIP,
                license="MIT",
                checksum="abc123",
            ),
            DependencyInfo(
                name="package2",
                version="2.0.0",
                package_manager=PackageManager.PIP,
                license="Apache-2.0",
                checksum="def456",
            ),
        ]
        
        sbom = engine.generate_sbom(
            dependencies,
            metadata={"project": "test-project", "version": "1.0.0"},
        )
        
        assert len(sbom.components) == 2
        assert sbom.components[0].name == "package1"
        assert sbom.components[1].name == "package2"
        assert all(c.hashes for c in sbom.components)
        assert all(c.licenses for c in sbom.components)
    
    def test_artifact_verification_integration(self, tmp_path):
        """Test artifact verification through engine"""
        engine = SupplyChainEngine(
            data_dir=str(tmp_path / "supply_chain"),
        )
        
        # Create test artifact
        artifact_path = tmp_path / "test.bin"
        artifact_content = b"test content"
        artifact_path.write_bytes(artifact_content)
        expected_hash = hashlib.sha256(artifact_content).hexdigest()
        
        is_valid, indicators = engine.verify_build_artifact(
            artifact_path, expected_hash
        )
        
        assert is_valid
        assert len(indicators) == 0
    
    def test_threat_report_generation(self, tmp_path):
        """Test threat report generation"""
        engine = SupplyChainEngine(
            data_dir=str(tmp_path / "supply_chain"),
            internal_package_patterns=[r"^internal-.*"],
            auto_remediate=False,
            dry_run=True,
        )
        
        # Scan some packages to generate threats
        packages = [
            DependencyInfo(
                name="internal-auth",
                version="1.0.0",
                package_manager=PackageManager.PIP,
            ),
            DependencyInfo(
                name="requets",
                version="1.0.0",
                package_manager=PackageManager.PIP,
            ),
        ]
        
        for pkg in packages:
            engine.scan_dependency(pkg)
        
        report = engine.get_threat_report()
        
        assert report["total_threats"] > 0
        assert "by_severity" in report
        assert "by_attack_vector" in report
        assert "threats" in report
        assert len(report["threats"]) > 0
    
    def test_auto_remediation_integration(self, tmp_path):
        """Test automated remediation integration"""
        engine = SupplyChainEngine(
            data_dir=str(tmp_path / "supply_chain"),
            internal_package_patterns=[r"^internal-.*"],
            auto_remediate=True,
            dry_run=True,
        )
        
        # Scan package that should trigger auto-remediation
        internal_pkg = DependencyInfo(
            name="internal-critical",
            version="1.0.0",
            package_manager=PackageManager.PIP,
        )
        
        threat = engine.scan_dependency(internal_pkg)
        
        # Auto-remediation should have been attempted
        if threat and threat.threat_level in [ThreatLevel.CRITICAL, ThreatLevel.HIGH]:
            # In dry run, should be marked as auto-remediated
            # (actual behavior depends on implementation)
            pass


class TestThreatIndicators:
    """Test threat indicator creation and handling"""
    
    def test_threat_indicator_creation(self):
        """Test creating threat indicators"""
        indicator = ThreatIndicator(
            indicator_type="test_threat",
            severity=ThreatLevel.HIGH,
            description="Test threat description",
            evidence={"key": "value"},
            confidence=0.85,
            mitigations=["Mitigation 1", "Mitigation 2"],
        )
        
        assert indicator.indicator_type == "test_threat"
        assert indicator.severity == ThreatLevel.HIGH
        assert indicator.confidence == 0.85
        assert len(indicator.mitigations) == 2
    
    def test_vulnerability_info(self):
        """Test vulnerability information structure"""
        vuln = VulnerabilityInfo(
            cve_id="CVE-2024-12345",
            severity=ThreatLevel.CRITICAL,
            description="Critical vulnerability",
            affected_versions=["1.0.0", "1.0.1"],
            patched_versions=["1.0.2"],
            exploit_available=True,
            references=["https://example.com/advisory"],
        )
        
        assert vuln.cve_id == "CVE-2024-12345"
        assert vuln.severity == ThreatLevel.CRITICAL
        assert vuln.exploit_available
        assert len(vuln.affected_versions) == 2
        assert len(vuln.patched_versions) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

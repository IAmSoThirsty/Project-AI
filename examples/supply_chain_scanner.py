#!/usr/bin/env python3
"""
Supply Chain Security Scanner Example

Demonstrates scanning dependencies for supply chain threats.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from engines.supply_chain_enhanced import (
    SupplyChainEngine,
    DependencyInfo,
    PackageManager,
    ThreatLevel,
)


def main():
    """Main example function"""
    
    print("=" * 70)
    print("Supply Chain Security Scanner Example")
    print("=" * 70)
    
    # Initialize engine with internal package patterns
    print("\n1. Initializing Supply Chain Engine...")
    engine = SupplyChainEngine(
        data_dir="data/supply_chain_demo",
        internal_package_patterns=[
            r"^mycompany-.*",
            r"^internal-.*",
            r"^private-.*",
        ],
        auto_remediate=True,
        dry_run=True,
    )
    print("   ✓ Engine initialized")
    
    # Example 1: Scan safe package
    print("\n2. Scanning Safe Package (requests)...")
    safe_pkg = DependencyInfo(
        name="requests",
        version="2.28.2",
        package_manager=PackageManager.PIP,
        license="Apache-2.0",
        checksum="abc123",
    )
    
    threat = engine.scan_dependency(safe_pkg)
    if threat:
        print(f"   ⚠️  Threat detected: {threat.attack_vector.value}")
    else:
        print("   ✓ Package is safe")
    
    # Example 2: Scan typosquatting attempt
    print("\n3. Scanning Typosquatting Package (requets)...")
    typo_pkg = DependencyInfo(
        name="requets",  # Typo of 'requests'
        version="2.28.0",
        package_manager=PackageManager.PIP,
    )
    
    threat = engine.scan_dependency(typo_pkg)
    if threat:
        print(f"   ✗ THREAT: {threat.attack_vector.value}")
        print(f"   Severity: {threat.threat_level.value}")
        for indicator in threat.indicators:
            print(f"   - {indicator.description}")
            print(f"     Mitigations:")
            for mitigation in indicator.mitigations:
                print(f"       • {mitigation}")
    
    # Example 3: Scan internal package (dependency confusion)
    print("\n4. Scanning Internal Package (mycompany-auth)...")
    internal_pkg = DependencyInfo(
        name="mycompany-auth",
        version="1.0.0",
        package_manager=PackageManager.PIP,
    )
    
    threat = engine.scan_dependency(internal_pkg)
    if threat:
        print(f"   ✗ THREAT: {threat.attack_vector.value}")
        print(f"   Severity: {threat.threat_level.value}")
        print(f"   Auto-remediated: {threat.auto_remediated}")
        if threat.auto_remediated:
            print(f"   Remediation actions:")
            for action in threat.remediation_actions:
                print(f"     • {action}")
    
    # Example 4: Generate SBOM
    print("\n5. Generating SBOM...")
    dependencies = [
        DependencyInfo(
            name="requests",
            version="2.28.2",
            package_manager=PackageManager.PIP,
            license="Apache-2.0",
            checksum="abc123",
        ),
        DependencyInfo(
            name="flask",
            version="2.3.0",
            package_manager=PackageManager.PIP,
            license="BSD-3-Clause",
            checksum="def456",
        ),
        DependencyInfo(
            name="pytest",
            version="7.4.0",
            package_manager=PackageManager.PIP,
            license="MIT",
            checksum="ghi789",
        ),
    ]
    
    sbom = engine.generate_sbom(
        dependencies,
        metadata={
            "project": "demo-project",
            "version": "1.0.0",
            "supplier": "Demo Company",
        },
    )
    
    print(f"   ✓ SBOM generated")
    print(f"   Components: {len(sbom.components)}")
    print(f"   Spec version: {sbom.spec_version}")
    
    # Example 5: Threat report
    print("\n6. Generating Threat Report...")
    report = engine.get_threat_report()
    
    print(f"   Total threats: {report['total_threats']}")
    print(f"   By severity:")
    for severity, count in report['by_severity'].items():
        print(f"     - {severity}: {count}")
    print(f"   By attack vector:")
    for vector, count in report['by_attack_vector'].items():
        print(f"     - {vector}: {count}")
    print(f"   Auto-remediated: {report['auto_remediated']}")
    
    # Example 6: Artifact verification
    print("\n7. Verifying Build Artifact...")
    
    # Create test artifact
    artifact_path = Path("data/supply_chain_demo/demo_artifact.bin")
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_content = b"demo artifact content"
    artifact_path.write_bytes(artifact_content)
    
    import hashlib
    expected_hash = hashlib.sha256(artifact_content).hexdigest()
    
    is_valid, indicators = engine.verify_build_artifact(
        artifact_path,
        expected_hash=expected_hash,
    )
    
    if is_valid:
        print("   ✓ Artifact verification PASSED")
    else:
        print("   ✗ Artifact verification FAILED")
        for indicator in indicators:
            print(f"   - {indicator.description}")
    
    # Example 7: Provenance tracking
    print("\n8. Tracking Build Provenance...")
    
    provenance = engine.provenance_tracker.track_build(
        source_commit="abc123def456789",
        build_id="demo-build-001",
        artifact_path=artifact_path,
        builder_info={
            "builder_id": "github-actions",
            "build_type": "https://github.com/slsa-framework/slsa-github-generator",
            "repo_uri": "https://github.com/demo/project",
            "automated": True,
            "isolated": True,
            "reproducible": True,
        },
    )
    
    print(f"   ✓ Provenance tracked")
    print(f"   Build ID: demo-build-001")
    print(f"   SLSA Level: {provenance.slsa_level.value}")
    print(f"   Builder: {provenance.builder_id}")
    
    # Example 8: Lineage tracing
    print("\n9. Tracing Artifact Lineage...")
    
    lineage = engine.provenance_tracker.trace_lineage(artifact_path)
    
    print(f"   ✓ Lineage traced")
    print(f"   Complete: {lineage['complete']}")
    print(f"   Builds: {len(lineage['builds'])}")
    print(f"   Source commits: {len(lineage['source_commits'])}")
    
    if lineage['source_commits']:
        print(f"   First commit: {lineage['source_commits'][0]['commit'][:12]}")
    
    print("\n" + "=" * 70)
    print("Supply Chain Security Scanner Example Complete")
    print("=" * 70)
    
    # Summary
    print("\n📊 SUMMARY:")
    print(f"   Total packages scanned: 3")
    print(f"   Threats detected: {report['total_threats']}")
    print(f"   Critical: {report['by_severity'].get('critical', 0)}")
    print(f"   High: {report['by_severity'].get('high', 0)}")
    print(f"   Auto-remediated: {report['auto_remediated']}")
    print(f"   Artifacts verified: 1")
    print(f"   Builds tracked: 1")


if __name__ == "__main__":
    main()

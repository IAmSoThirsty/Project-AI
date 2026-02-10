"""
Build Memory Integration Example.

Demonstrates how the database system integrates with Gradle builds,
constitutional validation, and security scanning.
"""

from datetime import datetime
from pathlib import Path

from gradle_evolution.db import (
    BuildGraphDB,
    BuildMemoryDB,
    BuildQueryEngine,
    MemoryManager,
)
from gradle_evolution.db.memory_manager import RetentionPolicy


def main():
    """Run integration example."""
    print("=== Build Memory Database Integration Example ===\n")

    # Initialize database
    print("1. Initializing database...")
    db = BuildMemoryDB()  # Uses data/build_memory.db
    print(f"   Database initialized at: {db.db_path}")
    print(f"   Schema version: {db.get_schema_version()}")
    print()

    # Create a build record
    print("2. Recording build execution...")
    build_id = db.create_build(
        version="2.0.0-SNAPSHOT",
        status="running",
        capsule_id="gradle-capsule-123",
        gradle_version="8.5",
        java_version="17.0.8",
        os_info="Linux 5.15.0",
        host_name="build-server-01",
        user_name="gradle-bot",
    )
    print(f"   Build ID: {build_id}")
    print()

    # Record build phases
    print("3. Tracking build phases...")
    phases = [
        ("initialization", "success", 2.5),
        ("configuration", "success", 5.2),
        ("compilation", "success", 45.8),
        ("testing", "success", 120.3),
        ("packaging", "success", 15.7),
    ]

    for phase_name, status, duration in phases:
        phase_id = db.create_build_phase(
            build_id=build_id,
            phase=phase_name,
            status=status,
            logs_path=f"logs/{phase_name}.log",
        )
        db.update_build_phase(
            phase_id,
            status=status,
            end_time=datetime.utcnow().isoformat(),
            duration=duration,
        )
        print(f"   ✓ {phase_name}: {status} ({duration}s)")
    print()

    # Record constitutional validation
    print("4. Recording constitutional compliance...")

    # Simulate a determinism violation
    violation_id = db.create_violation(
        build_id=build_id,
        phase="compilation",
        principle="DETERMINISM",
        severity="medium",
        reason="Timestamp embedded in compiled artifact",
    )
    print("   ⚠ Violation detected: DETERMINISM (medium)")
    print(f"     Violation ID: {violation_id}")

    # Waive the violation with justification
    db.waive_violation(
        violation_id,
        waiver_reason="Timestamp is intentional for build versioning",
        waived_by="tech-lead@example.com",
    )
    print("   ✓ Violation waived by tech-lead@example.com")
    print()

    # Record security events
    print("5. Recording security events...")

    # Simulate vulnerability detection
    event_id = db.create_security_event(
        build_id=build_id,
        event_type="dependency_vulnerability",
        severity="high",
        details="Detected CVE-2024-1234 in commons-codec:1.15",
        cve_ids=["CVE-2024-1234"],
        cvss_score=7.5,
        affected_components=["commons-codec:1.15"],
    )
    print("   🔒 Security event: dependency_vulnerability (high)")
    print(f"     Event ID: {event_id}")
    print("     CVE: CVE-2024-1234 (CVSS 7.5)")
    print()

    # Record artifacts
    print("6. Recording build artifacts...")
    artifacts = [
        ("build/libs/app-2.0.0.jar", "sha256:abc123def456", 2048576, "jar", True),
        (
            "build/libs/app-2.0.0-sources.jar",
            "sha256:def789ghi012",
            512000,
            "jar",
            False,
        ),
        (
            "build/distributions/app-2.0.0.tar.gz",
            "sha256:jkl345mno678",
            3145728,
            "tar.gz",
            True,
        ),
    ]

    for path, hash_val, size, artifact_type, signed in artifacts:
        db.create_artifact(
            build_id=build_id,
            path=path,
            hash=hash_val,
            size=size,
            artifact_type=artifact_type,
            signed=signed,
            signature_hash=f"sig-{hash_val}" if signed else None,
        )
        sign_status = "✓ signed" if signed else "unsigned"
        print(f"   📦 {Path(path).name}: {size // 1024} KB ({sign_status})")
    print()

    # Record dependencies
    print("7. Recording dependencies...")
    dependencies = [
        ("org.springframework.boot:spring-boot-starter-web", "3.1.5", 0, "Apache-2.0"),
        ("com.fasterxml.jackson.core:jackson-databind", "2.15.3", 0, "Apache-2.0"),
        ("commons-codec:commons-codec", "1.15", 1, "Apache-2.0"),  # 1 vulnerability
        ("org.slf4j:slf4j-api", "2.0.9", 0, "MIT"),
    ]

    for name, version, vuln_count, license in dependencies:
        db.create_dependency(
            build_id=build_id,
            name=name,
            version=version,
            source="maven-central",
            license=license,
            vulnerabilities=(
                [{"cve": "CVE-2024-1234", "severity": "high"}]
                if vuln_count > 0
                else None
            ),
        )
        vuln_indicator = f"⚠ {vuln_count} vuln" if vuln_count > 0 else "✓ clean"
        print(f"   📚 {name}:{version} ({vuln_indicator})")
    print()

    # Update build status
    print("8. Finalizing build...")
    total_duration = sum(duration for _, _, duration in phases)
    db.update_build(
        build_id,
        status="success",
        duration=total_duration,
        constitutional_status="waived",
        exit_code=0,
    )
    print("   ✓ Build completed successfully")
    print(f"   Duration: {total_duration:.1f}s")
    print("   Status: success (constitutional: waived)")
    print()

    # Build graph and analyze
    print("9. Building historical graph...")
    graph = BuildGraphDB(db)
    graph.build_graph(limit=100)

    stats = graph.get_graph_statistics()
    print(f"   Nodes: {stats['nodes']['total']}")
    print(f"     - Builds: {stats['nodes']['builds']}")
    print(f"     - Artifacts: {stats['nodes']['artifacts']}")
    print(f"     - Dependencies: {stats['nodes']['dependencies']}")
    print(f"   Edges: {stats['edges']['total']}")
    print()

    # Run analytics
    print("10. Running analytics...")
    query_engine = BuildQueryEngine(db)

    # Build trends
    trends = query_engine.analyze_build_trends(days=7)
    if trends.get("total_builds", 0) > 0:
        print("    Build Trends (7 days):")
        print(f"      Total builds: {trends['total_builds']}")
        print(f"      Success rate: {trends['success_rate']}%")
        print(f"      Avg duration: {trends['avg_duration_seconds']:.1f}s")

    # Constitutional compliance
    compliance = query_engine.analyze_constitutional_compliance(days=7)
    if compliance.get("total_builds", 0) > 0:
        print("    Constitutional Compliance (7 days):")
        print(f"      Total builds: {compliance['total_builds']}")
        print(f"      Compliance rate: {compliance['compliance_rate']}%")
        print(f"      Total violations: {compliance['total_violations']}")
    print()

    # Memory management
    print("11. Checking database health...")
    policy = RetentionPolicy(
        keep_last_n_builds=50,
        keep_days=30,
        keep_failed_builds=True,
        keep_with_violations=True,
    )
    manager = MemoryManager(db, retention_policy=policy)

    health = manager.get_health_status()
    print(f"    Health status: {health['status']}")
    if health.get("warnings"):
        for warning in health["warnings"]:
            print(f"      ⚠ {warning}")

    usage = manager.get_memory_usage()
    print(f"    Database size: {usage['total_size_mb']:.2f} MB")
    print(f"    Total records: {sum(usage['record_counts'].values())}")
    print()

    # Export graph
    print("12. Exporting graph...")
    output_dir = Path("build/graph-exports")
    output_dir.mkdir(parents=True, exist_ok=True)

    graph.export_to_dot(output_dir / "build_graph.dot")
    graph.export_to_json(output_dir / "build_graph.json")
    print(f"    ✓ Exported to {output_dir}/")
    print()

    # Database statistics
    print("13. Database statistics:")
    db_stats = db.get_statistics()
    for table, count in db_stats.items():
        print(f"    {table}: {count} records")
    print()

    print("=== Integration Example Complete ===")
    print(f"\nBuild {build_id} recorded with full history, graph, and analytics.")


if __name__ == "__main__":
    main()

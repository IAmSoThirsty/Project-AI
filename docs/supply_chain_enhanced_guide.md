# Enhanced Supply Chain Attack Engine

## Overview

The Enhanced Supply Chain Attack Engine provides comprehensive detection and prevention of supply chain attacks targeting software dependencies and build artifacts. This engine implements industry-standard frameworks including SLSA, SBOM standards, and OWASP LLM05 guidelines.

## Features

### 1. Dependency Confusion Detection

Detects malicious packages with the same name as internal packages (dependency confusion attacks):

- **Pattern Matching**: Configurable regex patterns for internal package names
- **Public Registry Checking**: Validates whether internal package names exist in public registries
- **Risk Assessment**: High-confidence detection with detailed mitigation strategies
- **Priority Configuration**: Recommendations for registry configuration

**Example**:
```python
from engines.supply_chain_enhanced import (
    SupplyChainEngine,
    DependencyInfo,
    PackageManager,
)

# Initialize with internal package patterns
engine = SupplyChainEngine(
    internal_package_patterns=[
        r"^mycompany-.*",
        r"^internal-.*",
        r"^corp-.*",
    ]
)

# Scan internal package
pkg = DependencyInfo(
    name="mycompany-auth",
    version="1.0.0",
    package_manager=PackageManager.PIP,
)

threat = engine.scan_dependency(pkg)
if threat:
    print(f"Threat: {threat.attack_vector.value}")
    print(f"Severity: {threat.threat_level.value}")
    for indicator in threat.indicators:
        print(f"  - {indicator.description}")
```

### 2. Malicious Package Identification

Multi-layered analysis for detecting malicious packages:

#### Static Analysis
- **Typosquatting Detection**: Levenshtein distance algorithm for popular package names
- **Known Malicious Signatures**: Database of known malicious package checksums
- **Suspicious Maintainer Patterns**: Pattern matching for fake/compromised maintainers
- **Code Pattern Analysis**: Detection of suspicious code patterns:
  - Network exfiltration attempts
  - Environment variable access
  - File system manipulation
  - Process execution
  - Code obfuscation (eval, exec, compile)
  - Cryptocurrency mining indicators

#### Dynamic Analysis
- **Sandbox Execution**: Optional runtime behavior monitoring
- **Resource Usage Monitoring**: CPU/memory/network usage patterns
- **API Call Tracking**: Monitoring of suspicious API calls
- **Behavioral Indicators**: Detection of malicious runtime behavior

**Example**:
```python
# Scan with static analysis only
threat = engine.scan_dependency(pkg, enable_dynamic=False)

# Scan with full dynamic analysis (slower but thorough)
threat = engine.scan_dependency(pkg, enable_dynamic=True)
```

### 3. Build Artifact Verification

SLSA-compliant artifact verification and validation:

#### Checksum Verification
- **SHA256 Hash Validation**: Cryptographic verification of artifact integrity
- **Multi-hash Support**: Support for multiple hash algorithms
- **Tamper Detection**: Immediate detection of modified artifacts

#### SLSA Provenance Verification
- **Builder Validation**: Trusted builder identity verification
- **Build Process Attestation**: Verification of build process metadata
- **Material Tracking**: Validation of source materials and dependencies
- **Reproducibility**: Support for reproducible builds

**SLSA Levels**:
- **Level 0**: No guarantees
- **Level 1**: Documentation of build process
- **Level 2**: Tamper-resistant build service
- **Level 3**: Hardened build platform
- **Level 4**: Two-party review (highest confidence)

**Example**:
```python
from pathlib import Path

# Verify artifact with checksum
is_valid, indicators = engine.verify_build_artifact(
    artifact_path=Path("dist/myapp-1.0.0.whl"),
    expected_hash="abc123...",
)

# Verify artifact with SLSA provenance
is_valid, indicators = engine.verify_build_artifact(
    artifact_path=Path("dist/myapp-1.0.0.whl"),
    expected_hash="abc123...",
    provenance_path=Path("dist/myapp-1.0.0.whl.provenance.json"),
)

if not is_valid:
    for indicator in indicators:
        print(f"Issue: {indicator.description}")
        print(f"Severity: {indicator.severity.value}")
```

### 4. Provenance Tracking

Complete build lineage tracking from source to binary:

#### Build Tracking
- **Source Commit Tracking**: Git commit hash association
- **Build Environment Recording**: Complete build environment metadata
- **Builder Identity**: Cryptographic builder identification
- **Build Parameters**: All build configuration and parameters

#### Lineage Tracing
- **Source-to-Binary Mapping**: Complete traceability
- **Dependency Graphs**: Full dependency tree with provenance
- **Build Reproducibility**: Verification of reproducible builds
- **Audit Trail**: Complete audit trail for compliance

**Example**:
```python
# Track a build
provenance = engine.provenance_tracker.track_build(
    source_commit="abc123def456",
    build_id="build-2024-001",
    artifact_path=Path("dist/artifact.bin"),
    builder_info={
        "builder_id": "github-actions",
        "build_type": "https://github.com/slsa-framework/slsa-github-generator",
        "repo_uri": "https://github.com/myorg/myproject",
        "automated": True,
        "isolated": True,
        "reproducible": True,
        "two_party_review": True,
    },
)

print(f"SLSA Level: {provenance.slsa_level.value}")

# Trace artifact lineage
lineage = engine.provenance_tracker.trace_lineage(
    Path("dist/artifact.bin")
)

print(f"Source commits: {lineage['source_commits']}")
print(f"Builds: {lineage['builds']}")
print(f"Complete: {lineage['complete']}")
```

### 5. Automated Remediation

Intelligent automated response to detected threats:

#### Threat Response Strategies

**Critical Threats** (Immediate Action):
- Immediate quarantine
- Block installation/usage
- Find and suggest safe alternatives
- Alert security team

**High Threats** (Urgent Action):
- Find safe version
- Auto-update if configured
- Schedule immediate review
- Generate remediation plan

**Medium Threats** (Scheduled Action):
- Schedule security review
- Add to watchlist
- Plan upgrade path

**Low/Info** (Monitor):
- Log for analysis
- Add to reports

**Example**:
```python
# Enable auto-remediation with dry run
engine = SupplyChainEngine(
    auto_remediate=True,
    dry_run=True,  # Simulate actions without making changes
)

threat = engine.scan_dependency(malicious_pkg)

if threat.auto_remediated:
    print("Threat auto-remediated:")
    print(f"  - Quarantined: {threat.quarantined}")
    print(f"  - Actions: {threat.remediation_actions}")

# Manual remediation
result = engine.remediator.remediate_threat(threat)
print(f"Actions taken: {result['actions_taken']}")
```

## SBOM (Software Bill of Materials)

### Generation

Generate CycloneDX/SPDX-compliant SBOMs:

```python
from engines.supply_chain_enhanced import DependencyInfo, PackageManager

dependencies = [
    DependencyInfo(
        name="requests",
        version="2.28.2",
        package_manager=PackageManager.PIP,
        license="Apache-2.0",
        checksum="abc123...",
    ),
    DependencyInfo(
        name="flask",
        version="2.3.0",
        package_manager=PackageManager.PIP,
        license="BSD-3-Clause",
        checksum="def456...",
    ),
]

sbom = engine.generate_sbom(
    dependencies,
    metadata={
        "project": "my-project",
        "version": "1.0.0",
        "supplier": "My Company",
    },
)

print(f"Components: {len(sbom.components)}")
print(f"Spec version: {sbom.spec_version}")

# Export SBOM
import json
with open("sbom.json", "w") as f:
    json.dump({
        "bomFormat": "CycloneDX",
        "specVersion": sbom.spec_version,
        "serialNumber": sbom.serial_number,
        "version": sbom.version,
        "metadata": sbom.metadata,
        "components": [
            {
                "name": c.name,
                "version": c.version,
                "purl": c.purl,
                "hashes": c.hashes,
                "licenses": c.licenses,
            }
            for c in sbom.components
        ],
    }, f, indent=2)
```

### Validation

Validate SBOM completeness and compliance:

```python
is_valid, indicators = engine.artifact_verifier.validate_sbom(sbom)

if not is_valid:
    for indicator in indicators:
        if indicator.indicator_type == "missing_component_hash":
            print(f"Missing hash for: {indicator.evidence['component']}")
        elif indicator.indicator_type == "missing_license":
            print(f"Missing license for: {indicator.evidence['component']}")
```

## Threat Reporting

### Comprehensive Reports

```python
report = engine.get_threat_report()

print(f"Total threats: {report['total_threats']}")
print(f"By severity: {report['by_severity']}")
print(f"By attack vector: {report['by_attack_vector']}")
print(f"Auto-remediated: {report['auto_remediated']}")
print(f"Quarantined: {report['quarantined']}")

for threat in report['threats']:
    print(f"\nThreat: {threat['threat_id']}")
    print(f"  Package: {threat['package']}")
    print(f"  Level: {threat['threat_level']}")
    print(f"  Vector: {threat['attack_vector']}")
    print(f"  Indicators: {threat['indicators_count']}")
```

## Architecture

### Components

```
SupplyChainEngine
├── DependencyConfusionDetector
│   ├── Internal package pattern matching
│   └── Public registry collision detection
├── MaliciousPackageScanner
│   ├── Static analysis
│   │   ├── Typosquatting detection
│   │   ├── Known malicious signatures
│   │   ├── Maintainer validation
│   │   └── Code pattern analysis
│   └── Dynamic analysis
│       ├── Sandbox execution
│       └── Behavioral monitoring
├── ArtifactVerifier
│   ├── Checksum verification
│   ├── SLSA provenance validation
│   └── SBOM validation
├── ProvenanceTracker
│   ├── Build tracking
│   ├── Lineage tracing
│   └── SLSA level determination
└── AutomatedRemediation
    ├── Threat assessment
    ├── Quarantine management
    └── Safe version detection
```

### Data Flow

```
1. Dependency Input
   └─> Dependency Confusion Check
       └─> Static Malware Scan
           └─> [Optional] Dynamic Malware Scan
               └─> Threat Assessment
                   └─> [Optional] Auto Remediation
                       └─> Threat Logging
                           └─> Report Generation

2. Artifact Input
   └─> Checksum Verification
       └─> Provenance Verification
           └─> SLSA Level Check
               └─> Threat Detection
                   └─> Validation Result

3. Build Tracking
   └─> Source Commit Capture
       └─> Build Metadata Collection
           └─> Provenance Generation
               └─> SLSA Level Determination
                   └─> Provenance Storage
                       └─> Lineage Tracking
```

## Configuration

### Engine Initialization

```python
engine = SupplyChainEngine(
    # Data directory for persistence
    data_dir="data/supply_chain",
    
    # Internal package patterns for dependency confusion detection
    internal_package_patterns=[
        r"^mycompany-.*",
        r"^internal-.*",
        r"^private-.*",
    ],
    
    # Enable automated remediation
    auto_remediate=True,
    
    # Dry run mode (no actual changes)
    dry_run=True,
)
```

### Supported Package Managers

- **Python**: pip
- **JavaScript**: npm, yarn
- **Java**: Maven, Gradle
- **Rust**: Cargo
- **Go**: go mod
- **Ruby**: RubyGems
- **.NET**: NuGet

## Security Best Practices

### 1. Dependency Management

- **Pin Exact Versions**: Use exact version pins (e.g., `==2.28.2` not `>=2.28.0`)
- **Verify Checksums**: Always verify package checksums
- **Private Registry Priority**: Configure private registries to take priority
- **Block Public Collision**: Block public packages with internal names

### 2. Build Security

- **Use SLSA Level 3+**: Target SLSA Level 3 or higher for critical builds
- **Reproducible Builds**: Enable reproducible builds where possible
- **Isolated Build Environment**: Use isolated, ephemeral build environments
- **Two-Party Review**: Implement two-party review for critical artifacts

### 3. Artifact Verification

- **Always Verify Hashes**: Verify artifact checksums before deployment
- **Validate Provenance**: Check SLSA provenance for all production artifacts
- **Maintain SBOM**: Generate and maintain up-to-date SBOMs
- **Audit Trail**: Preserve complete audit trail for compliance

### 4. Threat Response

- **Automated Quarantine**: Auto-quarantine critical threats immediately
- **Regular Scans**: Run dependency scans on every build
- **Monitor Public Registries**: Watch for typosquatting attempts
- **Security Alerts**: Set up alerts for high/critical threats

## Integration Examples

### CI/CD Pipeline

```python
#!/usr/bin/env python3
"""CI/CD Supply Chain Security Check"""

import sys
from pathlib import Path
from engines.supply_chain_enhanced import (
    SupplyChainEngine,
    DependencyInfo,
    PackageManager,
    ThreatLevel,
)

def scan_dependencies(requirements_file: Path) -> bool:
    """Scan dependencies and fail on critical threats"""
    
    engine = SupplyChainEngine(
        internal_package_patterns=[r"^mycompany-.*"],
        auto_remediate=False,
        dry_run=False,
    )
    
    # Parse requirements
    dependencies = []
    for line in requirements_file.read_text().splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        
        # Simple parsing (production would use proper parser)
        parts = line.split("==")
        if len(parts) == 2:
            dependencies.append(DependencyInfo(
                name=parts[0].strip(),
                version=parts[1].strip(),
                package_manager=PackageManager.PIP,
            ))
    
    # Scan all dependencies
    critical_threats = []
    high_threats = []
    
    for dep in dependencies:
        threat = engine.scan_dependency(dep)
        if threat:
            if threat.threat_level == ThreatLevel.CRITICAL:
                critical_threats.append(threat)
            elif threat.threat_level == ThreatLevel.HIGH:
                high_threats.append(threat)
    
    # Report results
    print(f"Scanned {len(dependencies)} dependencies")
    print(f"Critical threats: {len(critical_threats)}")
    print(f"High threats: {len(high_threats)}")
    
    if critical_threats:
        print("\n❌ CRITICAL THREATS DETECTED:")
        for threat in critical_threats:
            print(f"  - {threat.package.name}@{threat.package.version}")
            print(f"    Vector: {threat.attack_vector.value}")
            for indicator in threat.indicators:
                print(f"    - {indicator.description}")
        return False
    
    if high_threats:
        print("\n⚠️  HIGH THREATS DETECTED (review required):")
        for threat in high_threats:
            print(f"  - {threat.package.name}@{threat.package.version}")
    
    print("\n✓ Supply chain scan complete")
    return True

if __name__ == "__main__":
    success = scan_dependencies(Path("requirements.txt"))
    sys.exit(0 if success else 1)
```

### Pre-commit Hook

```python
#!/usr/bin/env python3
"""Pre-commit hook for dependency scanning"""

import sys
from pathlib import Path
from engines.supply_chain_enhanced import SupplyChainEngine, ThreatLevel

def pre_commit_scan():
    """Scan dependencies before commit"""
    
    engine = SupplyChainEngine(
        internal_package_patterns=[r"^mycompany-.*"],
    )
    
    # Check for modified dependency files
    dep_files = [
        "requirements.txt",
        "package.json",
        "Cargo.toml",
    ]
    
    for dep_file in dep_files:
        if Path(dep_file).exists():
            # Scan dependencies (simplified)
            print(f"Scanning {dep_file}...")
            # ... scanning logic ...
    
    print("✓ Pre-commit supply chain scan passed")
    return True

if __name__ == "__main__":
    sys.exit(0 if pre_commit_scan() else 1)
```

## Performance Considerations

### Static vs Dynamic Analysis

- **Static Analysis**: Fast, suitable for CI/CD (milliseconds per package)
- **Dynamic Analysis**: Slower, use for deep inspection (seconds per package)

**Recommendation**: Use static analysis in CI/CD, dynamic analysis for security audits.

### Caching

```python
# Cache scan results to avoid redundant scans
cache = {}

def scan_with_cache(pkg: DependencyInfo):
    cache_key = f"{pkg.name}@{pkg.version}"
    
    if cache_key in cache:
        return cache[cache_key]
    
    threat = engine.scan_dependency(pkg)
    cache[cache_key] = threat
    return threat
```

### Parallel Scanning

```python
from concurrent.futures import ThreadPoolExecutor

def scan_dependencies_parallel(dependencies):
    """Scan multiple dependencies in parallel"""
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        threats = list(executor.map(engine.scan_dependency, dependencies))
    
    return [t for t in threats if t is not None]
```

## Compliance

### Standards Compliance

- **SLSA Framework**: Full compliance with SLSA v1.0
- **NIST SSDF**: Aligned with NIST Secure Software Development Framework
- **OWASP LLM05**: Addresses OWASP LLM Top 10 supply chain vulnerabilities
- **CycloneDX/SPDX**: Supports both SBOM standards

### Audit Trail

All threats and verifications are logged with:
- Timestamp
- Package details
- Threat indicators
- Remediation actions
- Verification results

### Reporting

Generate compliance reports:

```python
report = engine.get_threat_report()

# Export for compliance
import json
with open("compliance_report.json", "w") as f:
    json.dump(report, f, indent=2)
```

## Troubleshooting

### Common Issues

**Issue**: False positives in typosquatting detection

**Solution**: Adjust similarity threshold or add exceptions:
```python
# In MaliciousPackageScanner._check_typosquatting()
# Adjust edit_distance threshold from 2 to 1 for stricter matching
```

**Issue**: Slow dynamic analysis

**Solution**: Enable only for critical packages:
```python
# Use enable_dynamic=True selectively
if pkg.name in critical_packages:
    threat = engine.scan_dependency(pkg, enable_dynamic=True)
else:
    threat = engine.scan_dependency(pkg, enable_dynamic=False)
```

**Issue**: High memory usage with large SBOMs

**Solution**: Stream SBOM generation:
```python
# Generate SBOM in batches
batch_size = 100
for i in range(0, len(dependencies), batch_size):
    batch = dependencies[i:i+batch_size]
    sbom_batch = engine.generate_sbom(batch)
    # Process batch...
```

## License

See main project LICENSE file.

## References

- [SLSA Framework](https://slsa.dev/)
- [NIST SSDF](https://csrc.nist.gov/Projects/ssdf)
- [OWASP LLM Top 10](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
- [CycloneDX](https://cyclonedx.org/)
- [SPDX](https://spdx.dev/)
- [Package URL (purl)](https://github.com/package-url/purl-spec)

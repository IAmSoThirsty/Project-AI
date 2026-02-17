# Gradle Evolution Substrate - Quick Start

## Installation

The Evolution Substrate is already integrated. No installation needed.

## Basic Usage

### 1. Validate Your Build

```bash
gradle evolutionValidate
```
This checks constitutional compliance, policy enforcement, and security.

### 2. Run a Normal Build

```bash
gradle buildAll
```
Evolution validation runs automatically during `gradle check`.

### 3. Create a Release with Capsule

```bash
gradle release
```
Automatically includes:

- Constitutional validation
- Signed build capsule
- Comprehensive audit report
- Living documentation
- Transparency log

## Common Commands

```bash

# Check system status

gradle evolutionStatus

# Generate audit report

gradle evolutionAudit

# View help

gradle evolutionHelp

# Start verification API

gradle evolutionApiStart -PapiPort=8765
```

## Configuration

Edit `gradle.properties`:
```properties

# Enable/disable evolution

evolution.enabled=true

# Strict constitutional enforcement

evolution.constitutional.strict=true

# Sign all capsules

evolution.capsule.sign=true
```

## Troubleshooting

**Issue:** Validation fails
**Fix:** Check `policies/constitution.yaml` exists

**Issue:** Python dependencies missing
**Fix:** Run `gradle pythonInstall` first

**Issue:** Database errors
**Fix:** Ensure `data/` directory is writable

## Next Steps

1. Read `EVOLUTION_ARCHITECTURE.md` for complete documentation
2. Run `gradle evolutionHelp` for all commands
3. Check `tests/gradle_evolution/` for usage examples

## Support

See `GRADLE_EVOLUTION_COMPLETE.md` for comprehensive details.

# ═══════════════════════════════════════════════════════════════════════════
# THIRSTY'S GRADLE - BACKWARD COMPATIBILITY WRAPPER (PowerShell)
# ═══════════════════════════════════════════════════════════════════════════
# 
# This script provides backward compatibility with legacy build commands
# by mapping them to the new Gradle build system.
# 
# Usage: .\build-wrapper.ps1 <command>
# 
# Legacy commands are automatically translated to Gradle equivalents.
# ═══════════════════════════════════════════════════════════════════════════

param(
    [Parameter(Position=0)]
    [string]$Command = "help"
)

$GradleCmd = ".\gradlew.bat"

function Print-Info {
    param([string]$Message)
    Write-Host "ℹ " -ForegroundColor Blue -NoNewline
    Write-Host $Message
}

function Print-Success {
    param([string]$Message)
    Write-Host "✓ " -ForegroundColor Green -NoNewline
    Write-Host $Message
}

function Print-Warning {
    param([string]$Message)
    Write-Host "⚠ " -ForegroundColor Yellow -NoNewline
    Write-Host $Message
}

function Print-Error {
    param([string]$Message)
    Write-Host "✗ " -ForegroundColor Red -NoNewline
    Write-Host $Message
}

switch ($Command.ToLower()) {
    # Make-style commands
    "test" {
        Print-Info "Legacy 'make test' → Gradle testAll"
        & $GradleCmd testAll
        exit $LASTEXITCODE
    }
    "lint" {
        Print-Info "Legacy 'make lint' → Gradle lintAll"
        & $GradleCmd lintAll
        exit $LASTEXITCODE
    }
    "format" {
        Print-Info "Legacy 'make format' → Gradle formatAll"
        & $GradleCmd formatAll
        exit $LASTEXITCODE
    }
    "run" {
        Print-Info "Legacy 'make run' → Gradle pythonRun"
        & $GradleCmd pythonRun
        exit $LASTEXITCODE
    }
    "precommit" {
        Print-Info "Legacy 'make precommit' → Gradle check"
        & $GradleCmd check
        exit $LASTEXITCODE
    }
    
    # npm-style commands
    "npm:test" {
        Print-Info "Legacy 'npm test' → Gradle npmTest"
        & $GradleCmd npmTest
        exit $LASTEXITCODE
    }
    "npm:build" {
        Print-Info "Legacy 'npm run build' → Gradle npmBuild"
        & $GradleCmd npmBuild
        exit $LASTEXITCODE
    }
    "npm:dev" {
        Print-Info "Legacy 'npm run dev' → Gradle npmDev"
        & $GradleCmd npmDev
        exit $LASTEXITCODE
    }
    
    # Python-specific commands
    "py:test" {
        Print-Info "Legacy 'pytest' → Gradle pythonTest"
        & $GradleCmd pythonTest
        exit $LASTEXITCODE
    }
    "py:lint" {
        Print-Info "Legacy 'ruff check' → Gradle pythonLint"
        & $GradleCmd pythonLint
        exit $LASTEXITCODE
    }
    "py:format" {
        Print-Info "Legacy 'black src' → Gradle pythonFormat"
        & $GradleCmd pythonFormat
        exit $LASTEXITCODE
    }
    
    # Android commands
    "android:build" {
        Print-Info "Legacy Android build → Gradle androidBuild"
        & $GradleCmd androidBuild
        exit $LASTEXITCODE
    }
    "android:release" {
        Print-Info "Legacy Android release → Gradle androidBuildRelease"
        & $GradleCmd androidBuildRelease
        exit $LASTEXITCODE
    }
    
    # Desktop commands
    "desktop:build" {
        Print-Info "Legacy desktop build → Gradle desktopBuild"
        & $GradleCmd desktopBuild
        exit $LASTEXITCODE
    }
    "desktop:package" {
        Print-Info "Legacy desktop package → Gradle desktopPackageAll"
        & $GradleCmd desktopPackageAll
        exit $LASTEXITCODE
    }
    
    # Unified commands
    "clean" {
        Print-Info "Unified clean → Gradle clean"
        & $GradleCmd clean
        exit $LASTEXITCODE
    }
    "check" {
        Print-Info "Unified check → Gradle check"
        & $GradleCmd check
        exit $LASTEXITCODE
    }
    "build" {
        Print-Info "Unified build → Gradle buildAll"
        & $GradleCmd buildAll
        exit $LASTEXITCODE
    }
    "release" {
        Print-Info "Unified release → Gradle release"
        & $GradleCmd release
        exit $LASTEXITCODE
    }
    
    # Help
    { $_ -in "help", "--help", "-h", "-?" } {
        Write-Host @"
═══════════════════════════════════════════════════════════════════════════
THIRSTY'S GRADLE - BACKWARD COMPATIBILITY WRAPPER
═══════════════════════════════════════════════════════════════════════════

This wrapper provides backward compatibility with legacy build commands.

LEGACY COMMAND MAPPINGS:
────────────────────────────────────────────────────────────────────────────

Make-style commands:
  test          → gradlew testAll
  lint          → gradlew lintAll
  format        → gradlew formatAll
  run           → gradlew pythonRun
  precommit     → gradlew check

NPM-style commands:
  npm:test      → gradlew npmTest
  npm:build     → gradlew npmBuild
  npm:dev       → gradlew npmDev

Python commands:
  py:test       → gradlew pythonTest
  py:lint       → gradlew pythonLint
  py:format     → gradlew pythonFormat

Android commands:
  android:build → gradlew androidBuild
  android:release → gradlew androidBuildRelease

Desktop commands:
  desktop:build → gradlew desktopBuild
  desktop:package → gradlew desktopPackageAll

Unified commands:
  clean         → gradlew clean
  check         → gradlew check
  build         → gradlew buildAll
  release       → gradlew release

RECOMMENDED: Use Gradle directly for full control
────────────────────────────────────────────────────────────────────────────
  .\gradlew.bat godTierHelp    # Show all available commands
  .\gradlew.bat tasks --all    # List all tasks
  .\gradlew.bat <task>         # Run specific task

See GRADLE_BUILD_SYSTEM.md for comprehensive documentation.
═══════════════════════════════════════════════════════════════════════════
"@
    }
    
    default {
        Print-Error "Unknown command: $Command"
        Print-Info "Run '.\build-wrapper.ps1 help' for usage information"
        exit 1
    }
}

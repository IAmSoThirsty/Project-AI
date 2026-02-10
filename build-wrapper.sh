#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════════════
# THIRSTY'S GRADLE - BACKWARD COMPATIBILITY WRAPPER
# ═══════════════════════════════════════════════════════════════════════════
# 
# This script provides backward compatibility with legacy build commands
# by mapping them to the new Gradle build system.
# 
# Usage: ./build-wrapper.sh <command>
# 
# Legacy commands are automatically translated to Gradle equivalents.
# ═══════════════════════════════════════════════════════════════════════════

set -e

GRADLE_CMD="./gradlew"
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    GRADLE_CMD="gradlew.bat"
fi

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Parse command
COMMAND="${1:-help}"

case "$COMMAND" in
    # Make-style commands
    "test")
        print_info "Legacy 'make test' → Gradle testAll"
        exec $GRADLE_CMD testAll
        ;;
    "lint")
        print_info "Legacy 'make lint' → Gradle lintAll"
        exec $GRADLE_CMD lintAll
        ;;
    "format")
        print_info "Legacy 'make format' → Gradle formatAll"
        exec $GRADLE_CMD formatAll
        ;;
    "run")
        print_info "Legacy 'make run' → Gradle pythonRun"
        exec $GRADLE_CMD pythonRun
        ;;
    "precommit")
        print_info "Legacy 'make precommit' → Gradle check"
        exec $GRADLE_CMD check
        ;;
        
    # npm-style commands
    "npm:test")
        print_info "Legacy 'npm test' → Gradle npmTest"
        exec $GRADLE_CMD npmTest
        ;;
    "npm:build")
        print_info "Legacy 'npm run build' → Gradle npmBuild"
        exec $GRADLE_CMD npmBuild
        ;;
    "npm:dev")
        print_info "Legacy 'npm run dev' → Gradle npmDev"
        exec $GRADLE_CMD npmDev
        ;;
        
    # Python-specific commands
    "py:test")
        print_info "Legacy 'pytest' → Gradle pythonTest"
        exec $GRADLE_CMD pythonTest
        ;;
    "py:lint")
        print_info "Legacy 'ruff check' → Gradle pythonLint"
        exec $GRADLE_CMD pythonLint
        ;;
    "py:format")
        print_info "Legacy 'black src' → Gradle pythonFormat"
        exec $GRADLE_CMD pythonFormat
        ;;
        
    # Android commands
    "android:build")
        print_info "Legacy Android build → Gradle androidBuild"
        exec $GRADLE_CMD androidBuild
        ;;
    "android:release")
        print_info "Legacy Android release → Gradle androidBuildRelease"
        exec $GRADLE_CMD androidBuildRelease
        ;;
        
    # Desktop commands
    "desktop:build")
        print_info "Legacy desktop build → Gradle desktopBuild"
        exec $GRADLE_CMD desktopBuild
        ;;
    "desktop:package")
        print_info "Legacy desktop package → Gradle desktopPackageAll"
        exec $GRADLE_CMD desktopPackageAll
        ;;
        
    # Unified commands
    "clean")
        print_info "Unified clean → Gradle clean"
        exec $GRADLE_CMD clean
        ;;
    "check")
        print_info "Unified check → Gradle check"
        exec $GRADLE_CMD check
        ;;
    "build")
        print_info "Unified build → Gradle buildAll"
        exec $GRADLE_CMD buildAll
        ;;
    "release")
        print_info "Unified release → Gradle release"
        exec $GRADLE_CMD release
        ;;
        
    # Help
    "help"|"--help"|"-h")
        cat <<'EOF'
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
  ./gradlew godTierHelp    # Show all available commands
  ./gradlew tasks --all    # List all tasks
  ./gradlew <task>         # Run specific task

See GRADLE_BUILD_SYSTEM.md for comprehensive documentation.
═══════════════════════════════════════════════════════════════════════════
EOF
        ;;
        
    *)
        print_error "Unknown command: $COMMAND"
        print_info "Run './build-wrapper.sh help' for usage information"
        exit 1
        ;;
esac

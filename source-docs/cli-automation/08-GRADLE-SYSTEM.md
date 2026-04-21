---
title: Gradle Build System
type: technical-reference
audience: [developers, build-engineers]
classification: P0-Core
tags: [gradle, build-system, android, java]
created: 2024-01-20
status: current
---

# Gradle Build System

**Multi-module Java/Android build orchestration with Gradle.**

## Overview

Project-AI uses Gradle for Java and Android builds with multi-module support.

## Gradle Wrapper

Always use Gradle wrapper for consistent builds:
```bash
# Unix/Linux/macOS
./gradlew build

# Windows
.\gradlew.bat build
```

## Key Tasks

- uild - Build all modules
- 	est - Run all tests
- :legion_mini:assembleDebug - Build Android debug APK
- :legion_mini:assembleRelease - Build Android release APK
- clean - Clean build artifacts
- dependencies - Show dependency tree

## Build Configuration

Located in:
- uild.gradle - Root project configuration
- settings.gradle - Multi-module setup
- ndroid/legion_mini/build.gradle - Android app configuration

## Performance

- Enable build cache: org.gradle.caching=true
- Parallel execution: org.gradle.parallel=true
- Daemon mode: org.gradle.daemon=true

---

**AGENT-038: CLI & Automation Documentation Specialist**

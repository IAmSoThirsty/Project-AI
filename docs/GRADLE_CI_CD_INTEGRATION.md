# CI/CD Integration Guide for Thirsty's Gradle

## Overview

This guide explains how to integrate Thirsty's Gradle build system with CI/CD pipelines, focusing on GitHub Actions integration and optimization strategies.

## GitHub Actions Integration

### Basic Integration

Add to your GitHub Actions workflow:

```yaml
name: Build and Test
on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:

      - name: Checkout code

        uses: actions/checkout@v4

      - name: Set up JDK 17

        uses: actions/setup-java@v4
        with:
          distribution: 'temurin'
          java-version: '17'

      - name: Setup Gradle

        uses: gradle/gradle-build-action@v2
        with:
          cache-read-only: ${{ github.ref != 'refs/heads/main' }}

      - name: Run checks

        run: ./gradlew check

      - name: Build all modules

        run: ./gradlew buildAll

      - name: Upload artifacts

        uses: actions/upload-artifact@v4
        with:
          name: build-artifacts
          path: build/artifacts/
```

### Matrix Strategy for Multi-Platform Builds

```yaml
name: Multi-Platform Build
on: [push, pull_request]

jobs:
  build:
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]

    runs-on: ${{ matrix.os }}

    steps:

      - uses: actions/checkout@v4

      - name: Set up JDK 17

        uses: actions/setup-java@v4
        with:
          distribution: 'temurin'
          java-version: '17'

      - name: Setup Gradle

        uses: gradle/gradle-build-action@v2

      - name: Build and test

        run: ./gradlew check buildAll

      - name: Upload artifacts

        uses: actions/upload-artifact@v4
        with:
          name: artifacts-${{ matrix.os }}
          path: build/artifacts/
```

### Comprehensive CI Pipeline

```yaml
name: Comprehensive CI
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:

  # Job 1: Lint and format check

  lint:
    runs-on: ubuntu-latest
    steps:

      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4

        with:
          distribution: 'temurin'
          java-version: '17'

      - uses: gradle/gradle-build-action@v2
      - name: Run linters

        run: ./gradlew lintAll

  # Job 2: Security scanning

  security:
    runs-on: ubuntu-latest
    steps:

      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4

        with:
          distribution: 'temurin'
          java-version: '17'

      - uses: gradle/gradle-build-action@v2
      - name: Security scan

        run: ./gradlew securityScanAll

      - name: Generate SBOM

        run: ./gradlew sbomGenerate

      - name: Upload SBOM

        uses: actions/upload-artifact@v4
        with:
          name: sbom
          path: build/artifacts/sbom/

  # Job 3: Unit tests

  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        module: [python, desktop, android]
    steps:

      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4

        with:
          distribution: 'temurin'
          java-version: '17'

      - uses: gradle/gradle-build-action@v2
      - name: Run tests

        run: |
          case "${{ matrix.module }}" in
            python)
              ./gradlew pythonTest
              ;;
            desktop)
              ./gradlew npmTest
              ;;
            android)
              ./gradlew androidTest
              ;;
          esac

      - name: Upload test results

        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: test-results-${{ matrix.module }}
          path: build/reports/

  # Job 4: Build all modules

  build:
    needs: [lint, test]
    runs-on: ubuntu-latest
    steps:

      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4

        with:
          distribution: 'temurin'
          java-version: '17'

      - uses: gradle/gradle-build-action@v2
      - name: Build all modules

        run: ./gradlew buildAll

      - name: Upload build artifacts

        uses: actions/upload-artifact@v4
        with:
          name: build-artifacts
          path: build/artifacts/

  # Job 5: Documentation

  docs:
    runs-on: ubuntu-latest
    steps:

      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4

        with:
          distribution: 'temurin'
          java-version: '17'

      - uses: gradle/gradle-build-action@v2
      - name: Build documentation

        run: ./gradlew docsBuild

      - name: Deploy to GitHub Pages

        if: github.ref == 'refs/heads/main'
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./build/docs
```

### Release Pipeline

```yaml
name: Release
on:
  push:
    tags: ['v*']

jobs:
  release:
    runs-on: ubuntu-latest
    permissions:
      contents: write
      packages: write

    steps:

      - uses: actions/checkout@v4

        with:
          fetch-depth: 0

      - name: Set up JDK 17

        uses: actions/setup-java@v4
        with:
          distribution: 'temurin'
          java-version: '17'

      - name: Setup Gradle

        uses: gradle/gradle-build-action@v2

      - name: Extract version from tag

        id: version
        run: echo "VERSION=${GITHUB_REF#refs/tags/v}" >> $GITHUB_OUTPUT

      - name: Run full release pipeline

        run: ./gradlew release -PprojectVersion=${{ steps.version.outputs.VERSION }}
        env:
          CI: true

      - name: Create GitHub Release

        uses: softprops/action-gh-release@v1
        with:
          files: build/artifacts/release/${{ steps.version.outputs.VERSION }}/**/*
          generate_release_notes: true
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

      - name: Build and push Docker image

        run: |
          echo "${{ secrets.GITHUB_TOKEN }}" | docker login ghcr.io -u ${{ github.actor }} --password-stdin
          ./gradlew dockerBuild dockerPush -PprojectVersion=${{ steps.version.outputs.VERSION }}
        env:
          DOCKER_REGISTRY: ghcr.io/${{ github.repository_owner }}
```

## Optimization Strategies

### 1. Gradle Build Cache

Enable in CI:

```yaml

- name: Setup Gradle

  uses: gradle/gradle-build-action@v2
  with:

    # Cache build outputs between runs

    cache-read-only: false
```

### 2. Dependency Caching

```yaml

- name: Cache dependencies

  uses: actions/cache@v3
  with:
    path: |
      ~/.gradle/caches
      ~/.gradle/wrapper
      .gradle/nodejs
      .gradle/npm
      .venv
      node_modules
    key: ${{ runner.os }}-gradle-${{ hashFiles('**/*.gradle*', '**/gradle-wrapper.properties', 'requirements*.txt', 'package-lock.json') }}
    restore-keys: |
      ${{ runner.os }}-gradle-
```

### 3. Parallel Execution

```yaml

- name: Build with parallel execution

  run: ./gradlew buildAll --parallel --max-workers=4
```

### 4. Incremental Builds

```yaml

- name: Run checks (incremental)

  run: ./gradlew check --build-cache --parallel
```

### 5. Test Sharding

```yaml
test:
  strategy:
    matrix:
      shard: [1, 2, 3, 4]
  steps:

    - name: Run tests (shard ${{ matrix.shard }})

      run: ./gradlew pythonTest -Pshard=${{ matrix.shard }} -PtotalShards=4
```

## Environment Variables

Set in GitHub Actions:

```yaml
env:
  CI: true
  GRADLE_OPTS: -Dorg.gradle.daemon=false -Dorg.gradle.parallel=true
  JAVA_OPTS: -Xmx4g
  PYTHON_EXEC: python3
  NODE_VERSION: 20.11.0
```

## Secrets Management

Required secrets in GitHub:

```yaml
secrets:
  GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}          # Automatic
  ANDROID_KEYSTORE: ${{ secrets.ANDROID_KEYSTORE }}  # For Android signing
  ANDROID_KEY_PASSWORD: ${{ secrets.ANDROID_KEY_PASSWORD }}
  DOCKER_REGISTRY_TOKEN: ${{ secrets.DOCKER_REGISTRY_TOKEN }}
  SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}            # For SonarQube
```

## Advanced Features

### Conditional Execution

```yaml

- name: Build Android (only if Android files changed)

  if: contains(github.event.head_commit.modified, 'android/') || contains(github.event.head_commit.modified, 'app/')
  run: ./gradlew androidBuild
```

### Build Notifications

```yaml

- name: Notify on failure

  if: failure()
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    text: 'Build failed for ${{ github.repository }}'
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

### Artifact Retention

```yaml

- name: Upload artifacts with retention

  uses: actions/upload-artifact@v4
  with:
    name: build-artifacts
    path: build/artifacts/
    retention-days: 30
```

## Performance Benchmarks

Expected CI execution times:

| Task         | Duration  | Notes             |
| ------------ | --------- | ----------------- |
| `lintAll`    | 2-3 min   | All linters       |
| `pythonTest` | 3-5 min   | With coverage     |
| `buildAll`   | 5-8 min   | All modules       |
| `check`      | 8-12 min  | Full validation   |
| `release`    | 15-20 min | Complete pipeline |

With optimizations (cache, parallel):

| Task         | Duration  | Improvement |
| ------------ | --------- | ----------- |
| `lintAll`    | 1-2 min   | 50% faster  |
| `pythonTest` | 2-3 min   | 40% faster  |
| `buildAll`   | 3-5 min   | 40% faster  |
| `check`      | 5-8 min   | 35% faster  |
| `release`    | 10-15 min | 30% faster  |

## Troubleshooting

### Out of Memory

```yaml
env:
  GRADLE_OPTS: -Xmx6g -XX:MaxMetaspaceSize=1g
```

### Timeout Issues

```yaml

- name: Build with timeout

  run: ./gradlew buildAll
  timeout-minutes: 30
```

### Permission Issues

```yaml

- name: Make gradlew executable

  run: chmod +x gradlew
```

## Integration with Existing Workflows

The Gradle system integrates seamlessly with existing CI/CD:

```yaml

# Existing workflow

- name: Run Python tests (legacy)

  run: pytest

# Gradle equivalent

- name: Run Python tests (Gradle)

  run: ./gradlew pythonTest

# Both can coexist during migration

- name: Run tests (hybrid)

  run: |
    ./gradlew pythonTest || pytest
```

## Monitoring and Reporting

### Build Scan

Enable Gradle Build Scan:

```yaml

- name: Build with scan

  run: ./gradlew buildAll --scan
```

### Code Coverage

```yaml

- name: Upload coverage to Codecov

  uses: codecov/codecov-action@v3
  with:
    files: build/reports/pytest/coverage.xml
```

### SonarQube Integration

```yaml

- name: SonarQube analysis

  run: ./gradlew sonarqube
  env:
    SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
```

## Best Practices

1. **Use caching aggressively** - Gradle, npm, Python dependencies
1. **Parallelize independent jobs** - Lint, test, build in parallel
1. **Fail fast** - Run quick checks (lint) before slow builds
1. **Incremental builds** - Only rebuild what changed
1. **Matrix builds** - Test across platforms/versions
1. **Artifact management** - Keep build artifacts for debugging
1. **Build scans** - Enable for build performance insights
1. **Secrets management** - Use GitHub Secrets, never commit credentials
1. **Branch protection** - Require CI checks before merge
1. **Status badges** - Show build status in README

## Migration Checklist

- [ ] Set up JDK in CI environment
- [ ] Configure Gradle wrapper
- [ ] Enable Gradle build cache
- [ ] Set up dependency caching
- [ ] Configure parallel execution
- [ ] Add test result uploads
- [ ] Configure artifact retention
- [ ] Set up release automation
- [ ] Enable build notifications
- [ ] Add status badges to README
- [ ] Update branch protection rules
- [ ] Configure secrets for signing/publishing
- [ ] Test full pipeline on feature branch
- [ ] Validate release workflow
- [ ] Update documentation

______________________________________________________________________

**Last Updated**: 2024-01-08 **Gradle Version**: 8.5 **Build System Version**: 1.0.0

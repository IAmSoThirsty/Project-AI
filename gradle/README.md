<!--                                        [2026-03-04 14:24]  -->
<!--                                       Productivity: Active  -->

# `gradle/` — Gradle Wrapper

> **Gradle wrapper files for the JVM build system.** The wrapper ensures a consistent Gradle version across all environments.

## Files

| File | Purpose |
|---|---|
| `gradle-wrapper.jar` | Gradle wrapper bootstrap |
| `gradle-wrapper.properties` | Gradle version and distribution URL |

## Usage

```bash
./gradlew build
./gradlew test
./gradlew evolutionOverride
```

See `build.gradle.kts` for the full build configuration.

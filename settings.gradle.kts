/*
 * ═══════════════════════════════════════════════════════════════════════════
 * THIRSTY'S GRADLE - SETTINGS & MODULE DISCOVERY
 * ═══════════════════════════════════════════════════════════════════════════
 * 
 * Root settings for the monolithic God Tier build system
 * Automatically discovers and configures all project modules
 * 
 * Version: 1.0.0
 * ═══════════════════════════════════════════════════════════════════════════
 */

rootProject.name = "Project-AI"

// ═══════════════════════════════════════════════════════════════════════════
// PLUGIN MANAGEMENT
// ═══════════════════════════════════════════════════════════════════════════

pluginManagement {
    repositories {
        gradlePluginPortal()
        google()
        mavenCentral()
    }
    
    plugins {
        id("com.github.node-gradle.node") version "7.0.1"
        id("org.jetbrains.dokka") version "1.9.10"
        id("org.sonarqube") version "4.4.1.3373"
        id("org.cyclonedx.bom") version "1.8.2"
        id("net.researchgate.release") version "3.0.2"
    }
}

// ═══════════════════════════════════════════════════════════════════════════
// DEPENDENCY RESOLUTION MANAGEMENT
// ═══════════════════════════════════════════════════════════════════════════

dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.PREFER_PROJECT)
    
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
    
    // Version catalog is automatically loaded from gradle/libs.versions.toml
}

// ═══════════════════════════════════════════════════════════════════════════
// MODULE INCLUSION
// ═══════════════════════════════════════════════════════════════════════════

// Android modules
if (file("android/app/build.gradle").exists()) {
    include(":app")
    project(":app").projectDir = file("android/app")
}

// Additional subprojects can be auto-discovered here
// The build.gradle.kts handles module discovery for non-Gradle modules

// ═══════════════════════════════════════════════════════════════════════════
// BUILD CACHE CONFIGURATION
// ═══════════════════════════════════════════════════════════════════════════

buildCache {
    local {
        isEnabled = true
        directory = file("${rootProject.projectDir}/.gradle/build-cache")
        removeUnusedEntriesAfterDays = 30
    }
}

// ═══════════════════════════════════════════════════════════════════════════
// FEATURE PREVIEWS
// ═══════════════════════════════════════════════════════════════════════════

enableFeaturePreview("TYPESAFE_PROJECT_ACCESSORS")
enableFeaturePreview("STABLE_CONFIGURATION_CACHE")

// Status logging disabled for IDE compatibility
// println("═══════════════════════════════════════════════════════════════════════════")
// println("THIRSTY'S GRADLE SETTINGS - Monolithic Build System Initialized")
// println("Root Project: ${rootProject.name}")
// println("Build Cache: Enabled (30 day retention)")
// println("═══════════════════════════════════════════════════════════════════════════")

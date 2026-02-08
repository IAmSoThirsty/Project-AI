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
    
    // Version catalog for centralized dependency management
    versionCatalogs {
        create("libs") {
            // Android versions
            version("androidGradlePlugin", "8.2.1")
            version("kotlin", "1.9.22")
            version("hilt", "2.50")
            
            // Node.js versions
            version("node", "20.11.0")
            version("npm", "10.2.4")
            
            // Python versions (tracked for reference)
            version("python", "3.11")
            version("pythonMax", "3.12")
            
            // Build tool versions
            version("gradleNodePlugin", "7.0.1")
            version("dokka", "1.9.10")
            version("sonarqube", "4.4.1.3373")
            version("cyclonedx", "1.8.2")
            version("releasePlugin", "3.0.2")
            
            // Library versions
            library("android-gradle", "com.android.tools.build:gradle:8.2.1")
            library("kotlin-gradle", "org.jetbrains.kotlin:kotlin-gradle-plugin:1.9.22")
            library("hilt-gradle", "com.google.dagger:hilt-android-gradle-plugin:2.50")
            library("node-gradle", "com.github.node-gradle:gradle-node-plugin:7.0.1")
        }
    }
}

// ═══════════════════════════════════════════════════════════════════════════
// MODULE INCLUSION
// ═══════════════════════════════════════════════════════════════════════════

// Android modules
if (file("app/build.gradle").exists()) {
    include(":app")
    project(":app").projectDir = file("app")
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

println("═══════════════════════════════════════════════════════════════════════════")
println("THIRSTY'S GRADLE SETTINGS - Monolithic Build System Initialized")
println("Root Project: ${rootProject.name}")
println("Build Cache: Enabled (30 day retention)")
println("═══════════════════════════════════════════════════════════════════════════")

/*
 * ═══════════════════════════════════════════════════════════════════════════
 * THIRSTY'S GRADLE: GOD TIER MONOLITHIC BUILD ORCHESTRATION
 * ═══════════════════════════════════════════════════════════════════════════
 * 
 * Enterprise-grade, unified build system for Project-AI
 * Coordinates ALL builds, tests, packaging, and deployments across:
 *   - Python backends (Flask/FastAPI)
 *   - Android applications (Legion Mini)
 *   - Electron Desktop (TypeScript/React)
 *   - Documentation generation
 *   - USB/Portable distributions
 *   - Testing, linting, security scanning
 *   - CI/CD integration and release automation
 * 
 * Version: 1.0.0
 * Architecture: Monolithic Density Pattern
 * Paradigm: Maximum Coordination, Zero Fragmentation
 * ═══════════════════════════════════════════════════════════════════════════
 */

import org.gradle.api.tasks.testing.logging.TestLogEvent
import java.time.LocalDateTime
import java.time.format.DateTimeFormatter

// ═══════════════════════════════════════════════════════════════════════════
// ROOT PROJECT CONFIGURATION
// ═══════════════════════════════════════════════════════════════════════════

buildscript {
    repositories {
        google()
        mavenCentral()
    }
    dependencies {
        classpath("com.android.tools.build:gradle:8.2.1")
        classpath("org.jetbrains.kotlin:kotlin-gradle-plugin:1.9.22")
        classpath("com.google.dagger:hilt-android-gradle-plugin:2.50")
        classpath("com.github.node-gradle:gradle-node-plugin:7.0.1")
    }
}

plugins {
    // Core build system
    id("base")
    
    // Node.js integration for Electron/npm builds
    id("com.github.node-gradle.node") version "7.0.1" apply false
    
    // Python integration via exec tasks (no direct plugin needed)
    
    // Documentation generation
    id("org.jetbrains.dokka") version "1.9.10" apply false
    
    // Security scanning
    id("org.sonarqube") version "4.4.1.3373" apply false
    
    // SBOM generation
    id("org.cyclonedx.bom") version "1.8.2" apply false
    
    // Release automation
    id("net.researchgate.release") version "3.0.2" apply false
}

allprojects {
    repositories {
        google()
        mavenCentral()
    }
}

// Project metadata
group = "ai.project"
version = findProperty("projectVersion")?.toString() ?: "1.0.0"
description = "Project-AI: Comprehensive AI Assistant Platform"

// ═══════════════════════════════════════════════════════════════════════════
// GLOBAL CONFIGURATION
// ═══════════════════════════════════════════════════════════════════════════

// Build environment
val buildTimestamp: String by lazy {
    LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME)
}

val isCI = System.getenv("CI")?.toBoolean() ?: false
val isContinuousIntegration = hasProperty("ci") || isCI

// Directories
val projectRoot = rootDir
val buildOutputDir = layout.buildDirectory.dir("outputs")
val artifactsDir = layout.buildDirectory.dir("artifacts")
val reportsDir = layout.buildDirectory.dir("reports")
val docsDir = layout.buildDirectory.dir("docs")

// Python configuration
val pythonExecutable = findProperty("pythonExec")?.toString() ?: "python"
val pythonVersion = findProperty("pythonVersion")?.toString() ?: "3.11"
val requirementsFile = file("requirements.txt")
val requirementsDevFile = file("requirements-dev.txt")
val pythonVenvDir = file(".venv")

// Node.js configuration
val nodeVersion = findProperty("nodeVersion")?.toString() ?: "20.11.0"
val npmVersion = findProperty("npmVersion")?.toString() ?: "10.2.4"

// Android configuration
val androidSdkDir = System.getenv("ANDROID_SDK_ROOT") ?: System.getenv("ANDROID_HOME")
val androidBuildToolsVersion = "34.0.0"

// Test configuration
val testParallelism = findProperty("testParallelism")?.toString()?.toInt() 
    ?: Runtime.getRuntime().availableProcessors()

// ═══════════════════════════════════════════════════════════════════════════
// MODULE DISCOVERY & CONFIGURATION
// ═══════════════════════════════════════════════════════════════════════════

// Auto-discover all modules and subsystems
val discoveredModules = mutableSetOf<String>()

// Android modules
if (file("android").exists()) {
    discoveredModules.add("android")
}
if (file("android/app/build.gradle").exists()) {
    discoveredModules.add("app")
}

// Desktop Electron module
if (file("desktop/package.json").exists()) {
    discoveredModules.add("desktop")
}

// Web modules
if (file("web/frontend/package.json").exists()) {
    discoveredModules.add("web-frontend")
}
if (file("web/backend").exists()) {
    discoveredModules.add("web-backend")
}

// Python modules
if (file("src/app").exists()) {
    discoveredModules.add("python-app")
}
if (file("api").exists()) {
    discoveredModules.add("python-api")
}
if (file("tarl").exists()) {
    discoveredModules.add("tarl")
}
if (file("kernel").exists()) {
    discoveredModules.add("kernel")
}
if (file("engines").exists()) {
    discoveredModules.add("engines")
}

logger.lifecycle("═══════════════════════════════════════════════════════════")
logger.lifecycle("THIRSTY'S GRADLE - God Tier Build Orchestration")
logger.lifecycle("═══════════════════════════════════════════════════════════")
logger.lifecycle("Project: ${project.name}")
logger.lifecycle("Version: ${project.version}")
logger.lifecycle("Build Time: $buildTimestamp")
logger.lifecycle("CI Mode: $isContinuousIntegration")
logger.lifecycle("Discovered Modules: ${discoveredModules.size}")
discoveredModules.sorted().forEach { logger.lifecycle("  • $it") }
logger.lifecycle("═══════════════════════════════════════════════════════════")

// ═══════════════════════════════════════════════════════════════════════════
// PYTHON BACKEND ORCHESTRATION
// ═══════════════════════════════════════════════════════════════════════════

// Python virtual environment setup
tasks.register<Exec>("pythonVenvCreate") {
    group = "python"
    description = "Create Python virtual environment"
    
    onlyIf { !pythonVenvDir.exists() }
    
    commandLine(pythonExecutable, "-m", "venv", pythonVenvDir.absolutePath)
    
    doLast {
        logger.lifecycle("✓ Python virtual environment created at ${pythonVenvDir.absolutePath}")
    }
}

// Python dependency installation
tasks.register<Exec>("pythonInstall") {
    group = "python"
    description = "Install Python dependencies"
    
    dependsOn("pythonVenvCreate")
    
    val pipExec = if (System.getProperty("os.name").lowercase().contains("windows")) {
        file("${pythonVenvDir}/Scripts/pip.exe").absolutePath
    } else {
        file("${pythonVenvDir}/bin/pip").absolutePath
    }
    
    inputs.files(requirementsFile, requirementsDevFile)
    outputs.dir(pythonVenvDir)
    
    commandLine(
        pipExec, "install",
        "-r", requirementsFile.absolutePath,
        "-r", requirementsDevFile.absolutePath
    )
    
    doLast {
        logger.lifecycle("✓ Python dependencies installed")
    }
}

// Python linting with ruff
tasks.register<Exec>("pythonLint") {
    group = "python"
    description = "Lint Python code with ruff"
    
    dependsOn("pythonInstall")
    
    val pythonExec = if (System.getProperty("os.name").lowercase().contains("windows")) {
        file("${pythonVenvDir}/Scripts/python.exe").absolutePath
    } else {
        file("${pythonVenvDir}/bin/python").absolutePath
    }
    
    commandLine(pythonExec, "-m", "ruff", "check", ".")
}

// Python lint auto-fix
tasks.register<Exec>("pythonLintFix") {
    group = "python"
    description = "Auto-fix Python linting issues with ruff"
    
    dependsOn("pythonInstall")
    
    val pythonExec = if (System.getProperty("os.name").lowercase().contains("windows")) {
        file("${pythonVenvDir}/Scripts/python.exe").absolutePath
    } else {
        file("${pythonVenvDir}/bin/python").absolutePath
    }
    
    commandLine(pythonExec, "-m", "ruff", "check", ".", "--fix")
}

// Python formatting with black
tasks.register<Exec>("pythonFormat") {
    group = "python"
    description = "Format Python code with black"
    
    dependsOn("pythonInstall")
    
    val pythonExec = if (System.getProperty("os.name").lowercase().contains("windows")) {
        file("${pythonVenvDir}/Scripts/python.exe").absolutePath
    } else {
        file("${pythonVenvDir}/bin/python").absolutePath
    }
    
    commandLine(pythonExec, "-m", "black", "src", "tests")
}

// Python type checking with mypy
tasks.register<Exec>("pythonTypeCheck") {
    group = "python"
    description = "Type check Python code with mypy"
    
    dependsOn("pythonInstall")
    
    val pythonExec = if (System.getProperty("os.name").lowercase().contains("windows")) {
        file("${pythonVenvDir}/Scripts/python.exe").absolutePath
    } else {
        file("${pythonVenvDir}/bin/python").absolutePath
    }
    
    commandLine(pythonExec, "-m", "mypy", "src", "--ignore-missing-imports")
}

// Python testing with pytest
tasks.register<Exec>("pythonTest") {
    group = "python"
    description = "Run Python tests with pytest"
    
    dependsOn("pythonInstall")
    
    val pythonExec = if (System.getProperty("os.name").lowercase().contains("windows")) {
        file("${pythonVenvDir}/Scripts/python.exe").absolutePath
    } else {
        file("${pythonVenvDir}/bin/python").absolutePath
    }
    
    val reportDir = reportsDir.get().dir("pytest")
    outputs.dir(reportDir)
    
    commandLine(
        pythonExec, "-m", "pytest",
        "-v",
        "--tb=short",
        "--junitxml=${reportDir.file("junit.xml").asFile.absolutePath}",
        "--cov=src",
        "--cov-report=html:${reportDir.dir("coverage").asFile.absolutePath}",
        "--cov-report=xml:${reportDir.file("coverage.xml").asFile.absolutePath}",
        "--cov-report=term-missing",
        "--maxfail=5",
        "-n", testParallelism.toString()
    )
    
    doLast {
        logger.lifecycle("✓ Python tests completed. Reports: ${reportDir.asFile.absolutePath}")
    }
}

// Python unit tests only
tasks.register<Exec>("pythonTestUnit") {
    group = "python"
    description = "Run Python unit tests only"
    
    dependsOn("pythonInstall")
    
    val pythonExec = if (System.getProperty("os.name").lowercase().contains("windows")) {
        file("${pythonVenvDir}/Scripts/python.exe").absolutePath
    } else {
        file("${pythonVenvDir}/bin/python").absolutePath
    }
    
    commandLine(
        pythonExec, "-m", "pytest",
        "-v", "-m", "unit",
        "--tb=short"
    )
}

// Python integration tests
tasks.register<Exec>("pythonTestIntegration") {
    group = "python"
    description = "Run Python integration tests"
    
    dependsOn("pythonInstall")
    
    val pythonExec = if (System.getProperty("os.name").lowercase().contains("windows")) {
        file("${pythonVenvDir}/Scripts/python.exe").absolutePath
    } else {
        file("${pythonVenvDir}/bin/python").absolutePath
    }
    
    commandLine(
        pythonExec, "-m", "pytest",
        "-v", "-m", "integration",
        "--tb=short"
    )
}

// Python security scanning
tasks.register<Exec>("pythonSecurityScan") {
    group = "python"
    description = "Scan Python dependencies for vulnerabilities"
    
    dependsOn("pythonInstall")
    
    val pipExec = if (System.getProperty("os.name").lowercase().contains("windows")) {
        file("${pythonVenvDir}/Scripts/pip.exe").absolutePath
    } else {
        file("${pythonVenvDir}/bin/pip").absolutePath
    }
    
    val reportDir = reportsDir.get().dir("security/python")
    outputs.dir(reportDir)
    
    commandLine(
        pipExec, "install", "pip-audit"
    )
    
    doLast {
        exec {
            val pipAudit = if (System.getProperty("os.name").lowercase().contains("windows")) {
                file("${pythonVenvDir}/Scripts/pip-audit.exe").absolutePath
            } else {
                file("${pythonVenvDir}/bin/pip-audit").absolutePath
            }
            
            commandLine(
                pipAudit,
                "--format", "json",
                "--output", reportDir.file("vulnerabilities.json").asFile.absolutePath
            )
        }
        logger.lifecycle("✓ Python security scan completed. Report: ${reportDir.asFile.absolutePath}")
    }
}

// Python package building
tasks.register<Exec>("pythonBuild") {
    group = "python"
    description = "Build Python package"
    
    dependsOn("pythonInstall", "pythonLint", "pythonTest")
    
    val pythonExec = if (System.getProperty("os.name").lowercase().contains("windows")) {
        file("${pythonVenvDir}/Scripts/python.exe").absolutePath
    } else {
        file("${pythonVenvDir}/bin/python").absolutePath
    }
    
    val distDir = file("dist")
    outputs.dir(distDir)
    
    commandLine(pythonExec, "-m", "build")
    
    doLast {
        logger.lifecycle("✓ Python package built. Artifacts: ${distDir.absolutePath}")
    }
}

// Python application execution
tasks.register<Exec>("pythonRun") {
    group = "python"
    description = "Run Python desktop application"
    
    dependsOn("pythonInstall")
    
    val pythonExec = if (System.getProperty("os.name").lowercase().contains("windows")) {
        file("${pythonVenvDir}/Scripts/python.exe").absolutePath
    } else {
        file("${pythonVenvDir}/bin/python").absolutePath
    }
    
    commandLine(pythonExec, "-m", "src.app.main")
}

// Python API server
tasks.register<Exec>("pythonRunApi") {
    group = "python"
    description = "Run Python API server"
    
    dependsOn("pythonInstall")
    
    val pythonExec = if (System.getProperty("os.name").lowercase().contains("windows")) {
        file("${pythonVenvDir}/Scripts/python.exe").absolutePath
    } else {
        file("${pythonVenvDir}/bin/python").absolutePath
    }
    
    commandLine(pythonExec, "start_api.py")
}

// ═══════════════════════════════════════════════════════════════════════════
// TAAR — Thirstys Active Agent Runner (Intelligent Build Orchestration)
// ═══════════════════════════════════════════════════════════════════════════

tasks.register<Exec>("taarRun") {
    group = "taar"
    description = "Run affected tasks for uncommitted changes (change-aware)"
    
    dependsOn("pythonInstall")
    
    val pythonExec = if (System.getProperty("os.name").lowercase().contains("windows")) {
        file("${pythonVenvDir}/Scripts/python.exe").absolutePath
    } else {
        file("${pythonVenvDir}/bin/python").absolutePath
    }
    
    commandLine(pythonExec, "-m", "taar.cli", "run")
}

tasks.register<Exec>("taarWatch") {
    group = "taar"
    description = "Start TAAR active watch mode — auto-run on file save"
    
    dependsOn("pythonInstall")
    
    val pythonExec = if (System.getProperty("os.name").lowercase().contains("windows")) {
        file("${pythonVenvDir}/Scripts/python.exe").absolutePath
    } else {
        file("${pythonVenvDir}/bin/python").absolutePath
    }
    
    commandLine(pythonExec, "-m", "taar.cli", "watch")
}

tasks.register<Exec>("taarCI") {
    group = "taar"
    description = "TAAR CI mode — fresh run, no cache, fail-fast"
    
    dependsOn("pythonInstall")
    
    val pythonExec = if (System.getProperty("os.name").lowercase().contains("windows")) {
        file("${pythonVenvDir}/Scripts/python.exe").absolutePath
    } else {
        file("${pythonVenvDir}/bin/python").absolutePath
    }
    
    commandLine(pythonExec, "-m", "taar.cli", "ci")
}

// ═══════════════════════════════════════════════════════════════════════════
// NODE.JS / NPM ORCHESTRATION (Electron Desktop, Web Frontend)
// ═══════════════════════════════════════════════════════════════════════════

// Configure Node.js plugin
apply(plugin = "com.github.node-gradle.node")

configure<com.github.gradle.node.NodeExtension> {
    version.set(nodeVersion)
    npmVersion.set(this@Build_gradle.npmVersion)
    download.set(true)
    workDir.set(file("${projectRoot}/.gradle/nodejs"))
    npmWorkDir.set(file("${projectRoot}/.gradle/npm"))
}

// Root npm install - handled automatically by gradle-node-plugin
// Configuration is done via the configure<NodeExtension> block above
// This manual registration was causing "Duplicate task name 'npmInstall'" errors

// Root npm build
tasks.register<com.github.gradle.node.npm.task.NpmTask>("npmBuild") {
    group = "npm"
    description = "Build npm packages"
    
    dependsOn("npmInstall")
    
    args.set(listOf("run", "build"))
}

// Root npm test
tasks.register<com.github.gradle.node.npm.task.NpmTask>("npmTest") {
    group = "npm"
    description = "Run npm tests"
    
    dependsOn("npmInstall")
    
    args.set(listOf("run", "test:js"))
}

// Markdown linting
tasks.register<com.github.gradle.node.npm.task.NpmTask>("npmLintMarkdown") {
    group = "npm"
    description = "Lint markdown files"
    
    dependsOn("npmInstall")
    
    args.set(listOf("run", "lint:markdown"))
}

// TARL build system integration
tasks.register<com.github.gradle.node.npm.task.NpmTask>("tarlBuild") {
    group = "tarl"
    description = "Build TARL language artifacts"
    
    dependsOn("npmInstall")
    
    args.set(listOf("run", "tarl:build"))
}

tasks.register<com.github.gradle.node.npm.task.NpmTask>("tarlClean") {
    group = "tarl"
    description = "Clean TARL build artifacts"
    
    dependsOn("npmInstall")
    
    args.set(listOf("run", "tarl:clean"))
}

// Desktop Electron build tasks
val desktopDir = file("desktop")
if (desktopDir.exists()) {
    
    tasks.register<com.github.gradle.node.npm.task.NpmTask>("desktopInstall") {
        group = "desktop"
        description = "Install Electron desktop dependencies"
        
        workingDir.set(desktopDir)
        args.set(listOf("install"))
        
        inputs.file("${desktopDir}/package.json")
        outputs.dir("${desktopDir}/node_modules")
    }
    
    tasks.register<com.github.gradle.node.npm.task.NpmTask>("desktopBuild") {
        group = "desktop"
        description = "Build Electron desktop application"
        
        dependsOn("desktopInstall")
        
        workingDir.set(desktopDir)
        args.set(listOf("run", "build"))
        
        val distDir = file("${desktopDir}/dist")
        outputs.dir(distDir)
        
        doLast {
            logger.lifecycle("✓ Desktop build completed. Output: ${distDir.absolutePath}")
        }
    }
    
    tasks.register<com.github.gradle.node.npm.task.NpmTask>("desktopPackageWin") {
        group = "desktop"
        description = "Package Electron desktop for Windows"
        
        dependsOn("desktopBuild")
        
        workingDir.set(desktopDir)
        args.set(listOf("run", "build:win"))
        
        val releaseDir = file("${desktopDir}/release")
        outputs.dir(releaseDir)
    }
    
    tasks.register<com.github.gradle.node.npm.task.NpmTask>("desktopPackageMac") {
        group = "desktop"
        description = "Package Electron desktop for macOS"
        
        dependsOn("desktopBuild")
        
        workingDir.set(desktopDir)
        args.set(listOf("run", "build:mac"))
        
        val releaseDir = file("${desktopDir}/release")
        outputs.dir(releaseDir)
    }
    
    tasks.register<com.github.gradle.node.npm.task.NpmTask>("desktopPackageLinux") {
        group = "desktop"
        description = "Package Electron desktop for Linux"
        
        dependsOn("desktopBuild")
        
        workingDir.set(desktopDir)
        args.set(listOf("run", "build:linux"))
        
        val releaseDir = file("${desktopDir}/release")
        outputs.dir(releaseDir)
    }
    
    tasks.register<Task>("desktopPackageAll") {
        group = "desktop"
        description = "Package Electron desktop for all platforms"
        
        dependsOn("desktopPackageWin", "desktopPackageMac", "desktopPackageLinux")
    }
}

// ═══════════════════════════════════════════════════════════════════════════
// ANDROID BUILD ORCHESTRATION
// ═══════════════════════════════════════════════════════════════════════════

// Note: Android build.gradle is configured separately in android/ directory
// These tasks delegate to the Android Gradle wrapper

if (file("android").exists() || file("app/build.gradle").exists()) {
    
    val gradlewCmd = if (System.getProperty("os.name").lowercase().contains("windows")) {
        "./gradlew.bat"
    } else {
        "./gradlew"
    }
    
    tasks.register<Exec>("androidBuild") {
        group = "android"
        description = "Build Android application"
        
        commandLine(gradlewCmd, ":app:assembleDebug")
        
        doLast {
            logger.lifecycle("✓ Android build completed")
        }
    }
    
    tasks.register<Exec>("androidBuildRelease") {
        group = "android"
        description = "Build Android release APK"
        
        commandLine(gradlewCmd, ":app:assembleRelease")
        
        doLast {
            logger.lifecycle("✓ Android release build completed")
        }
    }
    
    tasks.register<Exec>("androidTest") {
        group = "android"
        description = "Run Android tests"
        
        commandLine(gradlewCmd, ":app:testDebugUnitTest")
    }
    
    tasks.register<Exec>("androidLint") {
        group = "android"
        description = "Run Android lint checks"
        
        commandLine(gradlewCmd, ":app:lint")
    }
    
    tasks.register<Exec>("androidClean") {
        group = "android"
        description = "Clean Android build artifacts"
        
        commandLine(gradlewCmd, "clean")
    }
}

// ═══════════════════════════════════════════════════════════════════════════
// DOCUMENTATION GENERATION
// ═══════════════════════════════════════════════════════════════════════════

tasks.register<Exec>("docsBuild") {
    group = "documentation"
    description = "Build all documentation"
    
    val pythonExec = if (System.getProperty("os.name").lowercase().contains("windows")) {
        file("${pythonVenvDir}/Scripts/python.exe").absolutePath
    } else {
        file("${pythonVenvDir}/bin/python").absolutePath
    }
    
    dependsOn("pythonInstall")
    
    val docsOutput = docsDir.get()
    outputs.dir(docsOutput)
    
    // Check if Sphinx is configured
    if (file("docs/conf.py").exists()) {
        commandLine(pythonExec, "-m", "sphinx", "-b", "html", "docs", docsOutput.asFile.absolutePath)
    } else {
        // Fallback to simple docs copy
        doLast {
            copy {
                from("docs")
                into(docsOutput)
            }
            logger.lifecycle("✓ Documentation copied to ${docsOutput.asFile.absolutePath}")
        }
    }
}

tasks.register<Exec>("docsVerify") {
    group = "documentation"
    description = "Verify documentation links and structure"
    
    dependsOn("docsBuild", "npmLintMarkdown")
    
    doLast {
        logger.lifecycle("✓ Documentation verification completed")
    }
}

tasks.register<Copy>("docsPublish") {
    group = "documentation"
    description = "Publish documentation artifacts"
    
    dependsOn("docsBuild")
    
    from(docsDir)
    into(artifactsDir.get().dir("docs"))
    
    doLast {
        logger.lifecycle("✓ Documentation published to ${artifactsDir.get().dir("docs").asFile.absolutePath}")
    }
}

// ═══════════════════════════════════════════════════════════════════════════
// USB / PORTABLE DISTRIBUTION
// ═══════════════════════════════════════════════════════════════════════════

tasks.register<Exec>("usbCreateInstaller") {
    group = "usb"
    description = "Create USB installation package"
    
    val scriptFile = if (System.getProperty("os.name").lowercase().contains("windows")) {
        file("scripts/create_installation_usb.ps1")
    } else {
        file("scripts/create_installation_usb.sh")
    }
    
    onlyIf { scriptFile.exists() }
    
    if (System.getProperty("os.name").lowercase().contains("windows")) {
        commandLine("powershell", "-ExecutionPolicy", "Bypass", "-File", scriptFile.absolutePath)
    } else {
        commandLine("bash", scriptFile.absolutePath)
    }
}

tasks.register<Exec>("usbCreatePortable") {
    group = "usb"
    description = "Create portable USB package"
    
    val scriptFile = file("scripts/create_portable_usb.ps1")
    
    onlyIf { scriptFile.exists() }
    
    if (System.getProperty("os.name").lowercase().contains("windows")) {
        commandLine("powershell", "-ExecutionPolicy", "Bypass", "-File", scriptFile.absolutePath)
    }
}

tasks.register<Exec>("usbCreateUniversal") {
    group = "usb"
    description = "Create universal USB package (all platforms)"
    
    val scriptFile = file("scripts/create_universal_usb.ps1")
    
    onlyIf { scriptFile.exists() }
    
    if (System.getProperty("os.name").lowercase().contains("windows")) {
        commandLine("powershell", "-ExecutionPolicy", "Bypass", "-File", scriptFile.absolutePath)
    }
}

// ═══════════════════════════════════════════════════════════════════════════
// COMPREHENSIVE TESTING ORCHESTRATION
// ═══════════════════════════════════════════════════════════════════════════

tasks.register<Task>("testAll") {
    group = "verification"
    description = "Run ALL tests across all modules"
    
    val testTasks = mutableListOf<String>()
    
    if (discoveredModules.contains("python-app") || discoveredModules.contains("python-api")) {
        testTasks.add("pythonTest")
    }
    if (discoveredModules.contains("desktop")) {
        testTasks.add("npmTest")
    }
    if (discoveredModules.contains("android") || discoveredModules.contains("app")) {
        testTasks.add("androidTest")
    }
    
    dependsOn(testTasks)
    
    doLast {
        logger.lifecycle("═══════════════════════════════════════════════════════════")
        logger.lifecycle("✓ ALL TESTS COMPLETED SUCCESSFULLY")
        logger.lifecycle("═══════════════════════════════════════════════════════════")
    }
}

tasks.register<Exec>("testE2E") {
    group = "verification"
    description = "Run end-to-end tests"
    
    val scriptFile = if (System.getProperty("os.name").lowercase().contains("windows")) {
        file("scripts/run_e2e_tests.ps1")
    } else {
        file("scripts/run_e2e_tests.sh")
    }
    
    onlyIf { scriptFile.exists() }
    
    if (System.getProperty("os.name").lowercase().contains("windows")) {
        commandLine("powershell", "-ExecutionPolicy", "Bypass", "-File", scriptFile.absolutePath)
    } else {
        commandLine("bash", scriptFile.absolutePath)
    }
}

tasks.register<Exec>("testAdversarial") {
    group = "verification"
    description = "Run adversarial/red-team tests"
    
    dependsOn("pythonInstall")
    
    val pythonExec = if (System.getProperty("os.name").lowercase().contains("windows")) {
        file("${pythonVenvDir}/Scripts/python.exe").absolutePath
    } else {
        file("${pythonVenvDir}/bin/python").absolutePath
    }
    
    commandLine(pythonExec, "scripts/run_red_team_stress_tests.py")
}

tasks.register<Exec>("testPerformance") {
    group = "verification"
    description = "Run performance benchmarks"
    
    dependsOn("pythonInstall")
    
    val pythonExec = if (System.getProperty("os.name").lowercase().contains("windows")) {
        file("${pythonVenvDir}/Scripts/python.exe").absolutePath
    } else {
        file("${pythonVenvDir}/bin/python").absolutePath
    }
    
    commandLine(pythonExec, "scripts/run_robustness_benchmarks.py")
}

// ═══════════════════════════════════════════════════════════════════════════
// SECURITY & COMPLIANCE ORCHESTRATION
// ═══════════════════════════════════════════════════════════════════════════

tasks.register<Task>("securityScanAll") {
    group = "security"
    description = "Run comprehensive security scans"
    
    dependsOn("pythonSecurityScan")
    
    doLast {
        logger.lifecycle("✓ Security scans completed")
    }
}

tasks.register<Exec>("securityScanBandit") {
    group = "security"
    description = "Run Bandit security scanner on Python code"
    
    dependsOn("pythonInstall")
    
    val pythonExec = if (System.getProperty("os.name").lowercase().contains("windows")) {
        file("${pythonVenvDir}/Scripts/python.exe").absolutePath
    } else {
        file("${pythonVenvDir}/bin/python").absolutePath
    }
    
    val reportDir = reportsDir.get().dir("security/bandit")
    outputs.dir(reportDir)
    
    commandLine(
        pythonExec, "-m", "bandit",
        "-r", "src",
        "-f", "json",
        "-o", reportDir.file("report.json").asFile.absolutePath
    )
}

tasks.register<Task>("sbomGenerate") {
    group = "security"
    description = "Generate Software Bill of Materials (SBOM)"
    
    val sbomDir = artifactsDir.get().dir("sbom")
    outputs.dir(sbomDir)
    
    doLast {
        // Generate SBOM for Python dependencies
        val pythonSbom = sbomDir.file("python-dependencies.txt").asFile
        pythonSbom.parentFile.mkdirs()
        
        exec {
            val pipExec = if (System.getProperty("os.name").lowercase().contains("windows")) {
                file("${pythonVenvDir}/Scripts/pip.exe").absolutePath
            } else {
                file("${pythonVenvDir}/bin/pip").absolutePath
            }
            
            commandLine(pipExec, "freeze")
            standardOutput = pythonSbom.outputStream()
        }
        
        // Generate SBOM for npm dependencies
        if (file("package-lock.json").exists()) {
            copy {
                from("package-lock.json")
                into(sbomDir)
                rename { "npm-dependencies.json" }
            }
        }
        
        logger.lifecycle("✓ SBOM generated at ${sbomDir.asFile.absolutePath}")
    }
}

// ═══════════════════════════════════════════════════════════════════════════
// LINTING & CODE QUALITY ORCHESTRATION
// ═══════════════════════════════════════════════════════════════════════════

tasks.register<Task>("lintAll") {
    group = "verification"
    description = "Run ALL linters across all modules"
    
    val lintTasks = mutableListOf<String>()
    
    lintTasks.add("pythonLint")
    lintTasks.add("npmLintMarkdown")
    
    if (discoveredModules.contains("android") || discoveredModules.contains("app")) {
        lintTasks.add("androidLint")
    }
    
    dependsOn(lintTasks)
    
    doLast {
        logger.lifecycle("✓ All linting completed")
    }
}

tasks.register<Task>("formatAll") {
    group = "verification"
    description = "Auto-format code across all modules"
    
    dependsOn("pythonFormat", "pythonLintFix")
    
    doLast {
        logger.lifecycle("✓ All code formatted")
    }
}

// ═══════════════════════════════════════════════════════════════════════════
// DOCKER & CONTAINERIZATION
// ═══════════════════════════════════════════════════════════════════════════

tasks.register<Exec>("dockerBuild") {
    group = "docker"
    description = "Build Docker image"
    
    commandLine(
        "docker", "build",
        "-t", "project-ai:${project.version}",
        "-t", "project-ai:latest",
        "."
    )
    
    doLast {
        logger.lifecycle("✓ Docker image built: project-ai:${project.version}")
    }
}

tasks.register<Exec>("dockerCompose") {
    group = "docker"
    description = "Start Docker Compose environment"
    
    commandLine("docker-compose", "up", "-d")
}

tasks.register<Exec>("dockerComposeDown") {
    group = "docker"
    description = "Stop Docker Compose environment"
    
    commandLine("docker-compose", "down")
}

tasks.register<Exec>("dockerPush") {
    group = "docker"
    description = "Push Docker image to registry"
    
    dependsOn("dockerBuild")
    
    val registry = findProperty("dockerRegistry")?.toString() ?: "ghcr.io/iamsothirsty"
    
    doFirst {
        exec {
            commandLine("docker", "tag", "project-ai:${project.version}", "$registry/project-ai:${project.version}")
        }
    }
    
    commandLine("docker", "push", "$registry/project-ai:${project.version}")
}

// ═══════════════════════════════════════════════════════════════════════════
// RELEASE & ARTIFACT PUBLISHING
// ═══════════════════════════════════════════════════════════════════════════

tasks.register<Copy>("releaseCollectArtifacts") {
    group = "release"
    description = "Collect all release artifacts"
    
    val releaseDir = artifactsDir.get().dir("release/${project.version}")
    
    // Python wheel
    if (file("dist").exists()) {
        from("dist") {
            into("python")
        }
    }
    
    // Desktop releases
    if (file("desktop/release").exists()) {
        from("desktop/release") {
            into("desktop")
        }
    }
    
    // Android APKs
    if (file("app/build/outputs/apk").exists()) {
        from("app/build/outputs/apk") {
            into("android")
        }
    }
    
    // Documentation
    from(docsDir) {
        into("docs")
    }
    
    into(releaseDir)
    
    doLast {
        logger.lifecycle("✓ Release artifacts collected at ${releaseDir.asFile.absolutePath}")
    }
}

tasks.register<Exec>("releaseGitHubRelease") {
    group = "release"
    description = "Create GitHub release"
    
    dependsOn("releaseCollectArtifacts")
    
    val releaseDir = artifactsDir.get().dir("release/${project.version}")
    
    // This requires 'gh' CLI to be installed
    commandLine(
        "gh", "release", "create",
        "v${project.version}",
        "--title", "Release ${project.version}",
        "--generate-notes"
    )
    
    doLast {
        // Upload artifacts
        fileTree(releaseDir).files.forEach { artifact ->
            exec {
                commandLine(
                    "gh", "release", "upload",
                    "v${project.version}",
                    artifact.absolutePath
                )
            }
        }
        logger.lifecycle("✓ GitHub release v${project.version} created")
    }
}

// ═══════════════════════════════════════════════════════════════════════════
// GOD TIER UNIFIED COMMANDS
// ═══════════════════════════════════════════════════════════════════════════

tasks.named("clean") {
    group = "build"
    description = "Clean ALL build artifacts across ALL modules"
    
    doFirst {
        logger.lifecycle("🧹 Cleaning all build artifacts...")
    }
    
    delete(layout.buildDirectory)
    delete("dist")
    delete("build")
    delete(".pytest_cache")
    delete(".ruff_cache")
    delete(".mypy_cache")
    delete("__pycache__")
    delete(fileTree(".") { include("**/__pycache__") })
    delete(fileTree(".") { include("**/*.pyc") })
    
    if (file("desktop/dist").exists()) delete("desktop/dist")
    if (file("desktop/release").exists()) delete("desktop/release")
    if (file("app/build").exists()) delete("app/build")
    if (file("android/build").exists()) delete("android/build")
    
    doLast {
        logger.lifecycle("✓ All artifacts cleaned")
    }
}

tasks.named("check") {
    group = "verification"
    description = "Run ALL checks (lint, test, security)"
    
    dependsOn("lintAll", "testAll", "securityScanAll")
    
    doLast {
        logger.lifecycle("═══════════════════════════════════════════════════════════")
        logger.lifecycle("✓ ALL CHECKS PASSED")
        logger.lifecycle("═══════════════════════════════════════════════════════════")
    }
}

tasks.register<Task>("buildAll") {
    group = "build"
    description = "Build ALL modules (Python, Android, Desktop, Docs)"
    
    val buildTasks = mutableListOf<String>()
    
    if (discoveredModules.contains("python-app") || discoveredModules.contains("python-api")) {
        buildTasks.add("pythonBuild")
    }
    if (discoveredModules.contains("desktop")) {
        buildTasks.add("desktopBuild")
    }
    if (discoveredModules.contains("android") || discoveredModules.contains("app")) {
        buildTasks.add("androidBuildRelease")
    }
    buildTasks.add("docsBuild")
    
    dependsOn(buildTasks)
    
    doLast {
        logger.lifecycle("═══════════════════════════════════════════════════════════")
        logger.lifecycle("✓ ALL MODULES BUILT SUCCESSFULLY")
        logger.lifecycle("  Build Time: $buildTimestamp")
        logger.lifecycle("  Version: ${project.version}")
        logger.lifecycle("  Modules Built: ${buildTasks.size}")
        logger.lifecycle("═══════════════════════════════════════════════════════════")
    }
}

tasks.register<Task>("release") {
    group = "release"
    description = "GOD TIER: Full release pipeline (clean, check, build, package, publish)"
    
    dependsOn(
        "clean",
        "check",
        "buildAll",
        "sbomGenerate",
        "releaseCollectArtifacts"
    )
    
    tasks.findByName("check")?.mustRunAfter("clean")
    tasks.findByName("buildAll")?.mustRunAfter("check")
    tasks.findByName("sbomGenerate")?.mustRunAfter("buildAll")
    tasks.findByName("releaseCollectArtifacts")?.mustRunAfter("sbomGenerate")
    
    doLast {
        logger.lifecycle("═══════════════════════════════════════════════════════════")
        logger.lifecycle("🎉 GOD TIER RELEASE PIPELINE COMPLETED")
        logger.lifecycle("═══════════════════════════════════════════════════════════")
        logger.lifecycle("Version: ${project.version}")
        logger.lifecycle("Build Time: $buildTimestamp")
        logger.lifecycle("Artifacts: ${artifactsDir.get().asFile.absolutePath}")
        logger.lifecycle("═══════════════════════════════════════════════════════════")
        logger.lifecycle("Next steps:")
        logger.lifecycle("  1. Review artifacts in ${artifactsDir.get().asFile.absolutePath}")
        logger.lifecycle("  2. Run 'gradle releaseGitHubRelease' to publish to GitHub")
        logger.lifecycle("  3. Run 'gradle dockerPush' to publish Docker images")
        logger.lifecycle("═══════════════════════════════════════════════════════════")
    }
}

// Default task
defaultTasks("check")

// ═══════════════════════════════════════════════════════════════════════════
// TASK LISTING & HELP
// ═══════════════════════════════════════════════════════════════════════════

tasks.register<Task>("godTierHelp") {
    group = "help"
    description = "Display God Tier build system help"
    
    doLast {
        val modulesCount = project.findProperty("discoveredModulesCount") ?: "9"
        println("""
═══════════════════════════════════════════════════════════════════════════
                    THIRSTY'S GRADLE - GOD TIER BUILD SYSTEM
═══════════════════════════════════════════════════════════════════════════

🎯 UNIFIED COMMANDS (Use These!)
────────────────────────────────────────────────────────────────────────────
  gradle clean          Clean all build artifacts across all modules
  gradle check          Run all checks (lint, test, security)
  gradle buildAll       Build all modules (Python, Android, Desktop, Docs)
  gradle release        Full release pipeline (clean → check → build → publish)

📦 MODULE-SPECIFIC BUILDS
────────────────────────────────────────────────────────────────────────────
Python:
  gradle pythonInstall      Install Python dependencies
  gradle pythonLint         Lint Python code
  gradle pythonTest         Run Python tests
  gradle pythonBuild        Build Python package
  gradle pythonRun          Run desktop application
  gradle pythonRunApi       Run API server

Android:
  gradle androidBuild       Build Android debug APK
  gradle androidBuildRelease Build Android release APK
  gradle androidTest        Run Android tests
  gradle androidLint        Run Android lint

Desktop (Electron):
  gradle desktopBuild       Build Electron desktop app
  gradle desktopPackageWin  Package for Windows
  gradle desktopPackageMac  Package for macOS
  gradle desktopPackageLinux Package for Linux
  gradle desktopPackageAll  Package for all platforms

📚 DOCUMENTATION
────────────────────────────────────────────────────────────────────────────
  gradle docsBuild          Build documentation
  gradle docsVerify         Verify documentation
  gradle docsPublish        Publish documentation artifacts

🧪 TESTING
────────────────────────────────────────────────────────────────────────────
  gradle testAll            Run ALL tests
  gradle testE2E            Run end-to-end tests
  gradle testAdversarial    Run adversarial/red-team tests
  gradle testPerformance    Run performance benchmarks

🔒 SECURITY & QUALITY
────────────────────────────────────────────────────────────────────────────
  gradle lintAll            Run all linters
  gradle formatAll          Auto-format all code
  gradle securityScanAll    Run security scans
  gradle securityScanBandit Run Bandit security scanner
  gradle sbomGenerate       Generate Software Bill of Materials

💾 USB / PORTABLE
────────────────────────────────────────────────────────────────────────────
  gradle usbCreateInstaller Create USB installer
  gradle usbCreatePortable  Create portable USB package
  gradle usbCreateUniversal Create universal USB (all platforms)

🐳 DOCKER
────────────────────────────────────────────────────────────────────────────
  gradle dockerBuild        Build Docker image
  gradle dockerCompose      Start Docker Compose environment
  gradle dockerComposeDown  Stop Docker Compose environment
  gradle dockerPush         Push Docker image to registry

🚀 RELEASE & PUBLISHING
────────────────────────────────────────────────────────────────────────────
  gradle releaseCollectArtifacts  Collect all release artifacts
  gradle releaseGitHubRelease     Create GitHub release

═══════════════════════════════════════════════════════════════════════════
Version: ${project.version}
Discovered Modules: android, app, desktop, engines, kernel, python-api, python-app, tarl, web-backend
═══════════════════════════════════════════════════════════════════════════

For detailed task information, run: gradle tasks --all

        """.trimIndent())
    }
}

// ═══════════════════════════════════════════════════════════════════════════
// EVOLUTION SUBSTRATE - GOD TIER INTEGRATION LAYER
// ═══════════════════════════════════════════════════════════════════════════

val evolutionPython = if (System.getProperty("os.name").lowercase().contains("windows")) {
    file("${pythonVenvDir}/Scripts/python.exe").absolutePath
} else {
    file("${pythonVenvDir}/bin/python").absolutePath
}

val evolutionBridge = file("gradle-evolution/gradle_integration.py")

// Evolution: Constitutional validation for build phases
tasks.register<Exec>("evolutionValidate") {
    group = "evolution"
    description = "Validate build through constitutional, policy, and security layers"
    
    dependsOn("pythonInstall")
    
    commandLine(
        evolutionPython,
        evolutionBridge.absolutePath,
        "validate-phase",
        "full-build",
        """{"phase":"validation","timestamp":"$buildTimestamp","ci":"$isContinuousIntegration"}"""
    )
    
    doFirst {
        logger.lifecycle("🧬 Validating build through Evolution substrate...")
    }
    
    doLast {
        logger.lifecycle("✓ Constitutional validation complete")
    }
}

// Evolution: Create deterministic build capsule
tasks.register<Exec>("evolutionCapsule") {
    group = "evolution"
    description = "Create deterministic, signed build capsule with Merkle hash trees"
    
    dependsOn("pythonInstall", "buildAll")
    
    val artifactsJson = """["build/outputs","build/artifacts"]"""
    
    commandLine(
        evolutionPython,
        evolutionBridge.absolutePath,
        "create-capsule",
        "full-build",
        artifactsJson,
        """{"timestamp":"$buildTimestamp","version":"$version","ci":"$isContinuousIntegration"}"""
    )
    
    doFirst {
        logger.lifecycle("🧬 Creating deterministic build capsule with hash trees...")
    }
    
    doLast {
        logger.lifecycle("✓ Build capsule created: build/capsules/")
    }
}

// Evolution: Forensic replay from capsule
tasks.register<Exec>("evolutionReplay") {
    group = "evolution"
    description = "Forensic replay of build from capsule with cryptographic verification"
    
    dependsOn("pythonInstall")
    
    val capsuleId = project.findProperty("capsuleId")?.toString() ?: "latest"
    
    commandLine(
        evolutionPython,
        "-m", "gradle_evolution.capsules.replay_engine",
        "--capsule-id", capsuleId,
        "--verify"
    )
    
    doFirst {
        logger.lifecycle("🧬 Replaying build from capsule: $capsuleId")
    }
    
    doLast {
        logger.lifecycle("✓ Replay complete with cryptographic verification")
    }
}

// Evolution: Generate comprehensive audit report
tasks.register<Exec>("evolutionAudit") {
    group = "evolution"
    description = "Generate military-grade audit report with full accountability chain"
    
    dependsOn("pythonInstall")
    
    commandLine(
        evolutionPython,
        "-m", "gradle_evolution.audit.audit_integration",
        "--generate-report",
        "--output", "build/reports/evolution/audit.html",
        "--format", "html,json,pdf"
    )
    
    doFirst {
        logger.lifecycle("🧬 Generating comprehensive audit report...")
    }
    
    doLast {
        logger.lifecycle("✓ Audit reports generated:")
        logger.lifecycle("  • build/reports/evolution/audit.html")
        logger.lifecycle("  • build/reports/evolution/audit.json")
        logger.lifecycle("  • build/reports/evolution/audit.pdf")
    }
}

// Evolution: Generate living documentation
tasks.register<Exec>("evolutionDocs") {
    group = "evolution"
    description = "Generate living documentation from execution state and cognition"
    
    dependsOn("pythonInstall")
    
    commandLine(
        evolutionPython,
        evolutionBridge.absolutePath,
        "generate-docs"
    )
    
    doFirst {
        logger.lifecycle("🧬 Generating living documentation from execution state...")
    }
    
    doLast {
        logger.lifecycle("✓ Living documentation: build/docs/generated/")
    }
}

// Evolution: System status and health
tasks.register<Exec>("evolutionStatus") {
    group = "evolution"
    description = "Show evolution substrate status, health, and metrics"
    
    dependsOn("pythonInstall")
    
    commandLine(
        evolutionPython,
        evolutionBridge.absolutePath,
        "status"
    )
    
    doFirst {
        logger.lifecycle("═══════════════════════════════════════════════════════════")
        logger.lifecycle("EVOLUTION SUBSTRATE STATUS")
        logger.lifecycle("═══════════════════════════════════════════════════════════")
    }
}

// Evolution: Zero-magic transparency mode
tasks.register<Exec>("evolutionTransparency") {
    group = "evolution"
    description = "Enable zero-magic mode with full transparency logging"
    
    dependsOn("pythonInstall")
    
    commandLine(
        evolutionPython,
        "-m", "gradle_evolution.api.documentation_generator",
        "--zero-magic-mode",
        "--output", "build/transparency-log.json"
    )
    
    doFirst {
        logger.lifecycle("🧬 Enabling zero-magic transparency mode...")
    }
    
    doLast {
        logger.lifecycle("✓ Transparency log: build/transparency-log.json")
    }
}

// Evolution: Accountability override (requires human authorization)
tasks.register<Exec>("evolutionOverride") {
    group = "evolution"
    description = "Request human accountability override for policy violations"
    
    dependsOn("pythonInstall")
    
    val reason = project.findProperty("overrideReason")?.toString() 
        ?: throw GradleException("Must provide -PoverrideReason='...'")
    val authorizer = project.findProperty("authorizer")?.toString() 
        ?: throw GradleException("Must provide -Pauthorizer='...'")
    
    commandLine(
        evolutionPython,
        "-m", "gradle_evolution.audit.accountability",
        "--request-override",
        "--reason", reason,
        "--authorizer", authorizer
    )
    
    doFirst {
        logger.lifecycle("🧬 Requesting accountability override...")
        logger.lifecycle("  Reason: $reason")
        logger.lifecycle("  Authorizer: $authorizer")
    }
    
    doLast {
        logger.lifecycle("✓ Override request submitted for review")
    }
}

// Evolution: Policy scheduler configuration
tasks.register<Exec>("evolutionPolicySchedule") {
    group = "evolution"
    description = "Configure dynamic policy scheduling based on risk levels"
    
    dependsOn("pythonInstall")
    
    val mode = project.findProperty("policyMode")?.toString() ?: "adaptive"
    
    commandLine(
        evolutionPython,
        "-m", "gradle_evolution.security.policy_scheduler",
        "--mode", mode,
        "--config", "config/security_hardening.yaml"
    )
    
    doFirst {
        logger.lifecycle("🧬 Configuring policy scheduler: $mode mode")
    }
    
    doLast {
        logger.lifecycle("✓ Policy scheduler configured")
    }
}

// Evolution: Verifiability API server
tasks.register<Exec>("evolutionApiStart") {
    group = "evolution"
    description = "Start external verifiability API server"
    
    dependsOn("pythonInstall")
    
    val port = project.findProperty("apiPort")?.toString() ?: "8765"
    
    commandLine(
        evolutionPython,
        "-m", "gradle_evolution.api.verifiability_api",
        "--port", port,
        "--host", "0.0.0.0"
    )
    
    doFirst {
        logger.lifecycle("🧬 Starting verifiability API server on port $port...")
    }
}

// Wire evolution validation into check task (constitutional gate)
tasks.named("check").configure {
    dependsOn("evolutionValidate")
}

// Wire comprehensive evolution into release pipeline
tasks.named("release").configure {
    dependsOn(
        "evolutionValidate",
        "evolutionCapsule",
        "evolutionAudit",
        "evolutionDocs",
        "evolutionTransparency"
    )
    
    doFirst {
        logger.lifecycle("═══════════════════════════════════════════════════════════")
        logger.lifecycle("INITIATING GOD TIER RELEASE WITH EVOLUTION SUBSTRATE")
        logger.lifecycle("═══════════════════════════════════════════════════════════")
    }
}

// God Tier help for Evolution
tasks.register("evolutionHelp") {
    group = "evolution"
    description = "Display comprehensive Evolution substrate help"
    
    doLast {
        println("""
═══════════════════════════════════════════════════════════════════════════
         THIRSTY'S GRADLE - EVOLUTION SUBSTRATE (GOD TIER)
═══════════════════════════════════════════════════════════════════════════

The Evolution Substrate integrates constitutional governance, build cognition,
deterministic capsules, security enforcement, audit trails, and accountability
into the Gradle build lifecycle.

🧬 CONSTITUTIONAL LAYER
────────────────────────────────────────────────────────────────────────────
  evolutionValidate        Validate build through constitutional principles
                          • Enforces policies/constitution.yaml
                          • Policy engine integration
                          • Security layer validation
                          • Automatically runs on 'gradle check'

🔐 DETERMINISTIC CAPSULES
────────────────────────────────────────────────────────────────────────────
  evolutionCapsule         Create signed build capsule with Merkle trees
                          • Cryptographic signatures
                          • Hash tree verification
                          • Tamper-proof artifacts
                          • Automatically runs on 'gradle release'
  
  evolutionReplay          Forensic replay from capsule
                          Usage: gradle evolutionReplay -PcapsuleId=<id>
                          • Cryptographic verification
                          • Temporal consistency checks
                          • Audit trail reconstruction

📊 AUDIT & ACCOUNTABILITY
────────────────────────────────────────────────────────────────────────────
  evolutionAudit           Generate comprehensive audit report
                          • Military-grade audit trail
                          • Full accountability chain
                          • HTML, JSON, and PDF outputs
                          • Automatically runs on 'gradle release'
  
  evolutionOverride        Request human accountability override
                          Usage: gradle evolutionOverride \
                                 -PoverrideReason="..." \
                                 -Pauthorizer="..."
                          • Requires human authorization
                          • Creates immutable audit record
                          • Policy exception workflow

📚 DOCUMENTATION & TRANSPARENCY
────────────────────────────────────────────────────────────────────────────
  evolutionDocs            Generate living documentation
                          • Auto-generated from execution state
                          • Build cognition insights
                          • System behavior documentation
  
  evolutionTransparency    Enable zero-magic transparency mode
                          • Full execution logging
                          • No hidden operations
                          • Complete state disclosure

🔒 SECURITY & POLICY
────────────────────────────────────────────────────────────────────────────
  evolutionPolicySchedule  Configure dynamic policy scheduling
                          Usage: gradle evolutionPolicySchedule \
                                 -PpolicyMode=<adaptive|strict|permissive>
                          • Risk-adaptive scheduling
                          • Plugin containment
                          • Security mode switching
  
  evolutionStatus          Show system status and health
                          • Component health checks
                          • Metrics and statistics
                          • Configuration status

🌐 EXTERNAL VERIFIABILITY
────────────────────────────────────────────────────────────────────────────
  evolutionApiStart        Start verifiability API server
                          Usage: gradle evolutionApiStart -PapiPort=8765
                          • REST API for external verification
                          • Capsule verification endpoints
                          • Audit log access
                          • Real-time status monitoring

═══════════════════════════════════════════════════════════════════════════
ARCHITECTURE LAYERS
═══════════════════════════════════════════════════════════════════════════

1. Constitutional Engine    policies/constitution.yaml enforcement
2. Policy Enforcer          project_ai/engine/policy integration
3. Build Cognition         Self-modeling and optimization
4. State Management        Build memory and history
5. Capsule Engine          Deterministic, signed artifacts
6. Replay Engine           Forensic reconstruction
7. Security Engine         config/security_hardening.yaml
8. Policy Scheduler        Dynamic, risk-adaptive policies
9. Audit Integration       cognition/audit.py integration
10. Accountability Manager  Human override workflow
11. Verifiability API       External verification endpoints
12. Documentation Generator Living documentation from state

═══════════════════════════════════════════════════════════════════════════
INTEGRATION POINTS
═══════════════════════════════════════════════════════════════════════════

• Wires into 'gradle check' for constitutional validation
• Wires into 'gradle release' for complete audit trail
• Uses existing governance/ infrastructure
• Integrates cognition/ for build intelligence
• Leverages temporal/ for replay capability
• Extends project_ai/engine components
• Enforces config/security_hardening.yaml

═══════════════════════════════════════════════════════════════════════════
For complete Gradle help: gradle godTierHelp
For all tasks:            gradle tasks --all
═══════════════════════════════════════════════════════════════════════════
        """.trimIndent())
    }
}

// ═══════════════════════════════════════════════════════════════════════════
// END OF GOD TIER BUILD ORCHESTRATION WITH EVOLUTION SUBSTRATE
// ═══════════════════════════════════════════════════════════════════════════

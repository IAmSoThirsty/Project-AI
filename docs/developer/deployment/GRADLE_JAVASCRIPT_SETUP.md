# Gradle + JavaScript Setup Guide for Project-AI

This guide will help you set up Gradle to work with JavaScript/Node.js in your Project-AI repository.

## Overview

Your project now has Gradle configured with the **Node Gradle Plugin**, which allows Gradle to:
- Download and manage Node.js automatically
- Run npm commands through Gradle tasks
- Integrate JavaScript builds with your Android builds
- Provide a unified build system across multiple platforms

## Prerequisites

### 1. Install Java Development Kit (JDK)

Gradle requires Java to run. You need to install a JDK first.

#### Recommended: Install JDK 17 (LTS)

**Option A: Using Chocolatey (Recommended for Windows)**
```powershell
# Install Chocolatey if you don't have it
# Run PowerShell as Administrator and execute:
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Then install OpenJDK 17:
choco install openjdk17 -y
```

**Option B: Manual Download**
1. Download OpenJDK 17 from: https://adoptium.net/
2. Choose **Temurin 17 (LTS)** for Windows
3. Download the `.msi` installer
4. Run the installer and **check the option to set JAVA_HOME**
5. Restart your terminal/PowerShell

#### Verify Java Installation

```powershell
java -version
```

Expected output:
```
openjdk version "17.0.x" 2024-xx-xx
OpenJDK Runtime Environment Temurin-17.0.x+x (build 17.0.x+x)
OpenJDK 64-Bit Server VM Temurin-17.0.x+x (build 17.0.x+x, mixed mode, sharing)
```

### 2. Set JAVA_HOME Environment Variable

If the installer didn't set it automatically:

**PowerShell (Run as Administrator):**
```powershell
# Find your Java installation path
$javaPath = (Get-Command java).Source
$javaHome = Split-Path (Split-Path $javaPath)

# Set JAVA_HOME for current user
[System.Environment]::SetEnvironmentVariable('JAVA_HOME', $javaHome, 'User')

# Add to PATH
$currentPath = [System.Environment]::GetEnvironmentVariable('Path', 'User')
[System.Environment]::SetEnvironmentVariable('Path', "$currentPath;$javaHome\bin", 'User')

# Verify
$env:JAVA_HOME
```

**Manual Setup:**
1. Press `Win + X` → System
2. Click "Advanced system settings"
3. Click "Environment Variables"
4. Under "System variables" click "New"
5. Variable name: `JAVA_HOME`
6. Variable value: Path to JDK (e.g., `C:\Program Files\Eclipse Adoptium\jdk-17.0.10.7-hotspot`)
7. Edit "Path" and add: `%JAVA_HOME%\bin`
8. Click OK and restart your terminal

## Available Gradle Tasks for JavaScript

Once Java is installed, you can use these Gradle tasks:

### 📦 Install Dependencies
```bash
.\gradlew.bat npmInstall
```
This downloads Node.js automatically and installs npm packages from `package.json`.

### 🧪 Run JavaScript Tests
```bash
.\gradlew.bat npmTest
```
Runs all JavaScript tests defined in your project.

### 🔨 Build JavaScript/TypeScript
```bash
.\gradlew.bat npmBuild
```
Builds your JavaScript/TypeScript code (if you add a build script to `package.json`).

### 🚀 Run Development Server
```bash
.\gradlew.bat npmDev
```
Starts the development server using Docker Compose.

### ✅ Run Markdown Linting
```bash
.\gradlew.bat npmLint
```
Lints all markdown documentation files.

### 📋 List All Tasks
```bash
.\gradlew.bat tasks --all
```
Shows all available Gradle tasks.

## Configuration Details

### Node.js Version
The Gradle configuration automatically downloads **Node.js 20.11.0**. You don't need to install Node.js separately! The plugin will download it to `.gradle/nodejs/`.

### Gradle Node Plugin Settings
Located in `build.gradle`:
```gradle
node {
    version = '20.11.0'          // Node.js version to download
    download = true              // Auto-download Node.js
    workDir = file("${project.projectDir}/.gradle/nodejs")    // Node install location
    npmWorkDir = file("${project.projectDir}/.gradle/npm")    // npm cache location
}
```

## Adding More JavaScript Tasks

To add custom npm scripts, edit `package.json` and add them to the `scripts` section:

```json
{
  "scripts": {
    "build": "webpack --mode production",
    "start": "node server.js",
    "custom-task": "echo 'Custom task'"
  }
}
```

Then create corresponding Gradle tasks in `build.gradle`:

```gradle
task npmCustomTask(type: com.github.gradle.node.npm.task.NpmTask) {
    dependsOn npmInstall
    description = 'Run custom npm task'
    args = ['run', 'custom-task']
}
```

## Troubleshooting

### Error: "JAVA_HOME is not set"
- Follow the "Set JAVA_HOME Environment Variable" section above
- Restart your terminal/PowerShell after setting environment variables

### Error: "Could not find or load main class"
- Make sure you installed the JDK, not just the JRE
- Verify `java -version` shows OpenJDK, not just "java"

### Error: "Gradle version X.X requires Java Y"
- Update to Java 17 (LTS) or newer
- Check Gradle version compatibility: https://docs.gradle.org/current/userguide/compatibility.html

### Node.js Not Downloading
- Check internet connection
- Try running with `--refresh-dependencies` flag:
  ```bash
  .\gradlew.bat npmInstall --refresh-dependencies
  ```

### Permission Errors
- Run PowerShell as Administrator
- Check that `.gradle` directory is not read-only

## Next Steps

1. **Install Java JDK 17** using one of the methods above
2. **Set JAVA_HOME** environment variable
3. **Restart your terminal**
4. **Test Gradle**: `.\gradlew.bat tasks --all`
5. **Install npm packages**: `.\gradlew.bat npmInstall`
6. **Run your first task**: `.\gradlew.bat npmTest`

## Integration with VS Code

To enable VS Code IntelliSense for Java/Gradle:

1. Install the **Extension Pack for Java** from Microsoft
2. Create/update `.vscode/settings.json`:

```json
{
  "java.configuration.runtimes": [
    {
      "name": "JavaSE-17",
      "path": "C:\\Program Files\\Eclipse Adoptium\\jdk-17.0.10.7-hotspot",
      "default": true
    }
  ],
  "java.jdt.ls.java.home": "C:\\Program Files\\Eclipse Adoptium\\jdk-17.0.10.7-hotspot"
}
```

Replace the path with your actual Java installation path.

## Resources

- [Gradle Node Plugin Documentation](https://github.com/node-gradle/gradle-node-plugin)
- [Adoptium JDK Downloads](https://adoptium.net/)
- [Gradle Documentation](https://docs.gradle.org/)
- [Java Environment Setup](https://docs.oracle.com/javase/tutorial/essential/environment/paths.html)

---

**📝 Note:** Once you complete this setup, Gradle will manage both your Android builds and JavaScript builds in a unified way!

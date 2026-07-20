# Project-AI Android Read-Only Client

This development app exposes only the DOI registry (`GET /dois`) and canonical replay status
(`GET /replay/status`). It has no mutation, execution, governance, capability, token, or operator
authority surface. The API base URL is a development BuildConfig value.

Build with Java 17 and an Android SDK containing API 34 and Build Tools 34.0.0:

```powershell
$env:ANDROID_HOME = "$env:LOCALAPPDATA\Android\Sdk"
$env:ANDROID_SDK_ROOT = $env:ANDROID_HOME
.\gradlew.bat testDebugUnitTest assembleDebug
```

The version is `0.0.3`; the APK is unsigned beyond the normal Android debug key and is not a
release artifact.

# Project-AI Android Read-Only Client

This development app exposes only the DOI registry (`GET /dois`) and canonical replay status
(`GET /replay/status`). It has no mutation, execution, governance, capability, token, or operator
authority surface. The API base URL is a development BuildConfig value.

Build with Java 17 and an Android SDK containing API 34 and Build Tools 34.0.0:

```powershell
$env:ANDROID_HOME = "$env:LOCALAPPDATA\Android\Sdk"
$env:ANDROID_SDK_ROOT = $env:ANDROID_HOME
.\gradlew.bat lintDebug lintRelease testDebugUnitTest assembleDebug assembleRelease
```

The debug build may use cleartext traffic only to the Android emulator host
`10.0.2.2`. The main/release manifest denies cleartext traffic. Release builds default
to the non-routable HTTPS placeholder `https://project-ai.invalid`; provide the approved
TLS endpoint explicitly:

```powershell
.\gradlew.bat lintRelease assembleRelease -PprojectAiApiBaseUrl=https://project-ai.example
```

The build fails closed unless `projectAiApiBaseUrl` is a parseable HTTPS URL with a host
and no embedded credentials, query, or fragment. Cloud backup and device transfer are
disabled for every app storage domain. The interface uses density-independent sizing, a
bounded scrollable result region, selectable/linkable evidence, an accessibility heading,
and concise async load announcements.

The version is `0.0.3`; the APK is unsigned beyond the normal Android debug key and is
not a release artifact. Manual TalkBack acceptance still requires an emulator or device
with TalkBack installed.

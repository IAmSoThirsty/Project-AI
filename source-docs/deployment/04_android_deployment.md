# Android APK Deployment and Mobile Distribution

## Overview

Project-AI includes "Legion Mini" - an Android mobile application that provides on-the-go access to the AI assistant. The Android app is built with Gradle, packaged as APK files, and distributed via multiple channels including USB OTG, ADB installation, and direct APK downloads.

## Android Project Structure

### Module Organization

```
android/
├── legion_mini/                    # Main Android application module
│   ├── build.gradle               # Module-level build configuration
│   ├── src/
│   │   ├── main/
│   │   │   ├── AndroidManifest.xml
│   │   │   ├── java/com/projectai/legionmini/
│   │   │   │   ├── MainActivity.java
│   │   │   │   ├── LegionService.java
│   │   │   │   ├── ChatFragment.java
│   │   │   │   ├── PersonaFragment.java
│   │   │   │   └── SettingsFragment.java
│   │   │   ├── res/
│   │   │   │   ├── layout/
│   │   │   │   │   ├── activity_main.xml
│   │   │   │   │   ├── fragment_chat.xml
│   │   │   │   │   └── fragment_persona.xml
│   │   │   │   ├── drawable/
│   │   │   │   ├── values/
│   │   │   │   │   ├── strings.xml
│   │   │   │   │   ├── colors.xml
│   │   │   │   │   └── themes.xml
│   │   │   │   └── xml/
│   │   │   │       └── network_security_config.xml
│   │   │   └── assets/
│   │   └── debug/
│   │       └── AndroidManifest.xml   # Debug-specific overrides
│   └── proguard-rules.pro        # Code obfuscation rules
├── build.gradle                   # Root project build file
├── settings.gradle                # Project settings
├── gradle.properties              # Gradle configuration
└── gradle/
    └── wrapper/
        ├── gradle-wrapper.jar
        └── gradle-wrapper.properties
```

### Technology Stack

- **Build System**: Gradle 8.x with Kotlin DSL support
- **Target SDK**: Android 13 (API level 33)
- **Minimum SDK**: Android 8.0 Oreo (API level 26)
- **Language**: Java 17
- **Backend Integration**: Retrofit 2.9 (REST API client)
- **UI Framework**: Material Design 3
- **Dependency Injection**: Hilt/Dagger (optional)
- **Testing**: JUnit 4, Espresso, Mockito

## Build Configuration

### Root Build File

**Location**: `android/build.gradle`

```gradle
buildscript {
    ext.kotlin_version = '1.9.0'
    repositories {
        google()
        mavenCentral()
    }
    dependencies {
        classpath 'com.android.tools.build:gradle:8.1.0'
        classpath "org.jetbrains.kotlin:kotlin-gradle-plugin:$kotlin_version"
    }
}

allprojects {
    repositories {
        google()
        mavenCentral()
    }
}

task clean(type: Delete) {
    delete rootProject.buildDir
}
```

### Module Build File

**Location**: `android/legion_mini/build.gradle`

```gradle
plugins {
    id 'com.android.application'
    id 'kotlin-android'
    id 'kotlin-kapt'
}

android {
    namespace 'com.projectai.legionmini'
    compileSdk 33

    defaultConfig {
        applicationId "com.projectai.legionmini"
        minSdk 26
        targetSdk 33
        versionCode 1
        versionName "1.0.0"

        testInstrumentationRunner "androidx.test.runner.AndroidJUnitRunner"

        // Build config fields
        buildConfigField "String", "API_BASE_URL", "\"http://localhost:8001\""
        buildConfigField "String", "VERSION_NAME", "\"${versionName}\""
    }

    signingConfigs {
        release {
            storeFile file("../keystore/legion_mini_release.jks")
            storePassword System.getenv("KEYSTORE_PASSWORD") ?: "changeme"
            keyAlias "legion_mini"
            keyPassword System.getenv("KEY_PASSWORD") ?: "changeme"
        }
    }

    buildTypes {
        debug {
            applicationIdSuffix ".debug"
            versionNameSuffix "-debug"
            debuggable true
            minifyEnabled false
        }

        release {
            minifyEnabled true
            shrinkResources true
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
            signingConfig signingConfigs.release
        }
    }

    compileOptions {
        sourceCompatibility JavaVersion.VERSION_17
        targetCompatibility JavaVersion.VERSION_17
    }

    kotlinOptions {
        jvmTarget = '17'
    }

    buildFeatures {
        viewBinding true
        buildConfig true
    }

    packagingOptions {
        resources {
            excludes += ['META-INF/DEPENDENCIES', 'META-INF/LICENSE', 'META-INF/NOTICE']
        }
    }
}

dependencies {
    // AndroidX Core
    implementation 'androidx.core:core-ktx:1.10.1'
    implementation 'androidx.appcompat:appcompat:1.6.1'
    implementation 'com.google.android.material:material:1.9.0'
    implementation 'androidx.constraintlayout:constraintlayout:2.1.4'

    // Lifecycle
    implementation 'androidx.lifecycle:lifecycle-runtime-ktx:2.6.1'
    implementation 'androidx.lifecycle:lifecycle-viewmodel-ktx:2.6.1'

    // Networking
    implementation 'com.squareup.retrofit2:retrofit:2.9.0'
    implementation 'com.squareup.retrofit2:converter-gson:2.9.0'
    implementation 'com.squareup.okhttp3:okhttp:4.11.0'
    implementation 'com.squareup.okhttp3:logging-interceptor:4.11.0'

    // Coroutines
    implementation 'org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.1'

    // Image Loading
    implementation 'com.github.bumptech.glide:glide:4.15.1'
    kapt 'com.github.bumptech.glide:compiler:4.15.1'

    // Local Storage
    implementation 'androidx.room:room-runtime:2.5.2'
    kapt 'androidx.room:room-compiler:2.5.2'
    implementation 'androidx.room:room-ktx:2.5.2'

    // Security
    implementation 'androidx.security:security-crypto:1.1.0-alpha06'

    // Testing
    testImplementation 'junit:junit:4.13.2'
    testImplementation 'org.mockito:mockito-core:5.3.1'
    androidTestImplementation 'androidx.test.ext:junit:1.1.5'
    androidTestImplementation 'androidx.test.espresso:espresso-core:3.5.1'
}
```

### Key Configuration Options

**1. Application ID**:
- **Debug**: `com.projectai.legionmini.debug`
- **Release**: `com.projectai.legionmini`
- Allows simultaneous installation of debug and release builds

**2. Version Management**:
```gradle
versionCode 1        // Integer, increments with each release
versionName "1.0.0"  // Semantic versioning string
```

**3. ProGuard Configuration**:
```gradle
minifyEnabled true          # Enable code shrinking
shrinkResources true        # Remove unused resources
proguardFiles ...           # Obfuscation rules
```

**4. Build Config Fields**:
```gradle
buildConfigField "String", "API_BASE_URL", "\"http://localhost:8001\""
// Accessible in code as: BuildConfig.API_BASE_URL
```

## Building APK Files

### Using Gradle Wrapper

**Build Debug APK**:
```bash
# Windows
cd T:\Project-AI-main
gradlew.bat :legion_mini:assembleDebug

# Linux/macOS
cd /path/to/Project-AI-main
./gradlew :legion_mini:assembleDebug
```

**Output**: `android/legion_mini/build/outputs/apk/debug/legion_mini-debug.apk`

**Build Release APK**:
```bash
# Windows
gradlew.bat :legion_mini:assembleRelease

# Linux/macOS
./gradlew :legion_mini:assembleRelease
```

**Output**: `android/legion_mini/build/outputs/apk/release/legion_mini-release.apk`

### Using Production Build Script

**Location**: `scripts/build_production.ps1`

```powershell
# Build Android only
.\scripts\build_production.ps1 -Android

# Build all platforms
.\scripts\build_production.ps1 -All
```

**Script excerpt**:
```powershell
# Set Java environment
$env:JAVA_HOME = "C:\Program Files\Eclipse Adoptium\jdk-17.0.17.10-hotspot"
$env:PATH = "$env:JAVA_HOME\bin;$env:PATH"

# Build APKs
& .\gradlew.bat :legion_mini:assembleDebug
& .\gradlew.bat :legion_mini:assembleRelease

Write-Host "✓ Android APK built successfully"
Write-Host "  Debug: android\legion_mini\build\outputs\apk\debug\legion_mini-debug.apk"
Write-Host "  Release: android\legion_mini\build\outputs\apk\release\legion_mini-release.apk"
```

### Build Variants

| Variant | Application ID | Debuggable | Minified | Signed |
|---------|----------------|------------|----------|--------|
| Debug | com.projectai.legionmini.debug | ✅ | ❌ | Debug key |
| Release | com.projectai.legionmini | ❌ | ✅ | Release key |

**Use Cases**:
- **Debug**: Development, testing, USB debugging
- **Release**: Production distribution, Play Store upload

## Code Signing

### Debug Signing

**Default Behavior**: Gradle auto-generates debug keystore

**Location**: `~/.android/debug.keystore`

**Credentials**:
- Store password: `android`
- Key alias: `androiddebugkey`
- Key password: `android`

**Security**: Debug keys are **NOT** secure, never use for production

### Release Signing

**Keystore Generation**:
```bash
keytool -genkey -v \
  -keystore android/keystore/legion_mini_release.jks \
  -alias legion_mini \
  -keyalg RSA \
  -keysize 2048 \
  -validity 10000 \
  -storepass $KEYSTORE_PASSWORD \
  -keypass $KEY_PASSWORD \
  -dname "CN=Project AI, OU=Development, O=Thirsty Projects, L=City, ST=State, C=US"
```

**Environment Variables** (for CI/CD):
```bash
export KEYSTORE_PASSWORD="your_secure_password"
export KEY_PASSWORD="your_secure_password"
```

**Gradle Configuration** (`build.gradle`):
```gradle
signingConfigs {
    release {
        storeFile file("../keystore/legion_mini_release.jks")
        storePassword System.getenv("KEYSTORE_PASSWORD")
        keyAlias "legion_mini"
        keyPassword System.getenv("KEY_PASSWORD")
    }
}
```

**Security Best Practices**:
1. **Never commit keystore to Git**:
   ```gitignore
   # .gitignore
   android/keystore/*.jks
   ```

2. **Use CI/CD secrets** for passwords
3. **Backup keystore securely** (losing it = can't update app)
4. **Rotate keys** every 2-3 years

## APK Distribution Methods

### Method 1: USB OTG (On-The-Go)

**Target**: Android devices with OTG support

**Steps**:
1. Copy APK to USB drive: `E:\LegionMini\android\legion_mini-debug.apk`
2. Connect USB drive to Android device via OTG adapter
3. Open file manager app (Files, Solid Explorer, etc.)
4. Navigate to USB drive
5. Tap APK file
6. Allow "Unknown Sources" if prompted
7. Tap "Install"

**Advantages**:
- No PC required
- Works offline
- Fast transfer

**Disadvantages**:
- Requires OTG adapter
- Must enable Unknown Sources
- Not all devices support OTG

### Method 2: ADB (Android Debug Bridge)

**Target**: Developers, power users

**Prerequisites**:
- USB debugging enabled on device
- ADB installed on PC

**Enable USB Debugging**:
1. Settings → About Phone
2. Tap "Build Number" 7 times (enables Developer Options)
3. Settings → Developer Options
4. Enable "USB Debugging"

**Install via ADB**:
```bash
# Check device connected
adb devices

# Install APK
adb install android/legion_mini/build/outputs/apk/debug/legion_mini-debug.apk

# Install release APK
adb install android/legion_mini/build/outputs/apk/release/legion_mini-release.apk

# Reinstall (keep data)
adb install -r legion_mini-debug.apk

# Force downgrade (lower version code)
adb install -d legion_mini-debug.apk
```

**Automated Installation Script**:

**Location**: `INSTALL_ANDROID.bat` (on USB drive)

```batch
@echo off
title Legion Mini - Android Installation
echo ========================================
echo    Install Legion Mini on Android
echo ========================================
echo.
echo Make sure:
echo  1. USB Debugging is enabled
echo  2. Device is connected via USB
echo  3. You have ADB installed
echo.
pause
echo.
echo Installing APK...
cd /d "%~dp0LegionMini\android"
adb install -r legion_mini-debug.apk
echo.
echo Installation complete!
pause
```

### Method 3: Direct Download (Web Server)

**Hosting APK on Backend**:

**API Endpoint**: `GET /api/download/android`

**Flask Implementation** (`web/backend/app.py` [[web/backend/app.py]]):
```python
from flask import send_file
import os

@app.route('/api/download/android', methods=['GET'])
def download_android():
    apk_path = os.path.join('builds', 'legion_mini-release.apk')
    return send_file(
        apk_path,
        mimetype='application/vnd.android.package-archive',
        as_attachment=True,
        download_name='LegionMini.apk'
    )
```

**User Flow**:
1. User visits `http://localhost:5000/download`
2. Clicks "Download Android App"
3. Browser downloads APK
4. User opens APK from Downloads
5. Android prompts to install

**Security**: Serve over HTTPS, verify APK integrity with checksum

### Method 4: Play Store (Future)

**Not Yet Implemented**

**Requirements**:
1. Google Play Console account ($25 one-time fee)
2. Signed release APK
3. App listing (descriptions, screenshots, privacy policy)
4. Content rating questionnaire
5. Target API level compliance (Android 13+)

**Steps**:
1. Create app in Play Console
2. Upload release APK
3. Fill out store listing
4. Submit for review
5. Wait 1-7 days for approval

**Advantages**:
- Trusted distribution channel
- Automatic updates
- Wider reach

**Disadvantages**:
- Review process (can reject)
- Must comply with Play Store policies
- 15% commission on in-app purchases

## Android Manifest Configuration

### Network Security

**Location**: `android/legion_mini/src/main/res/xml/network_security_config.xml`

```xml
<?xml version="1.0" encoding="utf-8"?>
<network-security-config>
    <!-- Allow cleartext (HTTP) for localhost/development -->
    <domain-config cleartextTrafficPermitted="true">
        <domain includeSubdomains="true">localhost</domain>
        <domain includeSubdomains="true">10.0.2.2</domain>  <!-- Android emulator host -->
        <domain includeSubdomains="true">192.168.1.0/24</domain>  <!-- Local network -->
    </domain-config>

    <!-- Base config: HTTPS only for production -->
    <base-config cleartextTrafficPermitted="false">
        <trust-anchors>
            <certificates src="system" />
        </trust-anchors>
    </base-config>
</network-security-config>
```

**AndroidManifest.xml**:
```xml
<application
    android:networkSecurityConfig="@xml/network_security_config"
    ...>
```

### Permissions

**Location**: `android/legion_mini/src/main/AndroidManifest.xml`

```xml
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <!-- Network Access -->
    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />

    <!-- Storage (for image generation, file uploads) -->
    <uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" />
    <uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" />

    <!-- Location (for location tracker feature) -->
    <uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
    <uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION" />

    <!-- Notifications -->
    <uses-permission android:name="android.permission.POST_NOTIFICATIONS" />

    <!-- Wake Lock (for background services) -->
    <uses-permission android:name="android.permission.WAKE_LOCK" />

    <application
        android:allowBackup="true"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:roundIcon="@mipmap/ic_launcher_round"
        android:supportsRtl="true"
        android:theme="@style/Theme.LegionMini"
        android:networkSecurityConfig="@xml/network_security_config">
        
        <!-- Main Activity -->
        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:windowSoftInputMode="adjustResize">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>

        <!-- Background Service -->
        <service
            android:name=".LegionService"
            android:exported="false" />
    </application>
</manifest>
```

### Runtime Permissions (Android 6.0+)

**Code** (`MainActivity.java`):
```java
// Request location permission
if (ContextCompat.checkSelfPermission(this, Manifest.permission.ACCESS_FINE_LOCATION)
        != PackageManager.PERMISSION_GRANTED) {
    ActivityCompat.requestPermissions(this,
        new String[]{Manifest.permission.ACCESS_FINE_LOCATION},
        REQUEST_LOCATION_PERMISSION);
}

@Override
public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] grantResults) {
    if (requestCode == REQUEST_LOCATION_PERMISSION) {
        if (grantResults.length > 0 && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
            // Permission granted
            initLocationTracking();
        } else {
            // Permission denied
            showPermissionDeniedMessage();
        }
    }
}
```

## Backend Integration

### API Client (Retrofit)

**Interface** (`ApiService.java`):
```java
public interface ApiService {
    @POST("/api/chat")
    Call<ChatResponse> sendMessage(@Body ChatRequest request);

    @GET("/api/persona")
    Call<PersonaState> getPersona();

    @POST("/api/persona/update")
    Call<Void> updatePersona(@Body PersonaState state);

    @POST("/api/image/generate")
    Call<ImageResponse> generateImage(@Body ImageRequest request);

    @GET("/api/knowledge")
    Call<List<KnowledgeEntry>> getKnowledge();
}
```

**Retrofit Builder**:
```java
Retrofit retrofit = new Retrofit.Builder()
    .baseUrl(BuildConfig.API_BASE_URL)
    .addConverterFactory(GsonConverterFactory.create())
    .client(new OkHttpClient.Builder()
        .addInterceptor(new HttpLoggingInterceptor().setLevel(HttpLoggingInterceptor.Level.BODY))
        .connectTimeout(30, TimeUnit.SECONDS)
        .readTimeout(30, TimeUnit.SECONDS)
        .build())
    .build();

ApiService apiService = retrofit.create(ApiService.class);
```

### Local Data Persistence (Room)

**Entity** (`ChatMessage.java`):
```java
@Entity(tableName = "chat_messages")
public class ChatMessage {
    @PrimaryKey(autoGenerate = true)
    public long id;

    @ColumnInfo(name = "user_message")
    public String userMessage;

    @ColumnInfo(name = "ai_response")
    public String aiResponse;

    @ColumnInfo(name = "timestamp")
    public long timestamp;
}
```

**DAO** (`ChatDao.java`):
```java
@Dao
public interface ChatDao {
    @Query("SELECT * FROM chat_messages ORDER BY timestamp DESC")
    LiveData<List<ChatMessage>> getAllMessages();

    @Insert
    void insertMessage(ChatMessage message);

    @Query("DELETE FROM chat_messages")
    void deleteAll();
}
```

**Database** (`AppDatabase.java`):
```java
@Database(entities = {ChatMessage.class}, version = 1)
public abstract class AppDatabase extends RoomDatabase {
    public abstract ChatDao chatDao();

    private static AppDatabase instance;

    public static AppDatabase getInstance(Context context) {
        if (instance == null) {
            instance = Room.databaseBuilder(context.getApplicationContext(),
                    AppDatabase.class, "legion_mini_db")
                .build();
        }
        return instance;
    }
}
```

## ProGuard Configuration

### Obfuscation Rules

**Location**: `android/legion_mini/proguard-rules.pro`

```proguard
# Keep Retrofit interfaces
-keep,allowobfuscation,allowshrinking interface retrofit2.Call
-keep,allowobfuscation,allowshrinking class retrofit2.Response
-keep,allowobfuscation,allowshrinking class kotlin.coroutines.Continuation

# Keep Gson models
-keep class com.projectai.legionmini.models.** { *; }

# Keep Room entities
-keep class * extends androidx.room.RoomDatabase
-keep @androidx.room.Entity class *
-dontwarn androidx.room.paging.**

# Keep native methods
-keepclasseswithmembernames class * {
    native <methods>;
}

# Keep BuildConfig
-keep class com.projectai.legionmini.BuildConfig { *; }

# Remove logging in release
-assumenosideeffects class android.util.Log {
    public static *** d(...);
    public static *** v(...);
    public static *** i(...);
}
```

## APK Size Optimization

### Resource Shrinking

**Enabled in `build.gradle`**:
```gradle
buildTypes {
    release {
        minifyEnabled true
        shrinkResources true  // Remove unused resources
    }
}
```

**Remove Unused Languages**:
```gradle
android {
    defaultConfig {
        resConfigs "en", "es", "fr"  // Keep only these languages
    }
}
```

### APK Splitting

**By ABI**:
```gradle
android {
    splits {
        abi {
            enable true
            reset()
            include 'arm64-v8a', 'armeabi-v7a', 'x86', 'x86_64'
            universalApk false  // Don't generate universal APK
        }
    }
}
```

**Result**: Separate APKs for each architecture (smaller downloads)

### R8 Optimization

**Enable R8** (default in AGP 3.4+):
```gradle
android.enableR8=true
```

**R8 vs ProGuard**:
- R8 is faster and produces smaller APKs
- Fully compatible with ProGuard rules

## Testing

### Unit Tests

**Location**: `android/legion_mini/src/test/java/`

```java
@RunWith(JUnit4.class)
public class PersonaManagerTest {
    private PersonaManager personaManager;

    @Before
    public void setUp() {
        personaManager = new PersonaManager();
    }

    @Test
    public void testMoodUpdate() {
        personaManager.updateMood("happy");
        assertEquals("happy", personaManager.getCurrentMood());
    }
}
```

**Run Tests**:
```bash
./gradlew :legion_mini:testDebugUnitTest
```

### Instrumented Tests (UI)

**Location**: `android/legion_mini/src/androidTest/java/`

```java
@RunWith(AndroidJUnit4.class)
public class MainActivityTest {
    @Rule
    public ActivityScenarioRule<MainActivity> activityRule =
        new ActivityScenarioRule<>(MainActivity.class);

    @Test
    public void testSendMessage() {
        onView(withId(R.id.messageInput)).perform(typeText("Hello Legion"));
        onView(withId(R.id.sendButton)).perform(click());
        onView(withId(R.id.chatRecyclerView))
            .check(matches(hasDescendant(withText("Hello Legion"))));
    }
}
```

**Run Tests**:
```bash
# On connected device/emulator
./gradlew :legion_mini:connectedDebugAndroidTest
```

## CI/CD Integration

### GitHub Actions Workflow

**Location**: `.github/workflows/android-build.yml`

```yaml
name: Android Build

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up JDK 17
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'

      - name: Cache Gradle dependencies
        uses: actions/cache@v3
        with:
          path: |
            ~/.gradle/caches
            ~/.gradle/wrapper
          key: ${{ runner.os }}-gradle-${{ hashFiles('**/*.gradle*', '**/gradle-wrapper.properties') }}

      - name: Build Debug APK
        run: ./gradlew :legion_mini:assembleDebug

      - name: Build Release APK
        env:
          KEYSTORE_PASSWORD: ${{ secrets.KEYSTORE_PASSWORD }}
          KEY_PASSWORD: ${{ secrets.KEY_PASSWORD }}
        run: ./gradlew :legion_mini:assembleRelease

      - name: Upload APK artifacts
        uses: actions/upload-artifact@v3
        with:
          name: apk-files
          path: |
            android/legion_mini/build/outputs/apk/debug/*.apk
            android/legion_mini/build/outputs/apk/release/*.apk
```

## Troubleshooting

### Build Failures

**1. Gradle Sync Failed**
```bash
# Clear Gradle cache
./gradlew clean
rm -rf ~/.gradle/caches

# Re-download dependencies
./gradlew build --refresh-dependencies
```

**2. SDK Not Found**
```bash
# Set ANDROID_HOME environment variable
export ANDROID_HOME=$HOME/Android/Sdk
export PATH=$PATH:$ANDROID_HOME/tools:$ANDROID_HOME/platform-tools
```

**3. Java Version Mismatch**
```bash
# Check Java version
java -version

# Set JAVA_HOME to JDK 17
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk
```

### Installation Issues

**1. "App Not Installed"**
- Enable Unknown Sources: Settings → Security → Unknown Sources
- Check signature conflict: Uninstall old version
- Verify APK integrity: Re-download/re-copy

**2. "Parse Error"**
- APK corrupted: Re-download
- Incompatible Android version: Check `minSdk` (Android 8.0+)
- Architecture mismatch: Use universal APK

**3. "Installation Blocked"**
- Play Protect: Settings → Google Play Protect → Disable
- Admin restrictions: Check device management policies

## Related Documentation

- `02_desktop_distribution.md` - Desktop deployment
- `03_portable_usb_deployment.md` - USB installer (includes Android)
- `07_container_security.md` - Security hardening
- `10_cicd_docker_pipeline.md` - Automated builds

## References

- **Android Developer Guide**: https://developer.android.com/studio/build
- **Gradle Plugin**: https://developer.android.com/studio/releases/gradle-plugin
- **Retrofit**: https://square.github.io/retrofit/
- **Room Database**: https://developer.android.com/training/data-storage/room
- **ProGuard**: https://www.guardsquare.com/manual/home

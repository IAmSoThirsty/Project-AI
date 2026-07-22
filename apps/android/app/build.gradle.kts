import java.net.URI

plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

fun String.asBuildConfigString(): String =
    "\"${replace("\\", "\\\\").replace("\"", "\\\"")}\""

val releaseApiBaseUrl = providers.gradleProperty("projectAiApiBaseUrl")
    .orElse("https://project-ai.invalid")
    .get()
val parsedReleaseApiUrl = runCatching { URI(releaseApiBaseUrl) }.getOrNull()

require(
    parsedReleaseApiUrl?.scheme.equals("https", ignoreCase = true) &&
        !parsedReleaseApiUrl?.host.isNullOrBlank() &&
        parsedReleaseApiUrl?.userInfo == null &&
        parsedReleaseApiUrl?.query == null &&
        parsedReleaseApiUrl?.fragment == null,
) {
    "projectAiApiBaseUrl must be an HTTPS URL with a host and no credentials, query, or fragment."
}

android {
    namespace = "ai.project.readonly"
    compileSdk = 36
    buildToolsVersion = "36.0.0"

    defaultConfig {
        applicationId = "ai.project.readonly"
        minSdk = 26
        targetSdk = 36
        versionCode = 3
        versionName = "0.0.3"
        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
    }

    buildTypes {
        debug {
            buildConfigField("String", "API_BASE_URL", "\"http://10.0.2.2:8000\"")
        }
        release {
            isMinifyEnabled = false
            buildConfigField("String", "API_BASE_URL", releaseApiBaseUrl.asBuildConfigString())
        }
    }

    lint {
        abortOnError = true
        checkReleaseBuilds = true
        warningsAsErrors = true
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    kotlinOptions {
        jvmTarget = "17"
    }

    buildFeatures {
        buildConfig = true
    }
}

dependencies {
    testImplementation("junit:junit:4.13.2")
    testImplementation("org.json:json:20260719")
}

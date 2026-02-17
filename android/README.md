# Project AI - Android Application

## Overview

Production-ready Android application for interacting with the **Project AI Governance Kernel**. Built with Jetpack Compose, Material Design 3, and TARL governance enforcement.

## Features

✅ **Triumvirate Dashboard**

- Real-time kernel status monitoring
- Pillar health visualization (Galahad, Cerberus, Codex Deus)
- Recent governance decisions

✅ **Intent Submission**

- Submit requests for Triumvirate evaluation
- Actor type selection (Human, Agent, System)
- Action type selection (Read, Write, Execute, Mutate)
- Real-time governance verdict display

✅ **Audit Log Viewer**

- Immutable decision history
- Cryptographic intent hashing
- Timestamp tracking

✅ **TARL Rule Explorer**

- View governance policies
- Risk level indicators
- Allowed actor permissions

## Technology Stack

- **Language**: Kotlin
- **UI**: Jetpack Compose + Material Design 3
- **Architecture**: MVVM + Clean Architecture
- **DI**: Hilt (Dagger)
- **Networking**: Retrofit + OkHttp
- **Async**: Kotlin Coroutines + Flow
- **Navigation**: Jetpack Navigation

## Prerequisites

- Android Studio Hedgehog (2023.1.1) or later
- JDK 17
- Android SDK 34
- Minimum Android 8.0 (API 26)

## Setup

### 1. Configure Backend URL

The app connects to the Governance Kernel API. By default:

- **Emulator**: `http://10.0.2.2:8001`
- **Physical Device**: Update `API_BASE_URL` in `app/build.gradle`

### 2. Start Backend Server

```bash
cd ..
python start_api.py
```

### 3. Build & Run

```bash
./gradlew assembleDebug
./gradlew installDebug
```

## API Integration

### Endpoints

```
GET  /health    - Kernel status
GET  /tarl      - Governance rules
GET  /audit     - Decision history
POST /intent    - Submit for evaluation
POST /execute   - Execute under governance
```

## Screens

1. **Dashboard** - Kernel status & Triumvirate visualization
2. **Submit Intent** - Governance request submission
3. **Audit Log** - Decision history viewer
4. **TARL Rules** - Policy explorer

## Security

- TARL enforcement on all requests
- Cryptographic intent hashing
- Immutable audit logging
- Fail-closed architecture

---

**Production-ready governed mobile interface.**

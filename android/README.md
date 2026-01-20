`# Android APK Integration

This repository now includes a minimal Android project setup for CI/CD integration and future development.

## 🎯 Current Status

The Android project structure is now complete with:
- ✅ Gradle build system (v8.5)
- ✅ Minimal Android app module with MainActivity
- ✅ AndroidX support enabled
- ✅ CI/CD workflow integration (`.github/workflows/android.yml`)
- ✅ Cross-platform build scripts (gradlew/gradlew.bat)

## 📂 Project Structure

```
Project-AI/
├── build.gradle              # Root build configuration
├── settings.gradle           # Project settings
├── gradle.properties         # Gradle properties (AndroidX enabled)
├── gradlew                   # Unix build script
├── gradlew.bat              # Windows build script
├── gradle/wrapper/          # Gradle wrapper files
└── app/                     # Main Android app module
    ├── build.gradle         # App module build config
    ├── proguard-rules.pro   # ProGuard configuration
    └── src/main/
        ├── AndroidManifest.xml
        ├── java/com/projectai/app/MainActivity.java
        └── res/values/strings.xml
```

## 🚀 Building the Project

```bash
# Grant execute permission (Linux/Mac)
chmod +x gradlew

# Build the project
./gradlew build

# Build APK
./gradlew assembleDebug

# Install to connected device
./gradlew installDebug
```

## ✨ Latest Features Available for Integration

The desktop version now includes these powerful new features:
- **Cloud Sync**: Encrypted cross-device synchronization with device management and conflict resolution
- **Advanced ML Models**: RandomForest, GradientBoosting, and Neural Networks for intent/sentiment/behavior prediction
- **Plugin System**: Dynamic plugin loading with hooks and lifecycle management

## 🔧 Integration Plan
- The Android app will communicate with the main program and web backend via API endpoints and shared data models.
- All integration points will be documented and stubbed for easy merging into the main branch when development begins.

## 📋 Next Steps for Full Integration

## Program Functions for Integration

Below is a list of core functions and features from the Project-AI program that should
be considered for integration with the Android APK app:

### Core Modules

- **User Management**: authenticate, create_user, get_user_data, list_users, delete_user, set_password, update_user
- **Cloud Sync**: sync_user_data, fetch_user_data, list_user_devices, resolve_conflicts, auto_sync
- **ML Models**: train_intent_classifier, predict_intent, analyze_sentiment, predict_user_behavior, save_model, load_model, get_model_info
- **Image Generation**: generate_image, get_available_styles, get_style_description, set_content_filtering
- **Learning Paths**: generate_path, save_path, get_saved_paths
- **Location Tracker**: encrypt_location, decrypt_location, get_location_from_ip, get_location_from_coords, save_location_history, get_location_history, clear_location_history
- **Intent Detection**: train, predict, save_model, load_model
- **Emergency Alert**: add_emergency_contact, send_alert, log_alert, get_alert_history
- **Data Analysis**: load_data, get_summary_stats, create_visualization, perform_clustering
- **Security Resources**: get_resources_by_category, get_all_categories, get_repo_details, save_favorite, get_favorites
- **Plugin System**: initialize_plugin, execute_plugin, register_hook, trigger_hook, list_plugins, unload_plugin, reload_plugin, get_plugin_config, save_plugin_config

### GUI Modules (for reference)

- **Dashboard**: setup_ui, open_settings_dialog, setup_chat_tab, setup_tasks_tab, setup_learning_paths_tab, setup_data_analysis_tab, setup_security_tab, setup_location_tab, setup_emergency_tab, send_message, process_message, add_task, update_persona
- **Login**: create_admin_account, try_login
- **Settings Dialog**: get_values, load_settings, save_settings
- **Image Generation UI**: run, _generate_image, _on_image_generated, _on_error, _save_image
- **User Management UI**: refresh_user_list, on_user_selected, create_user_dialog, delete_user, toggle_approve, reset_password, save_changes

### Main Entrypoints

- setup_environment
- main

Refer to the respective Python files in `src/app/core/`, `src/app/gui/`, and
`src/app/main.py` for implementation details.

## Integration Requirements

### API Endpoints (to be implemented)
- `/api/auth/login` - User authentication
- `/api/users` - User management (CRUD)
- `/api/sync` - Cloud sync operations
- `/api/ml/predict` - ML model predictions
- `/api/image/generate` - Image generation
- `/api/learning-paths` - Learning path management
- `/api/location` - Location tracking
- `/api/emergency` - Emergency alerts
- `/api/data-analysis` - Data analysis operations
- `/api/security` - Security resources

### Data Models (examples)
- **User**: `{ username, password, email, profile, ... }`
- **ImageRequest**: `{ prompt, style, width, height, ... }`
- **LearningPath**: `{ interest, skill_level, steps, ... }`
- **Location**: `{ latitude, longitude, timestamp, ... }`
- **Alert**: `{ username, location, message, timestamp }`

### Integration Notes
- Use HTTPS for all API communication.
- Authentication should use secure tokens (JWT or similar).
- Data models must match backend Python structures for seamless integration.
- Document any changes to API contracts in this README.

---

---
*This branch is a stub for integration only. No actual integration is performed yet.*

## Formatting & Contribution

If you're contributing to the project, please format code before opening a PR.

PowerShell (Python):
```powershell
$env:PYTHONPATH='src'
python -m pip install ruff black isort
isort src tests --profile black
ruff check src tests --fix
black src tests
```

Frontend (if editing web files):
```powershell
cd web/frontend
npm install
npm run format
```


---

**Repository note:** Last updated: 2025-11-26 (automated)

<!-- last-updated-marker -->

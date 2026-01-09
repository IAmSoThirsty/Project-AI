# Quick Start Guide - Project-AI Dashboard

## 🚀 Launch Commands

### Standard Launch (Windows PowerShell)
```powershell
cd C:\Users\Jeremy\Documents\GitHub\Project-AI
$env:PYTHONPATH='src'
python src/app/main.py
```

### Alternative Launch Methods
```powershell
# Method 1: Using python module execution
python -m app.main

# Method 2: With environment file
python src/app/main.py  # Automatically loads .env file
```

---

## ✅ Pre-Launch Checklist

- [x] All dependencies installed (cryptography, requests, scikit-learn, geopy)
- [x] All tests passing (6/6 - 100%)
- [x] All new modules importable
- [x] Documentation updated
- [x] READMEs updated (main, web, android)

---

## 🎯 What You Can Do Now

1. **Launch the Dashboard** - All features integrated and working
2. **Test Cloud Sync** - If you have an API endpoint configured
3. **Train ML Models** - Use the advanced ML features
4. **Create Plugins** - Extend functionality with custom plugins
5. **Use All Original Features**:
   - User Management
   - Image Generation
   - Learning Paths
   - Data Analysis
   - Security Resources
   - Location Tracking
   - Emergency Alerts
   - Intent Detection

---

## 🔧 Environment Variables (Optional)

Add these to your `.env` file for enhanced features:

```env
# OpenAI Integration (for learning paths & chat)
OPENAI_API_KEY=sk-your-key-here

# Email Alerts (for emergency features)
SMTP_USERNAME=your_email@example.com
SMTP_PASSWORD=your_app_password_here

# Encryption (auto-generated if not provided)
FERNET_KEY=your-base64-key-here

# Cloud Sync (NEW!)
CLOUD_SYNC_URL=https://your-api.com/sync

# Directories (optional)
DATA_DIR=data
LOG_DIR=logs
```

---

## 📊 System Architecture

```
Project-AI/
├── src/app/
│   ├── main.py                    # Entry point
│   ├── core/                      # Business logic
│   │   ├── cloud_sync.py         # NEW: Cloud synchronization
│   │   ├── ml_models.py          # NEW: Advanced ML models
│   │   ├── plugin_system.py      # NEW: Plugin framework
│   │   ├── dashboard_methods.py  # NEW: Dashboard handlers
│   │   ├── user_manager.py
   │   ├── image_generator.py
   │   ├── learning_paths.py
   │   ├── data_analysis.py
   │   ├── security_resources.py
   │   ├── location_tracker.py
   │   ├── emergency_alert.py
   │   └── intent_detection.py
   │   └── intent_detection.py
│   └── gui/                       # User interface
│       ├── dashboard.py           # UPDATED: Integrated new features
│       ├── login.py               # FIXED: Layout issues
│       ├── image_generation.py    # FIXED: Thread issues
│       ├── settings_dialog.py
       └── user_management.py
├── tests/                         # Test suite (6/6 passing)
├── data/                          # User data storage
├── plugins/                       # Plugin directory (NEW!)
└── requirements.txt               # All dependencies

---

``` 
``` 

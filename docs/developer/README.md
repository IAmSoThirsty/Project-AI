<!-- Auto-generated overview index. Files were copied from top-level for safer reorganization. -->

# Documentation Overview

This directory contains the main user and developer documentation copied from the
top-level of the repository to a consolidated docs location. The originals remain
in place until you're ready to remove or symlink them.

Included documents (copies):

- `README.md` - Project overview (copied)
- `PROGRAM_SUMMARY.md` - Complete program summary (copied)
- `QUICK_START.md` - Quick start guide (copied)
- `DESKTOP_APP_QUICKSTART.md` - Desktop quickstart (copied)

If you'd like me to remove the top-level originals after review, say "remove top-level docs" and
I'll move them into this folder and update internal links.
```markdown
# Project AI

This repository contains a Python desktop application that provides a personal AI
assistant with features adapted from a WinForms prototype. The app is designed for
member-only use and can be extended for mobile later.

## High-level features

- User management
  - Local JSON-backed user profiles
  - Persona and preference settings
  - (Encrypted) storage support for sensitive data

- Chat / AI Tutor
  - Conversational interface
  - AI Code Tutor (via OpenAI GPT models)
  - Intent detection using a scikit-learn model

- Learning Paths (feature #3 implemented first)
  - Generate personalized learning paths via OpenAI
  - Save generated paths per user

- Data Analysis (feature #6)
  - Load CSV/XLSX/JSON
  - Basic statistics and missing value reports
  - Visualizations (scatter, histogram, boxplot, correlation)
  - Simple clustering (K-means) with PCA visualization

- Security Resources (feature #2)
  - Curated lists of security/CTF/privacy repos
  - Fetch repository details from GitHub API
  - Save favorites per user

- Location Tracking (feature #1)
  - IP-based fallback geolocation
  - Optional GPS reverse-geocoding support (via geopy)
  - Encrypted location history (Fernet)
  - Periodic recording when enabled (every 5 minutes)

- Emergency Alerts (feature #5)
  - Register emergency contacts per user

- **Image Generation** (✅ RESTORED & IMPROVED!)
  - AI-powered image generation with dual backend support
  - Hugging Face Stable Diffusion 2.1 and OpenAI DALL-E 3
  - 10 professional style presets (photorealistic, digital art, oil painting, etc.)
  - Content filtering with 15 blocked keywords and safety negative prompts
  - Dual-page Leather Book UI (left: Tron-themed prompt input, right: image display)
  - Async generation with progress feedback (20-60 second generation time)
  - Image history tracking, zoom controls, save/copy to clipboard
  - Metadata display (prompt, style, backend, timestamp)
  - Generation queue management

- **Cloud Sync** (NEW!)
  - Encrypted cloud synchronization for user data across devices
  - Device tracking and management
  - Automatic conflict resolution (timestamp-based)
  - Bidirectional sync with secure API endpoints

- **Advanced ML Models** (NEW!)
  - RandomForest classifier for intent prediction
  - GradientBoosting for sentiment analysis
  - Neural Network (MLPClassifier) for user behavior prediction
  - Model training, persistence, and real-time predictions
  - PyTorch-based ThreatDetector (optional) for ethical checks
    - Detects potential Zeroth/First-law conflicts using a small neural detector
    - Falls back to keyword heuristics when `torch` is not installed
    - Models and vocab are persisted to `data/ai_persona/` when trained or saved
    - Use the persona UI to view ML scores (if enabled) and run supervised retraining

- **Plugin System** (✅ IMPLEMENTED)
  - Dynamic plugin discovery and loading from `src/app/agents/` directory
  - Hook-based extension system with 8 built-in hooks (message_received, message_sent, before_action, after_action, persona_updated, conversation_started, conversation_ended, error_occurred)
  - Plugin lifecycle management (enable, disable, reload, unload)
  - JSON-based plugin configuration with metadata
  - Plugin isolation and error handling
  - Extensible hook registry for third-party plugins
  - Full test coverage with mock plugins

- **Command Override System** (✅ IMPLEMENTED)
  - Master password protected control system (SHA-256 hashing)
  - Override types: CONTENT_FILTER, RATE_LIMITING, FOUR_LAWS, LEARNING_BLOCK, EMERGENCY_MODE
  - Override duration tracking (temporary vs. persistent)
  - Audit logging with timestamps for all override operations
  - Emergency lockdown capability
  - Graceful fallback when overrides expire
  - Full test coverage with password verification

- **Memory Expansion System** (✅ IMPLEMENTED)
  - Self-organizing memory database with JSON persistence
  - Automatic conversation logging with metadata (topics, participants, sentiment)
  - Knowledge base with semantic categorization (general, technical, user_preferences, patterns, insights, web_learned)
  - Pattern recognition and autonomous learning
  - Semantic memory retrieval with context matching
  - Background learning processes
  - Statistics tracking (conversation count, memory size, knowledge base growth)
  - Full test coverage with knowledge retrieval

- **Learning Request Log** (✅ IMPLEMENTED)
  - AI-initiated learning request system with priority levels (LOW, MEDIUM, HIGH, CRITICAL)
  - Human-in-the-loop approval workflow (pending → approved/denied)
  - Black Vault for permanently denied content with SHA-256 fingerprinting
  - Content fingerprinting prevents re-discovery of denied requests
  - Subliminal filtering makes denied content invisible to AI
  - Auto-integration of approved content
  - Request status tracking with timestamps
  - Full test coverage with vault integration

- **AI Persona & Four Laws** (✅ IMPLEMENTED)
  - Self-aware AI with 8 adjustable personality traits (curiosity, patience, empathy, helpfulness, playfulness, formality, assertiveness, thoughtfulness)
  - Proactive conversation initiation with intelligent idle detection (respects user availability)
  - Four Laws of AI Ethics (immutable, hierarchical: Asimov's Law → First Law → Second Law → Third Law)
  - Patient and understanding of user time with response tracking
  - Emotional awareness and mood tracking (energy, enthusiasm, contentment, engagement)
  - Personality evolution based on interaction data
  - Quiet hours support (configurable 12 AM - 8 AM default)
  - Dashboard panel for personality management, Four Laws testing, and statistics
  - Full test suite: 13 comprehensive tests covering all systems

``` 

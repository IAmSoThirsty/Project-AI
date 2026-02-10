# Portable AI Application Guide

## Vision

Project-AI is designed to be a **fully portable, privacy-first AI application** that can be deployed as a single executable with zero installation requirements and complete offline functionality.

## Core Principles

### 1. Zero Installation Required

**Goal:** Users should be able to download a single file and run the application immediately without any setup process.

**Implementation:**

- Single-exe packaging (PyInstaller, Electron, or Go binary)
- All dependencies bundled within the executable
- No external installers or setup wizards
- Portable data directory alongside executable

### 2. Privacy-First Design

**Goal:** All user data and AI processing happens locally with zero cloud dependency.

**Features:**

- No telemetry or analytics
- No cloud sync (optional only)
- No external API calls for core functionality
- Encrypted local storage (Fernet encryption)
- User data never leaves the device

### 3. Embedded AI Models

**Goal:** Include AI models within the application package for complete offline operation.

**Approach:**

- Bundle lightweight models (TinyLLM, DistilGPT, MobileBERT)
- Quantized models for reduced size (4-bit, 8-bit)
- Model files in `models/` directory within package
- On-demand model loading (lazy initialization)

**Model Options:**

- **Text Generation:** GPT-2 (124M), DistilGPT2 (82M)
- **Embeddings:** MiniLM-L6 (22M)
- **Classification:** DistilBERT (66M)
- Total package size target: <500MB with models

### 4. Offline Functionality

**Goal:** Application works fully without internet connection.

**Core Features Available Offline:**

- AI persona interactions (local models)
- Memory system (local SQLite)
- Data analysis (pandas, scikit-learn)
- Image generation (local Stable Diffusion - optional large package)
- Plugin system (sandboxed execution)
- All TARL governance and Triumvirate logic

**Optional Online Features:**

- Cloud AI models (OpenAI, DeepSeek) - fallback to local if offline
- Plugin marketplace updates
- Software updates
- Cross-device sync (opt-in)

## Packaging Strategies

### Python (PyInstaller)

```bash
# Single-file executable
pyinstaller --onefile \
  --add-data "models:models" \
  --add-data "config:config" \
  --hidden-import=sklearn \
  --name=ProjectAI \
  src/app/main.py
```

**Pros:**

- Native Python
- Easy development
- Cross-platform

**Cons:**

- Larger file size (~200-300MB base)
- Slower startup time
- Antivirus false positives

### Electron (Desktop App)

```bash
# Package with electron-builder
npm run build:portable

# Creates portable .exe (Windows), .app (macOS), .AppImage (Linux)
```

**Pros:**

- Beautiful UI (web technologies)
- Cross-platform consistency
- Fast iteration

**Cons:**

- Larger package size (~150-200MB without models)
- Higher memory usage

### Go Binary (Future)

**Pros:**

- Smallest binary size (~10-50MB)
- Fastest startup
- Native performance

**Cons:**

- Requires rewrite from Python
- More complex AI model integration

## Architecture

```
ProjectAI-Portable/
├── ProjectAI.exe           # Single executable
├── models/                 # AI models (bundled or extracted on first run)
│   ├── gpt2-small/
│   ├── minilm/
│   └── distilbert/
├── data/                   # User data (created on first run)
│   ├── memory.db          # SQLite database
│   ├── personas/          # AI personas
│   ├── plugins/           # User plugins
│   └── cache/             # Temporary files
└── config/                # Application config
    ├── settings.json
    └── .env.local
```

## Installation Flow

1. **Download:** User downloads single file (e.g., `ProjectAI-v1.0.0-portable.exe`)
2. **Extract:** (if using compressed format) Unzip to any location
3. **Run:** Double-click executable
4. **First Launch:** Application creates `data/` and `config/` directories
5. **Ready:** Application is immediately usable

## Data Portability

### Moving Between Machines

Users can copy the entire application folder to:

- USB drives
- External SSDs
- Cloud storage (for manual sync)
- Network shares

All settings, data, and AI personas move with it.

### Data Structure

```
data/
├── memory.db              # Full conversation history
├── personas/
│   ├── default.json      # AI personality configs
│   └── custom.json
├── learning/
│   ├── approved/         # Approved learning content
│   └── blackvault/       # Denied content (encrypted)
└── exports/
    └── backups/          # User data backups
```

## Security in Portable Mode

### Encryption at Rest

- All sensitive data encrypted with Fernet (AES-128)
- Master key derived from user password (optional)
- Keys stored in secure OS keychain when available
- Fallback to encrypted file storage

### Sandboxing

- Plugins run in restricted Python environment
- File system access limited to `data/` directory
- Network access controlled by user permissions
- TARL policies enforce all operations

## Performance Optimization

### Fast Startup

- Lazy loading of AI models (load on first use)
- Parallel initialization of non-dependent systems
- Cached configuration
- Incremental model loading

### Memory Efficiency

- Model quantization (4-bit/8-bit)
- Dynamic unloading of unused models
- Shared embeddings between features
- Configurable cache sizes

## Platform-Specific Notes

### Windows

- Single `.exe` file
- Optional installer for Start Menu/Desktop shortcuts
- Windows Defender exclusion may be needed

### macOS

- `.app` bundle or `.dmg` disk image
- Code signing required for notarization
- Gatekeeper bypass instructions for unsigned builds

### Linux

- `.AppImage` (single file, no installation)
- Or `.deb`/`.rpm` packages
- Permissions: `chmod +x ProjectAI.AppImage`

## Update Strategy

### Manual Updates (Default)

- Download new version
- Replace old executable
- Data directory preserved

### Auto-Update (Optional)

- Check for updates on startup
- Download in background
- Prompt user to restart
- Preserves all user data

## Size Targets

| Package | Size Target | Contents |
|---------|-------------|----------|
| Minimal | ~150MB | Core + tiny models |
| Standard | ~500MB | Core + standard models |
| Full | ~2GB | Core + large models + SD |

## Future Enhancements

- [ ] WASM version for browser (privacy-focused web deployment)
- [ ] Mobile apps (iOS/Android) with same portable data format
- [ ] Encrypted P2P sync between devices (no cloud required)
- [ ] Model marketplace (download additional models as needed)
- [ ] Plugin marketplace (community extensions)

## Development Commands

```bash
# Build portable package
python scripts/build_portable.py

# Test portable mode
python scripts/test_portable.py

# Optimize model sizes
python scripts/quantize_models.py
```

---

**The portable app vision ensures Project-AI can be used anywhere, by anyone, without compromising privacy or requiring internet connectivity.**

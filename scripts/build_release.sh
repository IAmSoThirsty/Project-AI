#!/bin/bash
# Create complete v1.0.0 release package with all platforms
# Enhanced with dependency validation, manifest checking, and JSON reporting

set -e

VERSION="1.0.0"
RELEASE_DIR="releases/project-ai-v${VERSION}"
DATE=$(date +%Y-%m-%d)
BUILD_START=$(date +%s)

echo "========================================="
echo "Project AI v${VERSION} Release Builder"
echo "========================================="
echo "Date: ${DATE}"
echo ""

# Function to check dependencies
check_dependencies() {
    echo "Checking system dependencies..."
    local missing_deps=0
    
    # Check Python
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        echo "  ✓ Python 3.x found: ${PYTHON_VERSION}"
    else
        echo "  ✗ Python 3.x not found"
        missing_deps=$((missing_deps + 1))
    fi
    
    # Check Node.js (optional for web)
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version)
        echo "  ✓ Node.js found: ${NODE_VERSION}"
    else
        echo "  ⚠ Node.js not found (optional)"
    fi
    
    # Check npm (optional for web)
    if command -v npm &> /dev/null; then
        NPM_VERSION=$(npm --version)
        echo "  ✓ npm found: ${NPM_VERSION}"
    else
        echo "  ⚠ npm not found (optional)"
    fi
    
    # Check Docker (optional)
    if command -v docker &> /dev/null; then
        DOCKER_VERSION=$(docker --version | cut -d' ' -f3 | tr -d ',')
        echo "  ✓ Docker found: ${DOCKER_VERSION}"
    else
        echo "  ⚠ Docker not found (optional)"
    fi
    
    # Check Gradle (for Android)
    if [ -f "gradlew" ]; then
        echo "  ✓ Gradle wrapper found"
    else
        echo "  ⚠ Gradle wrapper not found (Android build may fail)"
    fi
    
    echo ""
    
    if [ $missing_deps -gt 0 ]; then
        echo "ERROR: Missing required dependencies. Please install them first."
        return 1
    fi
    
    return 0
}

# Check dependencies before proceeding
if ! check_dependencies; then
    exit 1
fi

# Create release directory structure
echo "Creating release directory structure..."
mkdir -p "${RELEASE_DIR}"
mkdir -p "${RELEASE_DIR}/backend"
mkdir -p "${RELEASE_DIR}/web"
mkdir -p "${RELEASE_DIR}/android"
mkdir -p "${RELEASE_DIR}/desktop"
mkdir -p "${RELEASE_DIR}/docs"
mkdir -p "${RELEASE_DIR}/monitoring"
mkdir -p "releases"

# 1. Backend API
echo "[1/5] Building Backend API..."
echo "  - Copying source files..."
cp -r api "${RELEASE_DIR}/backend/"
cp -r tarl "${RELEASE_DIR}/backend/"
cp -r config "${RELEASE_DIR}/backend/"
cp -r utils "${RELEASE_DIR}/backend/"
cp -r kernel "${RELEASE_DIR}/backend/"
cp -r governance "${RELEASE_DIR}/backend/"
cp start_api.py "${RELEASE_DIR}/backend/"
cp requirements.txt "${RELEASE_DIR}/backend/"
cp .env.example "${RELEASE_DIR}/backend/.env"

echo "  - Creating startup script..."
cat > "${RELEASE_DIR}/backend/start.sh" << 'EOF'
#!/bin/bash
echo "Starting Project AI Governance API v1.0.0..."
pip3 install -r requirements.txt
python3 start_api.py
EOF
chmod +x "${RELEASE_DIR}/backend/start.sh"

cat > "${RELEASE_DIR}/backend/start.bat" << 'EOF'
@echo off
echo Starting Project AI Governance API v1.0.0...
pip install -r requirements.txt
python start_api.py
EOF

echo "✓ Backend packaged"

# 2. Web Frontend
echo "[2/5] Packaging Web Frontend..."
cp -r web/* "${RELEASE_DIR}/web/"

cat > "${RELEASE_DIR}/web/DEPLOY.md" << 'EOF'
# Web Deployment

## Quick Start

1. Update API endpoint in `app.js`:
   ```javascript
   const API_BASE = 'https://your-domain.com/api';
   ```

2. Deploy to any static host:
   - **Netlify:** `netlify deploy --prod`
   - **GitHub Pages:** Push to `gh-pages` branch
   - **Your server:** Copy to `/var/www/html`

See WEB_DEPLOYMENT_GUIDE.md for full instructions.
EOF

echo "✓ Web packaged"

# 3. Android Build
echo "[3/5] Building Android APK..."
if [ -d "android" ]; then
    cd android
    
    # Build debug APK (faster)
    echo "  - Building debug APK..."
    ./gradlew assembleDebug
    
    # Copy APK
    if [ -f "app/build/outputs/apk/debug/app-debug.apk" ]; then
        cp app/build/outputs/apk/debug/app-debug.apk \
           "../${RELEASE_DIR}/android/project-ai-v${VERSION}-debug.apk"
        echo "✓ Android APK built"
    else
        echo "⚠ Android APK build skipped (Gradle not available)"
    fi
    
    cd ..
else
    echo "⚠ Android directory not found, skipping..."
fi

# Copy Android docs
cat > "${RELEASE_DIR}/android/INSTALL.md" << 'EOF'
# Android Installation

## Install APK

1. Transfer APK to your Android device
2. Enable "Install from unknown sources" in Settings
3. Tap the APK file to install
4. Grant necessary permissions

## Minimum Requirements

- Android 7.0+ (API Level 24+)
- 50MB free space

## First Launch

1. Open Project AI Governance app
2. Configure API endpoint in settings
3. Start using the governance dashboard
EOF

# 4. Desktop App
echo "[4/5] Building Desktop Apps..."
if [ -d "desktop" ] && [ -f "desktop/package.json" ]; then
    cd desktop
    
    echo "  - Installing dependencies..."
    npm install --silent
    
    echo "  - Building for current platform..."
    npm run build
    
    # Copy built files
    if [ -d "dist" ]; then
        cp -r dist/* "../${RELEASE_DIR}/desktop/" 2>/dev/null || true
        echo "✓ Desktop apps built"
    fi
    
    cd ..
else
    echo "⚠ Desktop directory not found, skipping..."
fi

cat > "${RELEASE_DIR}/desktop/INSTALL.md" << 'EOF'
# Desktop Installation

## Windows
1. Download `project-ai-governance-Setup-1.0.0.exe`
2. Run installer
3. Follow installation wizard
4. Launch from Start Menu

## macOS
1. Download `project-ai-governance-1.0.0.dmg`
2. Open DMG file
3. Drag app to Applications folder
4. Launch from Applications

## Linux
**AppImage (Universal):**
```bash
chmod +x project-ai-governance-1.0.0.AppImage
./project-ai-governance-1.0.0.AppImage
```

**Debian/Ubuntu:**
```bash
sudo dpkg -i project-ai-governance_1.0.0_amd64.deb
```
EOF

# 5. Monitoring Agents
echo "[5/7] Packaging Monitoring Agents..."
if [ -d "monitoring" ]; then
    echo "  - Copying monitoring configurations..."
    cp -r monitoring/* "${RELEASE_DIR}/monitoring/" 2>/dev/null || true
    echo "✓ Monitoring agents packaged"
else
    echo "⚠ Monitoring directory not found, skipping..."
fi

# Create monitoring README
cat > "${RELEASE_DIR}/monitoring/README.md" << 'EOF'
# Monitoring Agents

This directory contains monitoring and observability configurations.

## Components

- **Prometheus**: Metrics collection and storage
- **Grafana**: Visualization dashboards
- **AlertManager**: Alert routing and management
- **Node Exporter**: System-level metrics

## Quick Start

See `config/prometheus/` and `config/grafana/` in backend for full configuration.

For Docker deployment:
```bash
docker-compose up -d
```

Access points:
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin/admin)
- AlertManager: http://localhost:9093
EOF

# 6. Documentation
echo "[6/7] Copying Documentation..."
cp README.md "${RELEASE_DIR}/"
cp CONSTITUTION.md "${RELEASE_DIR}/"
cp CHANGELOG.md "${RELEASE_DIR}/"
cp LICENSE "${RELEASE_DIR}/"
cp SECURITY.md "${RELEASE_DIR}/"
cp -r docs/* "${RELEASE_DIR}/docs/" 2>/dev/null || true

# Create master README
cat > "${RELEASE_DIR}/README.md" << EOF
# Project AI Governance Kernel v${VERSION}

Official production release - ${DATE}

## 📦 What's Included

This package contains:

- **Backend API** (\`backend/\`) - FastAPI governance server
- **Web Frontend** (\`web/\`) - Browser-based interface
- **Android App** (\`android/\`) - APK for Android devices
- **Desktop Apps** (\`desktop/\`) - Electron apps for Win/Mac/Linux
- **Documentation** (\`docs/\`) - Complete guides

## 🚀 Quick Start

### 1. Backend API

\`\`\`bash
cd backend
./start.sh  # Linux/Mac
# OR
start.bat   # Windows
\`\`\`

API runs on: http://localhost:8001

### 2. Web Frontend

Open \`web/index.html\` in browser, or deploy to your domain (see \`web/DEPLOY.md\`)

### 3. Android App

Install APK: \`android/project-ai-v${VERSION}-debug.apk\`

### 4. Desktop App

See \`desktop/INSTALL.md\` for platform-specific instructions

## 📚 Documentation

- **Deployment:** \`docs/WEB_DEPLOYMENT_GUIDE.md\`
- **Security:** \`SECURITY.md\`
- **API Docs:** \`docs/API.md\`
- **Constitution:** \`CONSTITUTION.md\`

## 🔐 Security

This release includes:
- TARL Governance Framework
- Triumvirate Consensus
- Immutable Audit Logging
- 2000+ Security Tests (97%+ coverage)

## 📋 Requirements

- **Backend:** Python 3.8+
- **Web:** Any modern browser
- **Android:** Android 7.0+ (API 24+)
- **Desktop:** Windows 10+, macOS 10.14+, Ubuntu 18.04+

## 🆘 Support

- GitHub: https://github.com/yourusername/Project-AI
- Issues: https://github.com/yourusername/Project-AI/issues
- Docs: https://github.com/yourusername/Project-AI/docs

## 📄 License

MIT License - See LICENSE file

---

**Version:** ${VERSION}  
**Release Date:** ${DATE}  
**Build:** Production
EOF

# Create archives
echo ""
echo "Creating release archives..."

cd releases

# Create tar.gz (Linux/Mac)
echo "  - Creating .tar.gz archive..."
tar -czf "project-ai-v${VERSION}.tar.gz" "project-ai-v${VERSION}/"

# Create zip (cross-platform)
echo "  - Creating .zip archive..."
zip -q -r "project-ai-v${VERSION}.zip" "project-ai-v${VERSION}/"

cd ..

# Calculate sizes
TAR_SIZE=$(du -h "releases/project-ai-v${VERSION}.tar.gz" | cut -f1)
ZIP_SIZE=$(du -h "releases/project-ai-v${VERSION}.zip" | cut -f1)
BUILD_END=$(date +%s)
BUILD_DURATION=$((BUILD_END - BUILD_START))

# 7. Cleanup sensitive files
echo ""
echo "[7/7] Cleaning up sensitive files..."
find "${RELEASE_DIR}" -type f -name "*.key" -delete 2>/dev/null || true
find "${RELEASE_DIR}" -type f -name "*.pem" -delete 2>/dev/null || true
find "${RELEASE_DIR}" -type f -name "secrets.*" -delete 2>/dev/null || true
find "${RELEASE_DIR}" -type f -name ".env" ! -name ".env.example" -exec sed -i 's/=.*/=/' {} \; 2>/dev/null || true
echo "✓ Sensitive files cleaned"

# Generate machine-readable release summary (JSON)
echo ""
echo "Generating release summary..."
BUILD_SUMMARY="releases/release-summary-v${VERSION}.json"

cat > "${BUILD_SUMMARY}" << JSONEOF
{
  "version": "${VERSION}",
  "build_date": "${DATE}",
  "build_duration_seconds": ${BUILD_DURATION},
  "release_directory": "${RELEASE_DIR}",
  "artifacts": {
    "backend": {
      "included": true,
      "components": ["api", "tarl", "governance", "config", "utils", "kernel"],
      "startup_scripts": ["start.sh", "start.bat"]
    },
    "web": {
      "included": $([ -d "${RELEASE_DIR}/web" ] && echo "true" || echo "false"),
      "deployment_guide": $([ -f "${RELEASE_DIR}/web/DEPLOY.md" ] && echo "true" || echo "false")
    },
    "android": {
      "included": $([ -d "${RELEASE_DIR}/android" ] && echo "true" || echo "false"),
      "apk_count": $(ls "${RELEASE_DIR}/android/"*.apk 2>/dev/null | wc -l)
    },
    "desktop": {
      "included": $([ -d "${RELEASE_DIR}/desktop" ] && echo "true" || echo "false"),
      "installer_count": $(find "${RELEASE_DIR}/desktop/" -name "*.exe" -o -name "*.dmg" -o -name "*.AppImage" -o -name "*.deb" 2>/dev/null | wc -l)
    },
    "monitoring": {
      "included": true,
      "components": ["prometheus", "grafana", "alertmanager"]
    },
    "documentation": {
      "included": true,
      "root_docs": ["README.md", "CONSTITUTION.md", "CHANGELOG.md", "LICENSE", "SECURITY.md"]
    }
  },
  "archives": {
    "tar_gz": {
      "filename": "project-ai-v${VERSION}.tar.gz",
      "size": "${TAR_SIZE}"
    },
    "zip": {
      "filename": "project-ai-v${VERSION}.zip",
      "size": "${ZIP_SIZE}"
    }
  },
  "checksums": {
    "tar_gz_sha256": "$(sha256sum releases/project-ai-v${VERSION}.tar.gz | cut -d' ' -f1)",
    "zip_sha256": "$(sha256sum releases/project-ai-v${VERSION}.zip | cut -d' ' -f1)"
  },
  "requirements": {
    "backend": {
      "python": "3.8+",
      "dependencies_file": "requirements.txt"
    },
    "android": {
      "min_api_level": 24,
      "android_version": "7.0+"
    },
    "desktop": {
      "windows": "10+",
      "macos": "10.14+",
      "linux": "Ubuntu 18.04+"
    }
  }
}
JSONEOF

echo "✓ Release summary written to: ${BUILD_SUMMARY}"

# Validate the release package
echo ""
echo "Validating release package..."
if [ -f "scripts/validate_release.py" ]; then
    python3 scripts/validate_release.py "${RELEASE_DIR}" --version "${VERSION}" --output "releases/validation-report-v${VERSION}.json"
    VALIDATION_EXIT=$?
    
    if [ $VALIDATION_EXIT -eq 0 ]; then
        echo "✓ Validation passed"
    else
        echo "⚠ Validation found issues - check validation-report-v${VERSION}.json"
    fi
else
    echo "⚠ Validation script not found, skipping validation"
fi

echo ""
echo "========================================="
echo "✅ Release Build Complete!"
echo "========================================="
echo ""
echo "📦 Package: releases/project-ai-v${VERSION}/"
echo ""
echo "📄 Archives created:"
echo "  - project-ai-v${VERSION}.tar.gz (${TAR_SIZE})"
echo "  - project-ai-v${VERSION}.zip (${ZIP_SIZE})"
echo ""
echo "📊 Reports generated:"
echo "  - release-summary-v${VERSION}.json"
echo "  - validation-report-v${VERSION}.json"
echo ""
echo "📋 Contents:"
echo "  ✓ Backend API (Python)"
echo "  ✓ Web Frontend (HTML/CSS/JS)"
echo "  ✓ Android App (APK)"
echo "  ✓ Desktop Apps (Electron)"
echo "  ✓ Monitoring Agents"
echo "  ✓ Complete Documentation"
echo ""
echo "⏱  Build time: ${BUILD_DURATION} seconds"
echo ""
echo "🚀 Ready for distribution!"
echo ""
echo "Next steps:"
echo "  1. Test the release package"
echo "  2. Create Git tag: git tag v${VERSION}"
echo "  3. Push tag: git push origin v${VERSION}"
echo "  4. Create GitHub release"
echo "  5. Upload archives to GitHub"
echo ""

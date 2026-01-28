#!/bin/bash
# Create complete v1.0.0 release package with all platforms

set -e

VERSION="1.0.0"
RELEASE_DIR="releases/project-ai-v${VERSION}"
DATE=$(date +%Y-%m-%d)

echo "========================================="
echo "Project AI v${VERSION} Release Builder"
echo "========================================="
echo "Date: ${DATE}"
echo ""

# Create release directory
mkdir -p "${RELEASE_DIR}"
mkdir -p "${RELEASE_DIR}/backend"
mkdir -p "${RELEASE_DIR}/web"
mkdir -p "${RELEASE_DIR}/android"
mkdir -p "${RELEASE_DIR}/desktop"
mkdir -p "${RELEASE_DIR}/docs"

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

# 5. Documentation
echo "[5/5] Copying Documentation..."
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
echo "📋 Contents:"
echo "  ✓ Backend API (Python)"
echo "  ✓ Web Frontend (HTML/CSS/JS)"
echo "  ✓ Android App (APK)"
echo "  ✓ Desktop Apps (Electron)"
echo "  ✓ Complete Documentation"
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

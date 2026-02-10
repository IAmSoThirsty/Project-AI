# DEPLOYMENT & RELEASE - Quick Reference

## 🌐 **Web Deployment to Your Domain**

### **Fastest Option: Netlify**
```bash
cd web
netlify deploy --prod
# Add custom domain in dashboard: governance.yourdomain.com
```

### **Your Own Server:**
```bash
# 1. Upload files
scp -r web/* user@yourserver.com:/var/www/html/

# 2. Configure nginx
# 3. Get SSL: certbot --nginx -d governance.yourdomain.com
```

**Full Guide:** `docs/WEB_DEPLOYMENT_GUIDE.md`

---

## 📦 **Download Production Builds v1.0.0**

### **Option 1: Build Locally**

```bash
# Build all platforms
./scripts/build_release.sh

# Output: releases/project-ai-v1.0.0/
#   - backend/    (API server)
#   - web/        (Static site)
#   - android/    (APK)
#   - desktop/    (Win/Mac/Linux apps)
```

### **Option 2: GitHub Release (Recommended)**

1. **Create release:**
```bash
git tag -a v1.0.0 -m "v1.0.0 Production Release"
git push origin v1.0.0
```

2. **Download from GitHub:**
   - Go to: Releases → v1.0.0
   - Download platform-specific builds:
     - `backend-v1.0.0-{platform}.tar.gz`
     - `web-v1.0.0.zip`
     - `project-ai-android-v1.0.0.apk`
     - `project-ai-desktop-{platform}.{ext}`
     - `project-ai-v1.0.0-complete.zip` (all platforms)

**Full Guide:** `docs/PRODUCTION_RELEASE_GUIDE.md`

---

## 🎯 **Platform Selection**

### **Backend API**
- **Linux:** `backend-v1.0.0-linux-x64.tar.gz`
- **Windows:** `backend-v1.0.0-windows-x64.zip`
- **Docker:** `backend-v1.0.0-docker.tar.gz`

### **Web Frontend**
- **Universal:** `web-v1.0.0.zip` (deploy anywhere)

### **Android**
- **APK:** `project-ai-v1.0.0.apk` (Android 7.0+)

### **Desktop**
- **Windows:** `project-ai-Setup-1.0.0.exe`
- **macOS:** `project-ai-1.0.0.dmg`
- **Linux:** `project-ai-1.0.0.AppImage` or `.deb`

---

## 🚀 **Quick Deploy Commands**

### **Web to Domain:**
```bash
# Netlify
netlify deploy --prod --dir=web

# Your server
rsync -avz web/ user@server:/var/www/governance/
```

### **Backend to Server:**
```bash
# Copy files
scp -r backend user@server:/opt/project-ai/

# On server
cd /opt/project-ai
pip3 install -r requirements.txt
python3 start_api.py
```

### **Docker (Full Stack):**
```bash
docker-compose up -d
# Access: http://localhost:8000 (web) & :8001 (api)
```

---

## 📋 **Pre-Release Checklist**

```bash
# Run all production checks
make prod-check

# Includes:
# ✅ Tests (97%+ coverage)
# ✅ Linting
# ✅ Security scan
# ✅ Constitutional verification
```

---

## 📦 **Complete Package Contents**

```
project-ai-v1.0.0/
├── backend/           # API server (Python)
├── web/              # Static website
├── android/          # APK installer
├── desktop/          # Native apps
├── docs/             # Documentation
├── README.md         # Quick start
├── CONSTITUTION.md   # Governance guarantees
└── LICENSE           # MIT license
```

---

## 🔗 **Post-Deployment URLs**

After deployment, your app will be available at:

- **Web:** `https://governance.yourdomain.com`
- **API:** `https://governance.yourdomain.com/api`
- **Health:** `https://governance.yourdomain.com/api/health`
- **Docs:** `https://governance.yourdomain.com/api/docs`
- **Grafana:** `https://governance.yourdomain.com:3000`

---

## 📞 **Support**

- **Web Deployment:** See `docs/WEB_DEPLOYMENT_GUIDE.md`
- **Production Builds:** See `docs/PRODUCTION_RELEASE_GUIDE.md`
- **Security:** See `SECURITY.md`
- **Issues:** GitHub Issues

---

**Everything you need to deploy v1.0.0 to production!** 🚀

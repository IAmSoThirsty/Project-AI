# 🌐 Deploy to thirstysprojects.com - Complete Guide

## 🎯 **Deployment Overview**

Deploy the Project AI web interface with mandatory Software Charter to your custom domain: **thirstysprojects.com**

______________________________________________________________________

## 📋 **Pre-Deployment Checklist**

- [ ] Domain registered: `thirstysprojects.com`
- [ ] Hosting provider account active
- [ ] FTP/SFTP or hosting control panel access
- [ ] Web files ready in `web/` directory
- [ ] DNS access for configuration

______________________________________________________________________

## 📦 **Files to Deploy**

### **Required File:**

```
web/
└── index.html  (complete web interface with charter)
```

**File Size:** ~70 KB **Dependencies:** None (pure HTML/CSS/JS)

______________________________________________________________________

## 🚀 **Deployment Methods**

Choose the method that matches your hosting setup:

### **Method 1: cPanel / File Manager (Recommended for Beginners)**

### **Method 2: FTP/SFTP Upload**

### **Method 3: Git Deploy (Advanced)**

### **Method 4: Netlify/Vercel (Easiest)**

______________________________________________________________________

## 📘 **Method 1: cPanel / File Manager**

### **Step 1: Access cPanel**

1. Go to your hosting provider's cPanel
1. Log in with your credentials
1. Navigate to **File Manager**

### **Step 2: Navigate to Web Root**

1. Open `public_html/` (or `www/` or `htdocs/`)
1. This is your web root directory

### **Step 3: Clean Existing Files (Optional)**

```
Option A: Deploy to root (thirstysprojects.com)

- Delete existing index.html
- Upload new index.html

Option B: Deploy to subdirectory (thirstysprojects.com/project-ai)

- Create folder: project-ai/
- Upload index.html into project-ai/

```

### **Step 4: Upload Files**

1. Click **Upload** button
1. Select: `web/index.html`
1. Wait for upload to complete

### **Step 5: Set Permissions**

1. Right-click `index.html`
1. Set permissions: `644` (rw-r--r--)
1. Click **Change Permissions**

### **Step 6: Test**

- Visit: `https://thirstysprojects.com`
- Verify charter section loads
- Test timer functionality

______________________________________________________________________

## 📘 **Method 2: FTP/SFTP Upload**

### **Step 1: Get FTP Credentials**

From your hosting provider, obtain:

- FTP Host: `ftp.thirstysprojects.com` (or IP)
- Username: Your FTP username
- Password: Your FTP password
- Port: 21 (FTP) or 22 (SFTP)

### **Step 2: Install FTP Client**

**Option A: FileZilla (Free)**

```bash

# Download from: https://filezilla-project.org/

# Install and open

```

**Option B: WinSCP (Windows, Free)**

```bash

# Download from: https://winscp.net/

# Install and open

```

### **Step 3: Connect via FTP**

**FileZilla:**

1. Click **File → Site Manager**
1. Click **New Site**
1. Enter:
   - Protocol: `FTP` or `SFTP`
   - Host: `ftp.thirstysprojects.com`
   - Port: `21` (FTP) or `22` (SFTP)
   - User: Your username
   - Password: Your password
1. Click **Connect**

**Command Line (alternative):**

```bash

# Using SFTP

sftp username@thirstysprojects.com

# Using FTP

ftp ftp.thirstysprojects.com
```

### **Step 4: Navigate to Web Root**

```bash

# Common paths:

cd public_html/

# or

cd www/

# or

cd htdocs/
```

### **Step 5: Upload**

**FileZilla:**

1. Local side: Navigate to `web/` folder
1. Remote side: Navigate to `public_html/`
1. Drag `index.html` to remote side

**Command Line:**

```bash
put web/index.html index.html
chmod 644 index.html
quit
```

### **Step 6: Verify**

- Visit: `https://thirstysprojects.com`
- Check all features work

______________________________________________________________________

## 📘 **Method 3: Git Deploy (Advanced)**

If your hosting provider supports Git deployment:

### **Step 1: SSH into Server**

```bash
ssh username@thirstysprojects.com
```

### **Step 2: Navigate to Web Root**

```bash
cd public_html/

# or wherever your web root is

```

### **Step 3: Clone or Pull Repository**

**Option A: First Time**

```bash
git clone https://github.com/IAmSoThirsty/Project-AI.git temp
cp temp/web/index.html ./index.html
rm -rf temp
```

**Option B: Update Existing**

```bash
cd Project-AI
git pull origin main
cp web/index.html ../public_html/index.html
```

### **Step 4: Set Permissions**

```bash
chmod 644 index.html
```

### **Step 5: Verify**

```bash
curl https://thirstysprojects.com | head -20
```

______________________________________________________________________

## 📘 **Method 4: Netlify/Vercel (Easiest)**

### **Option A: Netlify**

#### **Via Netlify UI:**

1. Go to: https://app.netlify.com
1. Click **Add new site → Deploy manually**
1. Drag `web/` folder onto page
1. Wait for deployment
1. Click **Domain settings**
1. Add custom domain: `thirstysprojects.com`
1. Follow DNS configuration steps

#### **Via Netlify CLI:**

```bash

# Install

npm install -g netlify-cli

# Login

netlify login

# Deploy

cd web/
netlify deploy --prod

# Add custom domain (in Netlify dashboard)

```

#### **DNS Configuration for Netlify:**

Add these DNS records at your domain registrar:

```
Type: A
Name: @
Value: 75.2.60.5

Type: CNAME
Name: www
Value: [your-site].netlify.app
```

### **Option B: Vercel**

#### **Via Vercel UI:**

1. Go to: https://vercel.com
1. Click **New Project**
1. Import from Git: `IAmSoThirsty/Project-AI`
1. Root directory: `web/`
1. Click **Deploy**
1. Go to **Settings → Domains**
1. Add: `thirstysprojects.com`
1. Follow DNS instructions

#### **Via Vercel CLI:**

```bash

# Install

npm install -g vercel

# Login

vercel login

# Deploy

cd web/
vercel --prod

# Add custom domain

vercel domains add thirstysprojects.com
```

#### **DNS Configuration for Vercel:**

Add these DNS records:

```
Type: A
Name: @
Value: 76.76.21.21

Type: CNAME
Name: www
Value: cname.vercel-dns.com
```

______________________________________________________________________

## 🔧 **DNS Configuration**

### **Step 1: Access DNS Settings**

Go to your domain registrar (GoDaddy, Namecheap, Cloudflare, etc.)

### **Step 2: Configure A Record**

**For Traditional Hosting:**

```
Type: A
Name: @ (or leave blank for root)
Value: [Your hosting server IP]
TTL: 3600
```

**For Netlify:**

```
Type: A
Name: @
Value: 75.2.60.5
TTL: 3600
```

**For Vercel:**

```
Type: A
Name: @
Value: 76.76.21.21
TTL: 3600
```

### **Step 3: Configure CNAME (optional)**

**For www subdomain:**

```
Type: CNAME
Name: www
Value: thirstysprojects.com (or hosting provider CNAME)
TTL: 3600
```

### **Step 4: Wait for Propagation**

DNS changes can take 1-48 hours (usually 15-30 minutes)

Check propagation: https://dnschecker.org

______________________________________________________________________

## 🔒 **SSL/HTTPS Setup**

### **Option 1: Free SSL via cPanel/Hosting**

Most hosts offer free Let's Encrypt SSL:

1. Go to cPanel → **SSL/TLS Status**
1. Find `thirstysprojects.com`
1. Click **Run AutoSSL**
1. Wait for certificate generation

### **Option 2: Cloudflare (Free)**

1. Add site to Cloudflare: https://dash.cloudflare.com
1. Change nameservers to Cloudflare's
1. Enable **Full (Strict)** SSL mode
1. Automatic HTTPS redirect

### **Option 3: Let's Encrypt (Manual)**

```bash

# SSH into server

ssh username@thirstysprojects.com

# Install certbot

sudo apt-get install certbot python3-certbot-apache

# Get certificate

sudo certbot --apache -d thirstysprojects.com -d www.thirstysprojects.com

# Auto-renewal is usually configured automatically

```

### **Option 4: Netlify/Vercel Auto-SSL**

Both platforms provide automatic HTTPS for custom domains.

______________________________________________________________________

## ✅ **Verification Steps**

### **1. Check File Access**

```bash
curl -I https://thirstysprojects.com
```

Expected: `HTTP/2 200 OK`

### **2. Test Charter Section**

1. Visit: `https://thirstysprojects.com`
1. Scroll to "Software Charter & Terms"
1. Verify:
   - ✅ Charter loads with scrollbar
   - ✅ 5 checkboxes present
   - ✅ Timer display shows: "Please scroll through..."
   - ✅ Checkboxes are disabled

### **3. Test Timer Functionality**

1. Scroll charter into view
1. Watch timer start automatically
1. Wait 2 minutes
1. Verify:
   - ✅ Timer counts down (2:00 → 1:59 → ... → 0:00)
   - ✅ Color changes (red → yellow → green)
   - ✅ Checkboxes enable after timer expires

### **4. Test Acknowledgment**

1. Check all 5 boxes
1. Click "Acknowledge Charter & Enable Downloads"
1. Verify:
   - ✅ Page scrolls to downloads
   - ✅ All 8 download cards become active
   - ✅ Download buttons are clickable

### **5. Test HTTPS**

```bash
https://www.ssllabs.com/ssltest/analyze.html?d=thirstysprojects.com
```

Expected: A or A+ rating

### **6. Test Mobile**

- Visit on mobile device
- Verify responsive design
- Test charter scrolling on mobile

______________________________________________________________________

## 📊 **Performance Optimization**

### **1. Enable Gzip Compression**

**cPanel → .htaccess:**

```apache
<IfModule mod_deflate.c>
  AddOutputFilterByType DEFLATE text/html text/css text/javascript
</IfModule>
```

### **2. Enable Browser Caching**

**Add to .htaccess:**

```apache
<IfModule mod_expires.c>
  ExpiresActive On
  ExpiresByType text/html "access plus 1 hour"
  ExpiresByType text/css "access plus 1 month"
  ExpiresByType text/javascript "access plus 1 month"
</IfModule>
```

### **3. Cloudflare CDN (Optional)**

1. Add site to Cloudflare
1. Enable caching
1. Enable minification (HTML/CSS/JS)
1. Enable "Auto Minify"

______________________________________________________________________

## 🔍 **Troubleshooting**

### **Issue: Site Not Loading**

**Check 1: DNS Propagation**

```bash
nslookup thirstysprojects.com

# Should return your server IP

```

**Check 2: File Permissions**

```bash

# Should be 644 for index.html

ls -la index.html
```

**Check 3: Server Logs**

```bash

# cPanel: Error Logs section

# SSH: tail -f /var/log/apache2/error.log

```

### **Issue: HTTPS Not Working**

**Solution 1: Force HTTPS** Add to `.htaccess`:

```apache
RewriteEngine On
RewriteCond %{HTTPS} off
RewriteRule ^(.*)$ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]
```

**Solution 2: Check SSL Certificate**

```bash
openssl s_client -connect thirstysprojects.com:443
```

### **Issue: Timer Not Starting**

**Check 1: JavaScript Console**

- Press F12 in browser
- Go to Console tab
- Look for errors

**Check 2: Clear Browser Cache**

- Ctrl+Shift+Delete
- Clear cached files
- Reload page

### **Issue: Downloads Not Enabling**

**Check 1: Checkboxes**

- All 5 must be checked
- Timer must be expired

**Check 2: localStorage**

- F12 → Application → Local Storage
- Verify charter_acknowledged is set

______________________________________________________________________

## 📁 **Directory Structure**

### **Final Structure on Server:**

**Option A: Root Domain**

```
public_html/
└── index.html  (Project AI web interface)
```

**Option B: Subdirectory**

```
public_html/
├── index.html  (existing site)
└── project-ai/
    └── index.html  (Project AI interface)
```

______________________________________________________________________

## 🎨 **Customization Options**

### **Update Domain in Charter**

If you want to reference thirstysprojects.com in the charter:

Edit `web/index.html`, find download URLs section, and update:

```javascript
const downloadUrls = {
  'complete': 'https://thirstysprojects.com/downloads/project-ai-v1.0.0.zip',
  // ... etc
};
```

### **Add Subdomain**

Create subdomain `project-ai.thirstysprojects.com`:

**DNS Record:**

```
Type: CNAME
Name: project-ai
Value: thirstysprojects.com
TTL: 3600
```

**Upload to:**

```
public_html/project-ai/index.html
```

______________________________________________________________________

## 🚀 **Quick Deploy Script (Windows)**

Save as `deploy_to_thirstysprojects.bat`:

```batch
@echo off
echo ========================================
echo Deploying to thirstysprojects.com
echo ========================================

REM Set variables
set DOMAIN=thirstysprojects.com
set FTP_USER=your_username
set FTP_PASS=your_password
set LOCAL_FILE=web\index.html
set REMOTE_PATH=/public_html/index.html

echo.
echo Uploading index.html...

REM Using curl for FTP upload
curl -T "%LOCAL_FILE%" ftp://%DOMAIN%%REMOTE_PATH% --user %FTP_USER%:%FTP_PASS%

echo.
echo ========================================
echo Deployment Complete!
echo Visit: https://%DOMAIN%
echo ========================================

pause
```

**Usage:**

1. Update FTP credentials in script
1. Run: `deploy_to_thirstysprojects.bat`

______________________________________________________________________

## 📊 **Post-Deployment Monitoring**

### **1. Google Analytics (Optional)**

Add before `</head>` in index.html:

```html
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-XXXXXXXXXX');
</script>
```

### **2. Uptime Monitoring**

Use services like:

- UptimeRobot: https://uptimerobot.com (free)
- Pingdom: https://pingdom.com
- StatusCake: https://statuscake.com

Add monitor for: `https://thirstysprojects.com`

### **3. Error Tracking**

Monitor server logs or use:

- Sentry: https://sentry.io (error tracking)
- LogRocket: https://logrocket.com (session replay)

______________________________________________________________________

## ✅ **Deployment Checklist**

- [ ] Web file uploaded (`index.html`)
- [ ] File permissions set (644)
- [ ] DNS A record configured
- [ ] DNS CNAME configured (www)
- [ ] SSL certificate installed
- [ ] HTTPS redirect enabled
- [ ] Site loads at https://thirstysprojects.com
- [ ] Charter section visible
- [ ] Timer starts automatically
- [ ] Checkboxes enable after 2 minutes
- [ ] Downloads enable after acknowledgment
- [ ] Mobile responsive
- [ ] Browser cache configured
- [ ] Gzip compression enabled
- [ ] Uptime monitoring configured (optional)

______________________________________________________________________

## 🎉 **Success!**

Once deployed, your Project AI web interface with mandatory Software Charter will be live at:

### **🌐 https://thirstysprojects.com**

**Features:**

- ✅ Mandatory Software Charter (10 sections)
- ✅ 2-minute enforced reading timer
- ✅ 5 required acknowledgment checkboxes
- ✅ 8 platform-specific downloads
- ✅ Complete audit trail
- ✅ Professional design with animations

______________________________________________________________________

## 📞 **Support**

If you encounter issues:

1. Check troubleshooting section above
1. Review hosting provider documentation
1. Check browser console (F12) for errors
1. Verify DNS propagation: https://dnschecker.org
1. Test SSL: https://www.ssllabs.com/ssltest/

______________________________________________________________________

**Ready to deploy!** Choose your method above and get your site live. 🚀

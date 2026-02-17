# ✅ Deploy to thirstysprojects.com - Quick Checklist

## 🚀 **FASTEST PATH: 3 Steps**

### **Step 1: Choose Method**

- [ ] Option A: Run `deploy_to_thirstysprojects.bat` (Windows, automated)
- [ ] Option B: Use cPanel File Manager (manual, 10 min)
- [ ] Option C: Use Netlify drag-and-drop (instant, 5 min)

### **Step 2: Upload File**

- [ ] Upload `web/index.html` to hosting
- [ ] Verify file is named `index.html` (not `index.html.html`)
- [ ] Set permissions to `644` (if using FTP/SSH)

### **Step 3: Verify Live**

- [ ] Visit: https://thirstysprojects.com
- [ ] Charter section loads ✅
- [ ] Timer starts when scrolling ✅
- [ ] Checkboxes work after 2 minutes ✅

______________________________________________________________________

## 📋 **PRE-FLIGHT CHECK**

- [ ] Domain registered: `thirstysprojects.com`
- [ ] Hosting account active
- [ ] Access credentials ready (FTP/cPanel)
- [ ] File ready: `web/index.html` exists

______________________________________________________________________

## 🔧 **OPTION A: Interactive Script (Recommended)**

```bash

# Just run this:

deploy_to_thirstysprojects.bat

# Choose option 1 for FTP

# Enter credentials when prompted

# Done!

```

**Time:** 5 minutes

______________________________________________________________________

## 🔧 **OPTION B: cPanel Manual Upload**

1. [ ] Login to cPanel
1. [ ] Open **File Manager**
1. [ ] Navigate to `public_html/`
1. [ ] Click **Upload**
1. [ ] Select `web/index.html`
1. [ ] Wait for upload
1. [ ] Visit https://thirstysprojects.com

**Time:** 10 minutes

______________________________________________________________________

## 🔧 **OPTION C: Netlify (Instant)**

1. [ ] Go to https://app.netlify.com
1. [ ] Drag `web/` folder onto page
1. [ ] Wait for deployment
1. [ ] Go to **Domain settings**
1. [ ] Add: `thirstysprojects.com`
1. [ ] Copy DNS settings
1. [ ] Update DNS at domain registrar

**DNS Records:**

```
A Record:
Name: @
Value: 75.2.60.5

CNAME:
Name: www
Value: [your-site].netlify.app
```

**Time:** 5 minutes (+ DNS propagation)

______________________________________________________________________

## 🔒 **SSL/HTTPS (REQUIRED)**

### **cPanel/Shared Hosting:**

- [ ] Go to cPanel → **SSL/TLS Status**
- [ ] Click **Run AutoSSL**
- [ ] Wait 1-2 minutes

### **Cloudflare (Free):**

- [ ] Add site to Cloudflare
- [ ] Change nameservers
- [ ] SSL auto-enabled

### **Netlify/Vercel:**

- [ ] Automatic (no action needed)

______________________________________________________________________

## ✅ **POST-DEPLOYMENT VERIFICATION**

### **Basic Tests:**

- [ ] `https://thirstysprojects.com` loads
- [ ] No SSL errors
- [ ] Page displays correctly

### **Charter Tests:**

- [ ] Scroll to "Software Charter & Terms"
- [ ] Charter content is scrollable
- [ ] Timer shows: "Please scroll through..."
- [ ] Scrolling starts timer
- [ ] Timer counts down (2:00)

### **Acknowledgment Tests:**

- [ ] Wait 2 minutes
- [ ] Timer shows: "✅ Reading time complete"
- [ ] Checkboxes become enabled
- [ ] Can check all 5 boxes
- [ ] "Acknowledge" button activates

### **Download Tests:**

- [ ] Click "Acknowledge Charter & Enable Downloads"
- [ ] Page scrolls to downloads
- [ ] All 8 download cards active
- [ ] No grayed-out cards
- [ ] Download buttons clickable

### **Mobile Tests:**

- [ ] Site loads on mobile
- [ ] Charter scrollable on mobile
- [ ] Timer works on mobile
- [ ] Responsive design

______________________________________________________________________

## 🎯 **QUICK TROUBLESHOOTING**

### **Site not loading?**

- [ ] Check DNS propagation: dnschecker.org
- [ ] Wait 15-30 minutes
- [ ] Clear browser cache

### **HTTPS not working?**

- [ ] Enable SSL in cPanel
- [ ] Or use Cloudflare
- [ ] Force HTTPS redirect

### **Timer not starting?**

- [ ] Clear browser cache
- [ ] Try different browser
- [ ] Check JavaScript console (F12)

### **Downloads not enabling?**

- [ ] Wait full 2 minutes
- [ ] Check all 5 boxes
- [ ] Clear localStorage (F12)

______________________________________________________________________

## 📞 **HELP & DOCS**

- 📘 **Full Guide:** `DEPLOY_TO_THIRSTYSPROJECTS.md`
- 📘 **Charter Info:** `WEB_CHARTER_DOWNLOADS_COMPLETE.md`
- 📘 **General Deploy:** `WEB_DEPLOYMENT_GUIDE.md`
- 🔧 **Script:** `deploy_to_thirstysprojects.bat`

______________________________________________________________________

## 🎉 **SUCCESS CRITERIA**

Your deployment is complete when:

✅ Site loads at `https://thirstysprojects.com` ✅ SSL certificate is valid (green lock) ✅ Charter section is visible and scrollable ✅ Timer starts when scrolling charter ✅ Timer counts down for 2 minutes ✅ Checkboxes enable after timer expires ✅ All 5 checkboxes can be checked ✅ Downloads enable after acknowledgment ✅ All 8 download options are active ✅ Mobile responsive design works

______________________________________________________________________

## 🚀 **GO LIVE!**

```bash

# Fastest: Run this command

deploy_to_thirstysprojects.bat

# Then visit:

https://thirstysprojects.com
```

**That's it!** Your charter-protected Project AI site is live! 🎉

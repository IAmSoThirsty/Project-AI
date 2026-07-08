# 🚀 Production Deployment Guide

Complete guide for deploying The Triumvirate to GitHub Pages and ensuring production readiness.

## Table of Contents

- [Pre-Deployment Checklist](#pre-deployment-checklist)
- [GitHub Pages Setup](#github-pages-setup)
- [Configuration](#configuration)
- [Testing](#testing)
- [Deployment](#deployment)
- [Post-Deployment](#post-deployment)
- [Monitoring](#monitoring)
- [Troubleshooting](#troubleshooting)

## Pre-Deployment Checklist

### 1. Code Quality

- [ ] All tests passing (`npm test`)
- [ ] No console errors in browser
- [ ] No lint errors
- [ ] Code reviewed and approved
- [ ] All TODOs resolved or documented

### 2. Content

- [ ] All content proofread and finalized
- [ ] Images optimized and compressed
- [ ] All links tested and working
- [ ] Metadata complete (titles, descriptions, OG tags)
- [ ] Copyright notices updated

### 3. Performance

- [ ] CSS built and minified (`npm run build:css`)
- [ ] Images compressed (< 200KB each)
- [ ] No unused dependencies
- [ ] Lighthouse score > 90 for all categories

### 4. SEO

- [ ] Sitemap.xml updated with current date
- [ ] Robots.txt configured correctly
- [ ] Meta tags present on all pages
- [ ] Structured data validated
- [ ] Canonical URLs set

### 5. Security

- [ ] Security headers configured (.htaccess and _headers)
- [ ] No API keys or secrets in code
- [ ] CSP policy tested
- [ ] HTTPS enabled (if custom domain)

### 6. Accessibility

- [ ] WCAG 2.1 Level AA compliant
- [ ] Keyboard navigation tested
- [ ] Screen reader tested
- [ ] Color contrast validated
- [ ] Alt text on all images

### 7. PWA

- [ ] Service worker tested
- [ ] Manifest.json valid
- [ ] App icons generated (all sizes)
- [ ] Offline functionality working
- [ ] Install prompt tested

## GitHub Pages Setup

### Step 1: Repository Settings

1. Go to repository **Settings**
2. Navigate to **Pages** section
3. Select **Source**: GitHub Actions
4. Save settings

### Step 2: Configure Base URL

Ensure all files reference the correct base URL:

```html
<!-- In all HTML files -->
<base href="/the_triumvirate/">
```

### Step 3: Update URLs

Update these files with GitHub Pages URLs:

- `sitemap.xml` → `https://iamsothirsty.github.io/the_triumvirate/`
- `robots.txt` → `https://iamsothirsty.github.io/the_triumvirate/`
- `public/manifest.json` → Update start_url and scope
- `includes/meta-tags.html` → Update og:url and canonical URLs

## Configuration

### Environment-Specific Settings

#### Development
```javascript
// js/analytics.js
config.ga4.enabled = false;
```

#### Production
```javascript
// js/analytics.js
config.ga4.enabled = true;
config.ga4.measurementId = 'G-XXXXXXXXXX'; // Your GA4 ID
```

### Analytics Setup

1. **Create Google Analytics 4 Property**
   - Visit [Google Analytics](https://analytics.google.com/)
   - Create new GA4 property
   - Copy Measurement ID (G-XXXXXXXXXX)
   - Update `js/analytics.js` with your ID

2. **Test Analytics**
   ```bash
   # Start local server
   npm run dev
   
   # Open browser console
   # You should see: "📊 Analytics: Disabled (no measurement ID configured)"
   ```

## Testing

### Local Testing

```bash
# Install dependencies
npm install

# Build CSS
npm run build:css

# Run tests
npm test

# Run integration tests
npm run test:integration

# Test with local server
npx http-server -p 8080
```

### Pre-Production Testing

```bash
# Test Lighthouse scores
npm install -g @lhci/cli
lhci autorun --config=lighthouserc.js

# Validate HTML
npm install -g html-validator-cli
html-validator --file=index.html --verbose

# Check broken links
npm install -g broken-link-checker
blc http://localhost:8080/the_triumvirate/ -ro
```

### Accessibility Testing

```bash
# Install axe-core CLI
npm install -g @axe-core/cli

# Run accessibility audit
axe http://localhost:8080/the_triumvirate/
```

## Deployment

### Automatic Deployment (Recommended)

The repository is configured for automatic deployment via GitHub Actions.

1. **Commit and Push**
   ```bash
   git add .
   git commit -m "Production ready deployment"
   git push origin main
   ```

2. **Monitor Deployment**
   - Go to **Actions** tab in GitHub
   - Watch deployment progress
   - Verify successful completion

3. **Access Site**
   - Visit: `https://iamsothirsty.github.io/the_triumvirate/`
   - Allow 2-5 minutes for DNS propagation

### Manual Deployment

If you need to deploy manually:

```bash
# Build assets
npm run build:css

# Create deployment branch
git checkout -b gh-pages

# Push to GitHub Pages
git push origin gh-pages
```

## Post-Deployment

### Immediate Verification

- [ ] Site loads at production URL
- [ ] All pages accessible
- [ ] No 404 errors
- [ ] Images loading correctly
- [ ] CSS styles applied
- [ ] JavaScript functioning
- [ ] Service worker registered
- [ ] PWA installable

### SEO Verification

#### Submit Sitemap

1. **Google Search Console**
   - Add property: `https://iamsothirsty.github.io`
   - Verify ownership
   - Submit sitemap: `/the_triumvirate/sitemap.xml`

2. **Bing Webmaster Tools**
   - Add site
   - Submit sitemap

#### Test Social Sharing

1. **Facebook Debugger**
   - Visit: https://developers.facebook.com/tools/debug/
   - Enter URL
   - Click "Scrape Again"
   - Verify image and metadata

2. **Twitter Card Validator**
   - Visit: https://cards-dev.twitter.com/validator
   - Enter URL
   - Verify card preview

3. **LinkedIn Post Inspector**
   - Visit: https://www.linkedin.com/post-inspector/
   - Enter URL
   - Verify preview

### Performance Verification

Run Lighthouse audit:

```bash
# Install Lighthouse CI
npm install -g @lhci/cli

# Run audit
lhci autorun --collect.url=https://iamsothirsty.github.io/the_triumvirate/
```

Target scores:
- **Performance**: > 90
- **Accessibility**: > 95
- **Best Practices**: > 90
- **SEO**: > 95
- **PWA**: Installable

## Monitoring

### Analytics Dashboard

1. **Google Analytics 4**
   - Monitor real-time users
   - Track page views
   - Review user flow
   - Check conversion goals

2. **Search Console**
   - Monitor search performance
   - Check indexing status
   - Review mobile usability
   - Track Core Web Vitals

### Error Monitoring

Monitor browser console for:
- JavaScript errors
- Failed resource loads
- Service worker issues
- Network failures

### Performance Monitoring

Track these metrics weekly:
- Page load time
- Time to Interactive (TTI)
- Largest Contentful Paint (LCP)
- First Input Delay (FID)
- Cumulative Layout Shift (CLS)

## Troubleshooting

### Common Issues

#### Site Not Loading

1. Check GitHub Actions deployment status
2. Verify GitHub Pages is enabled in settings
3. Check repository visibility (public)
4. Wait 5-10 minutes for propagation

#### 404 Errors

1. Verify `base` tag in HTML: `<base href="/the_triumvirate/">`
2. Check file paths are correct
3. Ensure files are committed to repository
4. Check case sensitivity in URLs

#### CSS Not Loading

1. Verify CSS file exists: `css/main.css`
2. Run build: `npm run build:css`
3. Check network tab for 404 errors
4. Verify base href is correct

#### Service Worker Issues

1. Check HTTPS is enabled
2. Verify `sw.js` is in root directory
3. Check browser console for registration errors
4. Clear cache and hard reload

#### Analytics Not Working

1. Verify GA4 measurement ID is correct
2. Check analytics.js is loaded
3. Verify `config.ga4.enabled = true`
4. Check browser console for errors
5. Use Google Tag Assistant

### Performance Issues

If Lighthouse score < 90:

1. **Optimize Images**
   ```bash
   # Using imageoptim or tinypng
   npm install -g imageoptim-cli
   imageoptim assets/images/*.png
   ```

2. **Minify Resources**
   ```bash
   # Minify CSS
   npm install -g clean-css-cli
   cleancss -o css/main.min.css css/main.css
   ```

3. **Enable Caching**
   - Verify .htaccess or _headers file
   - Check Cache-Control headers
   - Test with curl: `curl -I https://site.url`

### Getting Help

- **GitHub Issues**: Report bugs or request features
- **Discussions**: Ask questions in GitHub Discussions
- **Documentation**: Check README.md and CONTRIBUTING.md
- **Email**: Contact maintainers

## Rollback Procedure

If deployment fails:

```bash
# Revert to previous commit
git revert HEAD

# Or reset to specific commit
git reset --hard <commit-hash>

# Force push (use with caution)
git push origin main --force
```

## Continuous Improvement

### Monthly Tasks

- [ ] Review analytics data
- [ ] Check for broken links
- [ ] Update dependencies
- [ ] Review and update content
- [ ] Check Lighthouse scores
- [ ] Review error logs

### Quarterly Tasks

- [ ] Comprehensive accessibility audit
- [ ] Security audit
- [ ] Performance optimization review
- [ ] Content refresh
- [ ] SEO review
- [ ] User feedback analysis

## Success Criteria

Your deployment is successful when:

✅ Site accessible at production URL  
✅ All Lighthouse scores > 90  
✅ No console errors  
✅ Analytics tracking  
✅ PWA installable  
✅ Search engines can crawl  
✅ Social sharing works  
✅ Offline functionality works  

---

**Congratulations! Your site is production-ready! 🎉**

For ongoing maintenance, see [MAINTENANCE.md](MAINTENANCE.md)

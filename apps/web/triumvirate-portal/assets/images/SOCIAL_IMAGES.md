# Social Media Images Guide

This guide explains how to create and optimize social media preview images for The Triumvirate project.

## Image Specifications

### Open Graph (Facebook, LinkedIn, etc.)
- **Dimensions**: 1200 × 630 pixels
- **Format**: PNG or JPEG
- **Max File Size**: 8 MB (recommended < 300 KB)
- **Aspect Ratio**: 1.91:1
- **Filename**: `og-image.png`

### Twitter Card
- **Dimensions**: 1200 × 600 pixels
- **Format**: PNG or JPEG
- **Max File Size**: 5 MB (recommended < 300 KB)
- **Aspect Ratio**: 2:1
- **Filename**: `twitter-card.png`

### Mobile Screenshots (PWA)
- **Wide Format**: 1280 × 720 pixels
- **Narrow Format**: 750 × 1334 pixels
- **Format**: PNG
- **Filename**: `screenshot-wide.png`, `screenshot-mobile.png`

## Current Placeholder Images

We've created SVG placeholders that can be converted to PNG:

1. **og-image.svg** - Open Graph placeholder
2. **twitter-card.svg** - Twitter Card placeholder

## Converting SVG to PNG

### Using Online Tools
1. Visit [CloudConvert](https://cloudconvert.com/svg-to-png)
2. Upload the SVG file
3. Set width to 1200px (for OG) or 1200px (for Twitter)
4. Download the PNG

### Using Command Line (requires Inkscape or ImageMagick)

```bash
# Using Inkscape
inkscape og-image.svg --export-png=og-image.png --export-width=1200

# Using ImageMagick
convert -background none og-image.svg -resize 1200x630 og-image.png
```

### Using Node.js (sharp library)

```javascript
const sharp = require('sharp');
const { readFileSync } = require('fs');

const svg = readFileSync('og-image.svg');

sharp(svg)
  .resize(1200, 630)
  .png()
  .toFile('og-image.png');
```

## Page-Specific Images

Create unique images for each major page:

### Required Images
- ✅ `og-image.png` - Home page (already templated)
- ✅ `twitter-card.png` - Home page (already templated)
- ⏳ `og-manifesto.png` - Manifesto Gateway
- ⏳ `og-trinity.png` - Trinity Deep Dive
- ⏳ `og-project-ai.png` - Project AI
- ⏳ `og-cerberus.png` - Cerberus
- ⏳ `og-codex.png` - Codex Deus Maximus
- ⏳ `og-research.png` - Research Center
- ⏳ `og-founder.png` - Founder Profile

## Design Guidelines

### Color Palette
- **Primary Background**: `#0F172A` (slate-900)
- **Secondary Background**: `#1E293B` (slate-800)
- **Accent**: `#0891B2` (cyan-600)
- **Text**: `#F8FAFC` (slate-50)
- **Gradient**: Linear gradient from `#60A5FA` → `#06B6D4` → `#22D3EE`

### Typography
- **Primary Font**: Arial, Helvetica, sans-serif
- **Heading Size**: 56-64px
- **Subheading Size**: 32-36px
- **Body Text**: 20-24px

### Branding Elements
- Trinity symbol: 🔱
- ThirstysProjects.com logo
- Gradient text effects
- Subtle geometric patterns

## Testing Your Images

### Social Media Preview Tools
1. **Facebook**: [Sharing Debugger](https://developers.facebook.com/tools/debug/)
2. **Twitter**: [Card Validator](https://cards-dev.twitter.com/validator)
3. **LinkedIn**: [Post Inspector](https://www.linkedin.com/post-inspector/)
4. **General**: [Metatags.io](https://metatags.io/)

### Checklist
- [ ] Images are the correct dimensions
- [ ] File sizes are optimized (< 300 KB)
- [ ] Text is readable at small sizes
- [ ] Colors match brand guidelines
- [ ] Images look good on both light and dark backgrounds
- [ ] No important content is cut off on mobile
- [ ] Images include branding (logo or name)

## Optimization

### Compress Images
```bash
# Using imageoptim-cli (macOS)
imageoptim og-image.png

# Using pngquant
pngquant --quality=65-80 og-image.png

# Using TinyPNG online
# Visit https://tinypng.com/
```

### Best Practices
1. Use PNG for images with text or transparency
2. Use JPEG for photographic content
3. Compress images without visible quality loss
4. Test on multiple devices and platforms
5. Update images when content changes

## PWA App Icons

Current app icon assets are in this directory and referenced by `public/manifest.json`:

- `favicon.svg`
- `icon-192x192.svg`
- `icon-192x192.png`
- `icon-512x512.svg`
- `icon-512x512.png`

## Resources
- [Open Graph Protocol](https://ogp.me/)
- [Twitter Card Documentation](https://developer.twitter.com/en/docs/twitter-for-websites/cards/overview/abouts-cards)
- [PWA Asset Generator](https://github.com/onderceylan/pwa-asset-generator)

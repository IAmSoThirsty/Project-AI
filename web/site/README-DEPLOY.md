# Thirstys Projects — Deployment & Maintenance

## Folder structure

```
thirstys-projects-site/
├── index.html               ← Home
├── about.html
├── projects.html            ← Filterable project gallery
├── project-ai.html          ← Project-AI & OCTOREFLEX dossier
├── cerberus.html            ← Cerberus Guard Bot dossier
├── hub-epstein.html         ← Hub of Epstein Files (educational/research)
├── papers.html              ← Zenodo research index
├── blog.html                ← Field notes index
├── blog/
│   └── post-template.html   ← Copy this for new long-form posts
├── contact.html
├── legal.html
├── 404.html
├── robots.txt
├── sitemap.xml
├── .htaccess                ← HTTPS redirect, security headers, caching
├── assets/
│   ├── css/site.css
│   ├── js/
│   │   ├── site.js          ← Nav, footer, theme, reveal, mouse-light
│   │   ├── particles.js     ← Hero constellation canvas
│   │   ├── projects.js      ← Loads + filters projects.json
│   │   ├── papers.js        ← Loads + filters + searches papers.json
│   │   └── blog.js          ← Loads posts.json
│   ├── data/
│   │   ├── projects.json    ← Edit to add/update projects
│   │   ├── papers.json      ← 21 Zenodo papers — edit to add new
│   │   └── posts.json       ← Field notes index
│   └── img/
│       ├── favicon.svg
│       └── og.svg           ← Open Graph card
└── README-DEPLOY.md         ← This file
```

## Stack

- Pure static HTML5 / CSS / vanilla JS — no build step required.
- Tailwind is **not** used at runtime. The site uses a hand-tuned design system in `assets/css/site.css` (CSS variables + class-based components). If you want Tailwind utilities you can add the Play CDN to any page; nothing else needs to change.
- [Alpine.js](https://alpinejs.dev) (CDN) powers the dropdown menu and mobile nav. Two declarative attributes — that's it.
- Google Fonts: Inter, Space Grotesk, JetBrains Mono.
- Compatible with any static host: cPanel, Netlify, Cloudflare Pages, S3, GitHub Pages.

## cPanel (Namecheap) — upload steps

1. Sign in to your Namecheap **cPanel** dashboard for `thirstysprojects.com`.
2. Open **File Manager** → navigate to `public_html/`.
3. (Optional) Backup any existing `index.html` first by renaming it to `index.bak.html`.
4. Click **Upload** in the toolbar. Upload **all files and folders** from this project, preserving structure. (Easiest: zip the whole `thirstys-projects-site` directory locally, upload the zip, then right-click → **Extract**, and move the contents up one level if needed so that `index.html` sits directly in `public_html/`.)
5. Confirm `public_html/` now contains `index.html`, `assets/`, `blog/`, `.htaccess`, `sitemap.xml`, `robots.txt`, etc.
6. Visit `https://thirstysprojects.com` — done.

> The included `.htaccess` will: force HTTPS, serve `404.html` on any missing route, allow pretty URLs (`/papers` → `/papers.html`), set strict security headers, and enable caching/compression.

## Enable SSL (free, automatic)

- cPanel → **SSL/TLS Status** (or **AutoSSL**).
- Make sure both `thirstysprojects.com` and `www.thirstysprojects.com` are listed and have a green padlock.
- If not, click **Run AutoSSL** and wait a few minutes. AutoSSL runs Let's Encrypt for you. Once issued, the `.htaccess` HTTPS redirect kicks in automatically.

## Wire the contact form

`contact.html` POSTs to [FormSubmit.co](https://formsubmit.co) using the email `karrick1995@gmail.com`. On the **first** submission FormSubmit sends a one-click activation link to that address — click it once and the form is permanently enabled. No backend, no hosting, no API key.

To switch to your own backend or to another service (Netlify Forms, Formspree, Google Forms, Postmark, etc.), just change the `<form action="…">` URL in `contact.html`. No other changes needed.

## How to maintain

### Add a research paper
1. Open `assets/data/papers.json`.
2. Append a new entry:
   ```json
   {
     "id": 12345678,
     "doi": "10.5281/zenodo.12345678",
     "doi_url": "https://doi.org/10.5281/zenodo.12345678",
     "zenodo_url": "https://zenodo.org/records/12345678",
     "title": "Your title",
     "date": "2026-07-01",
     "abstract": "Plain-text abstract (~500 chars).",
     "keywords": ["AGI Governance", "Containment"],
     "type": "Preprint"
   }
   ```
3. Save. The paper appears on `papers.html` and the home spotlight on next load.

### Add a project
Edit `assets/data/projects.json`. Each entry takes a `name`, `tagline`, `summary`, `tags`, `github`, optional `page` (for an internal dossier), `featured` flag, and `accent` (`cyan`, `violet`, `amber`, `rose`, `emerald`).

### Add a blog post
**Short form (linked card only):** append an entry to `assets/data/posts.json` with `title`, `date`, `tags`, `excerpt`, and either `external` (an outside URL) or no link (the slug-based path is implied).

**Long form:** copy `blog/post-template.html` → `blog/<slug>.html`, edit content, then add the index entry to `posts.json`.

### Update the hero / featured / footer
- Hero copy lives directly in `index.html` — edit the `<section class="hero">` block.
- Footer + nav are generated by `assets/js/site.js` — edit `NAV_LINKS` and `SOCIALS` arrays at the top of that file.

### Change colors / typography
All design tokens live as CSS variables at the top of `assets/css/site.css` (`:root` and `[data-theme="light"]`). Edit one variable; every page updates.

### Light mode
The theme toggle in the navbar persists the user's choice in `localStorage`. Default is dark.

## SEO checklist (built-in)
- [x] Per-page `<title>`, `meta description`, `canonical`, Open Graph, Twitter Card.
- [x] JSON-LD `Person` schema on the homepage.
- [x] `sitemap.xml` and `robots.txt`.
- [x] Semantic landmarks (`<header>`, `<nav>`, `<main>`, `<footer>`, `<article>`, `<section>`).
- [x] Reduced-motion guards.
- [x] Lazy-friendly: only fonts and Alpine load from CDN.

## Backup tip
After each meaningful update, duplicate the `public_html/` directory to a timestamped folder via cPanel **File Manager** → Compress. Or push a copy of this entire project to a private GitHub repo for full history.

## License
Site code: provided as-is for use by Jeremy Karrick / Thirstys Projects. Project source code and research papers carry their own per-repo / per-record licenses.

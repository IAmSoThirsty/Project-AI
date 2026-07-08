/* eslint-env node, jest */
/* global require, __dirname, describe, test, expect */

const fs = require('node:fs');
const path = require('node:path');

const ROOT = path.resolve(__dirname, '..');
const toAbsolute = (relativePath) => path.join(ROOT, relativePath);
const readText = (relativePath) => fs.readFileSync(toAbsolute(relativePath), 'utf8');
const CONTENT_PAGES = [
  'pages/manifesto_gateway.html',
  'pages/trinity_deep_dive.html',
  'pages/project_ai_cognitive_engine.html',
  'pages/cerberus_security_fortress.html',
  'pages/codex_deus_maximus_repository.html',
  'pages/scenario_demonstrations.html',
  'pages/research_center.html',
  'pages/future_architectures.html',
  'pages/trust_transparency_center.html',
  'pages/jeremy_karrick_founder_profile.html'
];

describe('The Triumvirate - Production Readiness Checks', () => {
  test('critical pages exist', () => {
    const requiredPages = [
      'index.html',
      '404.html',
      ...CONTENT_PAGES
    ];

    requiredPages.forEach((relativePath) => {
      expect(fs.existsSync(toAbsolute(relativePath))).toBe(true);
    });
  });

  test('index has core production metadata and runtime scripts', () => {
    const indexHtml = readText('index.html');

    expect(indexHtml).toContain('<base href="/the_triumvirate/">');
    expect(indexHtml).toContain('name="description"');
    expect(indexHtml).toContain('property="og:title"');
    expect(indexHtml).toContain('name="twitter:card"');
    expect(indexHtml).toContain('rel="canonical"');
    expect(indexHtml).toContain('rel="manifest"');
    expect(indexHtml).toContain('js/sw-register.js');
    expect(indexHtml).toContain('js/analytics.js');
  });

  test('manifest points to real icon assets', () => {
    const manifest = JSON.parse(readText('public/manifest.json'));

    expect(manifest.start_url).toBe('/the_triumvirate/');
    expect(manifest.scope).toBe('/the_triumvirate/');
    expect(Array.isArray(manifest.icons)).toBe(true);
    expect(manifest.icons.length).toBeGreaterThanOrEqual(2);

    manifest.icons.forEach((icon) => {
      const relativeAssetPath = icon.src.replace(/^\/the_triumvirate\//, '');
      expect(fs.existsSync(toAbsolute(relativeAssetPath))).toBe(true);
    });
  });

  test('service worker contains core cache entries', () => {
    const sw = readText('sw.js');

    expect(sw).toContain("const CACHE_VERSION = 'v1.0.1'");
    expect(sw).toContain("'/the_triumvirate/'");
    expect(sw).toContain("'/the_triumvirate/index.html'");
    expect(sw).toContain("'/the_triumvirate/404.html'");
    expect(sw).toContain("'/the_triumvirate/public/manifest.json'");
    expect(sw).toContain('self.addEventListener(\'fetch\'');
  });

  test('robots and sitemap are configured for GitHub Pages base URL', () => {
    const robots = readText('robots.txt');
    const sitemap = readText('sitemap.xml');

    expect(robots).toContain('Sitemap: https://iamsothirsty.github.io/the_triumvirate/sitemap.xml');
    expect(sitemap).toContain('<loc>https://iamsothirsty.github.io/the_triumvirate/</loc>');
    expect(sitemap).toContain('<urlset');
  });

  test('ci and deploy workflows include tests and build steps', () => {
    const ciWorkflow = readText('.github/workflows/nodejs.yml');
    const deployWorkflow = readText('.github/workflows/deploy-pages.yml');

    expect(ciWorkflow).toContain('Run tests');
    expect(ciWorkflow).toContain('Run integration tests');
    expect(ciWorkflow).toContain('Build CSS');

    expect(deployWorkflow).toContain('Install dependencies');
    expect(deployWorkflow).toContain('Run tests');
    expect(deployWorkflow).toContain('Run integration tests');
    expect(deployWorkflow).toContain('Deploy to GitHub Pages');
  });

  test('developer utility scripts are available', () => {
    const packageJson = JSON.parse(readText('package.json'));

    expect(packageJson.scripts).toHaveProperty('meta:list');
    expect(packageJson.scripts).toHaveProperty('meta:generate');
    expect(packageJson.scripts).toHaveProperty('test:lighthouse');
  });

  test('meta generator supports all configured page keys', () => {
    const { metaTagsConfig, generateMetaTags } = require(toAbsolute('js/meta-generator.js'));

    Object.entries(metaTagsConfig).forEach(([pageKey, pageConfig]) => {
      const tags = generateMetaTags(pageKey);

      expect(tags).toContain('name="description"');
      expect(tags).toContain('name="twitter:card"');
      expect(tags).toContain('rel="canonical"');

      const imageRelativePath = pageConfig.image.replace(
        /^https?:\/\/[^/]+\/the_triumvirate\//,
        ''
      );
      const twitterRelativePath = (pageConfig.twitterImage || pageConfig.image).replace(
        /^https?:\/\/[^/]+\/the_triumvirate\//,
        ''
      );

      expect(fs.existsSync(toAbsolute(imageRelativePath))).toBe(true);
      expect(fs.existsSync(toAbsolute(twitterRelativePath))).toBe(true);
    });
  });

  test('content pages include canonical and social metadata', () => {
    CONTENT_PAGES.forEach((relativePath) => {
      const html = readText(relativePath);
      const canonicalUrl = `https://iamsothirsty.github.io/the_triumvirate/${relativePath}`;

      expect(html).toContain('name="description"');
      expect(html).toContain('name="robots"');
      expect(html).toContain('property="og:title"');
      expect(html).toContain('property="og:description"');
      expect(html).toContain(`property="og:url" content="${canonicalUrl}"`);
      expect(html).toContain('property="og:image"');
      expect(html).toContain('name="twitter:card"');
      expect(html).toContain('name="twitter:title"');
      expect(html).toContain('name="twitter:description"');
      expect(html).toContain('name="twitter:image"');
      expect(html).toContain(`<link rel="canonical" href="${canonicalUrl}">`);
    });
  });

  test('content pages avoid parent-relative paths that break GitHub Pages base', () => {
    CONTENT_PAGES.forEach((relativePath) => {
      const html = readText(relativePath);
      expect(html).not.toMatch(/\.\.\/(index\.html|public\/|assets\/)/);
    });
  });
});

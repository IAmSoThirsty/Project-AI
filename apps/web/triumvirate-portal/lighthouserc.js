/**
 * Lighthouse CI Configuration
 * For automated performance, accessibility, and SEO audits
 */

module.exports = {
  ci: {
    collect: {
      numberOfRuns: 3,
      startServerCommand: 'npm run serve',
      startServerReadyPattern: 'Hit CTRL-C to stop the server',
      url: [
        'http://localhost:8080/the_triumvirate/',
        'http://localhost:8080/the_triumvirate/pages/manifesto_gateway.html',
        'http://localhost:8080/the_triumvirate/pages/trinity_deep_dive.html',
        'http://localhost:8080/the_triumvirate/pages/project_ai_cognitive_engine.html',
        'http://localhost:8080/the_triumvirate/pages/cerberus_security_fortress.html',
        'http://localhost:8080/the_triumvirate/pages/codex_deus_maximus_repository.html'
      ],
      settings: {
        preset: 'desktop',
        chromeFlags: '--no-sandbox --headless --disable-gpu',
      },
    },
    assert: {
      preset: 'lighthouse:recommended',
      assertions: {
        'categories:performance': ['error', { minScore: 0.9 }],
        'categories:accessibility': ['error', { minScore: 0.95 }],
        'categories:best-practices': ['error', { minScore: 0.9 }],
        'categories:seo': ['error', { minScore: 0.95 }],
        'categories:pwa': ['warn', { minScore: 0.8 }],
        
        // Performance metrics
        'first-contentful-paint': ['warn', { maxNumericValue: 1800 }],
        'largest-contentful-paint': ['error', { maxNumericValue: 2500 }],
        'cumulative-layout-shift': ['error', { maxNumericValue: 0.1 }],
        'total-blocking-time': ['warn', { maxNumericValue: 200 }],
        'speed-index': ['warn', { maxNumericValue: 3400 }],
        
        // Accessibility
        'color-contrast': 'error',
        'heading-order': 'warn',
        'html-has-lang': 'error',
        'image-alt': 'error',
        'label': 'error',
        'link-name': 'error',
        
        // Best Practices
        'errors-in-console': 'warn',
        'no-vulnerable-libraries': 'error',
        'uses-http2': 'warn',
        'uses-passive-event-listeners': 'warn',
        
        // SEO
        'document-title': 'error',
        'meta-description': 'error',
        'http-status-code': 'error',
        'link-text': 'warn',
        'crawlable-anchors': 'warn',
        'is-crawlable': 'error',
        'robots-txt': 'warn',
        'canonical': 'error',
      },
    },
    upload: {
      target: 'temporary-public-storage',
    },
    server: {
      // Optional: Configure a server for CI
    },
  },
};

const fs = require('node:fs');
const path = require('node:path');

const ROOT = path.resolve(__dirname, '..');
const toAbsolute = (relativePath) => path.join(ROOT, relativePath);
const readText = (relativePath) => fs.readFileSync(toAbsolute(relativePath), 'utf8');

const ALL_PAGES = [
  'index.html',
  '404.html',
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

describe('The Triumvirate - Accessibility Contracts', () => {
  // Regression for the Lighthouse/axe "skip-link" failure: a skip link whose
  // anchor target is missing (manifesto_gateway) or not programmatically
  // focusable (index) is announced but goes nowhere for keyboard users.
  test('every skip link targets an existing, focusable main-content element', () => {
    ALL_PAGES.forEach((relativePath) => {
      const html = readText(relativePath);
      if (!html.includes('class="skip-link"')) {
        return;
      }

      expect(html).toContain('href="#main-content"');

      const target = html.match(/<[a-z]+[^>]*id="main-content"[^>]*>/);
      expect(target).not.toBeNull();
      expect(target[0]).toContain('tabindex="-1"');
    });
  });
});

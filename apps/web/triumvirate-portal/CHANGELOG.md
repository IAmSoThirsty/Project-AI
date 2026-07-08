# Changelog

All notable changes to The Triumvirate project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.2] - 2026-04-27

### CI and workflow fixes

- Hardened CI workflow to run without external `uses` actions so build,
  test, integration, CSS build, and audit gates execute reliably.
- Removed automatic push trigger from deploy workflow to avoid redundant
  failing checks and keep deployment as an explicit manual release action.

### Versioning

- Release version incremented from `1.0.1` to `1.0.2`.

## [1.0.1] - 2026-04-27

### Highlights

- Dedicated high-coverage Jest suites for `js/meta-generator.js` and `js/sw-register.js`
- Release-readiness validation improvements and reproducible local quality gates

### Changed

- Release version incremented from `1.0.0` to `1.0.1`
- Coverage verification now passes configured global thresholds for
  statements, branches, lines, and functions

### Fixed

- Cleared test coverage blocker that prevented release gate completion

## [1.0.0] - 2026-01-06

### Added

- Initial release of The Triumvirate website
- 11 comprehensive HTML pages covering AI, Humanity, and Technology framework
- Custom Tailwind CSS design system with Neural Depth color palette
- Responsive design with mobile-first approach
- Accessibility features (WCAG 2.1 Level AA compliant)
- Keyboard navigation support with custom shortcuts
- Loading screen with particle effects and animations
- Interactive radial menu system on Trinity Deep Dive page
- Complete navigation system with mobile menu
- Comprehensive system audit documentation (SYSTEM_AUDIT.md)

### Core Pages

- Landing page (index.html) with auto-redirect
- Manifesto Gateway - Main philosophical hub
- Trinity Deep Dive - Technical system overview
- Project AI - Cognitive engine architecture
- Cerberus - Security fortress framework
- Codex Deus Maximus - Knowledge repository
- Scenario Demonstrations - Real-world use cases
- Research Center - Academic resources
- Future Architectures - Roadmap and vision
- Trust & Transparency Center - Accountability hub
- Founder Profile - Jeremy Karrick's story

### Design System

- Neural Depth color palette
- Custom typography (JetBrains Mono, Inter, Space Grotesk, Fira Code)
- Responsive breakpoints for all device sizes
- Custom animations and transitions
- Glow effects and advanced styling

### Build System

- NPM package management
- Tailwind CSS compilation with custom configuration
- Watch mode for development
- DhiWise component tagging integration

### Infrastructure

- Apache .htaccess configuration for clean URLs
- PWA manifest.json
- Favicon implementation
- Rocket.new deployment integration

## [Unreleased]

### To Be Added

- XML sitemap for SEO
- robots.txt for search engine crawling
- Open Graph meta tags for social media
- Analytics integration (Google Analytics or Plausible)
- Contact form functionality
- Newsletter subscription
- Blog/news section
- Search functionality
- Backend API infrastructure
- User authentication system
- Testing infrastructure (Jest, Playwright)
- CI/CD pipeline (GitHub Actions)
- Performance optimizations (CSS purging, image optimization)
- Security headers (CSP, HSTS)

---

## Version History

- **1.0.0** (2026-01-06): Initial public release

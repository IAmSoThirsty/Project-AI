<div align="right">
  <img src="https://img.shields.io/badge/Date-2026--03--10-blue?style=for-the-badge" alt="Date" />
  <img src="https://img.shields.io/badge/Status-Active-success?style=for-the-badge" alt="Status" />
  <img src="https://img.shields.io/badge/Tier-Master-gold?style=for-the-badge" alt="Tier" />
</div>

# 🔱 The Triumvirate

<div align="center">

![The Triumvirate Banner](https://img.shields.io/badge/The_Triumvirate-AI_×_Humanity_×_Technology-0891B2?style=for-the-badge)

**Exploring the Trinity of AI, Humanity & Technology**

A comprehensive manifesto and architectural framework for shaping the future of AGI-Human relations through ethical AI development, robust security, and transparent knowledge systems.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Built with Tailwind CSS](https://img.shields.io/badge/Built_with-Tailwind_CSS-38B2AC?logo=tailwind-css)](https://tailwindcss.com)
[![HTML5](https://img.shields.io/badge/HTML5-E34F26?logo=html5&logoColor=white)](https://developer.mozilla.org/en-US/docs/Web/HTML)

[System Audit](./SYSTEM_AUDIT.md) • [Documentation](#-project-structure) • [Quick Start](#-quick-start)

</div>

---

## 📖 About The Triumvirate

**The Triumvirate** is ThirstysProjects.com's flagship initiative exploring the intersection of artificial intelligence, humanity, and technology. This project presents a comprehensive framework consisting of three pillars:

### The Trinity 🔺

1. **Project AI (Cognitive Engine)** 🧠
   - Adaptive cognitive architecture with ethical frameworks
   - Context-aware memory systems and learning architecture
   - Real-time decision-making with moral reasoning

2. **Cerberus (Security Fortress)** 🛡️
   - Multi-layered security architecture
   - Threat detection and response systems
   - Privacy-first design with quantum-resistant encryption

3. **Codex Deus Maximus (Knowledge Repository)** 📚
   - Distributed knowledge architecture
   - Version-controlled ethical guidelines
   - Transparent decision-making processes

---

## ✨ Key Features

- 🎨 **Modern Design** - Clean, responsive UI built with Tailwind CSS
- ♿ **Accessibility-First** - WCAG compliant with keyboard navigation support
- 📱 **Mobile Responsive** - Optimized for all screen sizes
- 🎭 **Interactive Demos** - Live scenario demonstrations
- 🔐 **Security Focus** - Comprehensive security architecture documentation
- 🌐 **Progressive Enhancement** - Works across all modern browsers
- 🚀 **Performance Optimized** - Fast loading with minimal dependencies

---

## 🚀 Quick Start

### Prerequisites

- Node.js (v20.x recommended)
- npm or yarn
- A modern web browser

### Installation

1. **Clone the repository**

```bash
git clone https://github.com/IAmSoThirsty/the_triumvirate.git
cd the_triumvirate
```

2. **Install dependencies**

```bash
npm install
```

3. **Build CSS assets**

```bash
npm run build:css
```

4. **Run verification tests**

```bash
npm run validate
```

5. **Start local server**

```bash
npm run serve
```

6. **Open in browser**

```
Open http://localhost:8080/the_triumvirate/
```

---

## 📁 Project Structure

```
the_triumvirate/
├── 📄 index.html                          # Main entry point with loading screen
├── 📁 pages/                              # Core content pages
│   ├── manifesto_gateway.html             # Main manifesto landing page
│   ├── trinity_deep_dive.html             # Technical exploration of 3 systems
│   ├── project_ai_cognitive_engine.html   # Project AI details
│   ├── cerberus_security_fortress.html    # Cerberus security system
│   ├── codex_deus_maximus_repository.html # Knowledge repository
│   ├── scenario_demonstrations.html       # Interactive case studies
│   ├── research_center.html               # Research and resources
│   ├── future_architectures.html          # Future vision and roadmap
│   ├── trust_transparency_center.html     # Trust & transparency hub
│   └── jeremy_karrick_founder_profile.html # Founder information
├── 📁 css/
│   ├── tailwind.css                       # Tailwind source with custom utilities
│   └── main.css                           # Compiled CSS (auto-generated)
├── 📁 assets/
│   └── images/                            # Image assets
├── 📁 public/
│   ├── favicon.ico                        # Site favicon
│   └── manifest.json                      # PWA manifest
├── 📄 tailwind.config.js                  # Tailwind configuration
├── 📄 package.json                        # Dependencies and scripts
├── 📄 .htaccess                           # Apache configuration
└── 📄 README.md                           # This file
```

---

## 🎨 Design System

### Color Palette

The Triumvirate uses a carefully crafted "Neural Depth Palette":

- **Primary (Authority)**: `#1E3A8A` - Core manifesto blue
- **Secondary (Precision)**: `#0891B2` - Technical cyan
- **Accent (Emphasis)**: `#06B6D4` - Breakthrough cyan
- **Background (Canvas)**: `#0F172A` - Deep slate
- **Text (Clarity)**: `#F8FAFC` - High contrast white

### Typography

- **Headlines**: JetBrains Mono (monospace)
- **Body**: Inter (sans-serif)
- **CTAs**: Space Grotesk (sans-serif)
- **Code**: Fira Code (monospace)

### Responsive Breakpoints

- `sm`: 640px and up
- `md`: 768px and up
- `lg`: 1024px and up
- `xl`: 1280px and up
- `2xl`: 1536px and up

---

## 🛠️ Development

### Available Scripts

```bash

# Run core unit tests

npm test

# Run static integration checks

npm run test:integration

# Run all required checks before deploy

npm run validate

# List available meta-tag templates

npm run meta:list

# Generate meta tags for a specific page key

npm run meta:generate -- --page manifesto

# Run Lighthouse CI profile locally

npm run test:lighthouse

# Build CSS for production

npm run build:css

# Watch CSS changes during development

npm run watch:css

# Start development mode (watch CSS)

npm run dev

# Run static local server

npm run serve
```

### Technologies Used

- **HTML5** - Semantic markup with accessibility features
- **Tailwind CSS 3.4** - Utility-first CSS framework
- **Custom CSS** - Animations and advanced styling
- **JavaScript** - Interactive features and navigation
- **Rocket.new** - Build and deployment platform

### Build Process

The project uses Tailwind CSS with custom configuration:

1. Source: `css/tailwind.css`
2. Config: `tailwind.config.js`
3. Output: `css/main.css` (generated)

### Deployment

This project is configured for **GitHub Pages via GitHub Actions**.

- CI workflow: `.github/workflows/nodejs.yml`
- Deploy workflow: `.github/workflows/deploy-pages.yml`
- Production base URL: `https://iamsothirsty.github.io/the_triumvirate/`

Deploys are automatically triggered on pushes to `main` after tests pass.

For advanced deployment hardening and release checks, see:

- `DEPLOYMENT.md`
- `PRODUCTION_CHECKLIST.md`
- `SECURITY.md`
- `PERFORMANCE_BUDGET.md`
- `assets/images/SOCIAL_IMAGES.md`

---

## 📄 Pages Overview

| Page | Purpose | Key Features |
|------|---------|--------------|
| **index.html** | Landing/splash screen | Auto-redirect, loading animation |
| **manifesto_gateway.html** | Main hub | Philosophy, vision, navigation |
| **trinity_deep_dive.html** | Technical details | Architecture diagrams, system specs |
| **project_ai_cognitive_engine.html** | AI system | Cognitive architecture, ethics |
| **cerberus_security_fortress.html** | Security | Multi-layer security framework |
| **codex_deus_maximus_repository.html** | Knowledge base | Distributed architecture |
| **scenario_demonstrations.html** | Use cases | Interactive demos, case studies |
| **research_center.html** | Resources | Research, papers, references |
| **future_architectures.html** | Roadmap | Future vision, development plans |
| **trust_transparency_center.html** | Trust hub | Transparency, accountability |
| **jeremy_karrick_founder_profile.html** | About | Founder information |

---

## ♿ Accessibility Features

- ✅ Skip to content links
- ✅ ARIA labels and landmarks
- ✅ Keyboard navigation support
- ✅ Focus indicators
- ✅ Screen reader friendly
- ✅ Semantic HTML structure
- ✅ High contrast text
- ✅ Responsive font sizing

---

## 🔒 Security

- Apache `.htaccess` configuration for clean URLs
- Content Security Policy headers (recommended)
- No sensitive data in client-side code
- Secure external resource loading

---

## 🌐 Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

---

## 📈 Performance

- Minimal JavaScript dependencies
- Optimized CSS bundle
- Lazy-loaded images with fallbacks
- Progressive enhancement
- Clean semantic HTML

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

---

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 👤 Author

**Thirsty (Jeremy Karrick)**

- Website: [ThirstysProjects.com](https://thirstysprojects.com)
- GitHub: [@IAmSoThirsty](https://github.com/IAmSoThirsty)

---

## 🙏 Acknowledgments

- Built with [Rocket.new](https://rocket.new)
- Powered by [Tailwind CSS](https://tailwindcss.com)
- Typography by [Google Fonts](https://fonts.google.com)
- Icons and graphics created in-house

---

## 📊 Project Stats

- **Total Pages**: 11 HTML pages
- **Lines of Code**: ~13,886 HTML + 4,174 CSS
- **Dependencies**: 9 npm packages
- **Build Time**: < 2 seconds
- **Bundle Size**: ~79KB CSS (compiled)

---

<div align="center">

**Built with ❤️ and deep thought**

*Shaping the future of AGI-Human relations*

[⬆ Back to top](#-the-triumvirate)

</div>

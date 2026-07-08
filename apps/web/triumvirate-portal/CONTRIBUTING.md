# Contributing to The Triumvirate

Thank you for your interest in contributing to The Triumvirate! This document provides guidelines and instructions for contributing to this project.

## 🤝 Code of Conduct

We are committed to providing a welcoming and inspiring community for all. Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md) to ensure a respectful and constructive environment for everyone.

## 🚀 Getting Started

### Prerequisites

- Node.js (v12.x or higher)
- npm or yarn
- Git
- A modern web browser
- A text editor (VS Code recommended)

### Setting Up Your Development Environment

1. **Fork the repository**

   ```bash

   # Click the "Fork" button on GitHub

   ```

2. **Clone your fork**

   ```bash
   git clone https://github.com/YOUR_USERNAME/the_triumvirate.git
   cd the_triumvirate
   ```

3. **Add upstream remote**

   ```bash
   git remote add upstream https://github.com/IAmSoThirsty/the_triumvirate.git
   ```

4. **Install dependencies**

   ```bash
   npm install
   ```

5. **Start development server**

   ```bash
   npm run dev
   ```

6. **Open in browser**

   ```
   Open index.html in your browser or use a local server
   ```

## 📋 How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with:

- Clear, descriptive title
- Steps to reproduce the bug
- Expected behavior
- Actual behavior
- Screenshots (if applicable)
- Browser and OS information

### Suggesting Enhancements

Enhancement suggestions are welcome! Please create an issue with:

- Clear, descriptive title
- Detailed description of the proposed feature
- Rationale for why this enhancement would be useful
- Mockups or examples (if applicable)

### Pull Requests

1. **Create a branch**

   ```bash
   git checkout -b feature/your-feature-name

   # or

   git checkout -b fix/your-bug-fix
   ```

2. **Make your changes**
   - Follow the coding style of the project
   - Write clear, concise commit messages
   - Test your changes thoroughly
   - Update documentation if needed

3. **Commit your changes**

   ```bash
   git add .
   git commit -m "Add descriptive commit message"
   ```

4. **Push to your fork**

   ```bash
   git push origin feature/your-feature-name
   ```

5. **Open a Pull Request**
   - Go to the original repository on GitHub
   - Click "New Pull Request"
   - Select your branch
   - Fill in the PR template
   - Wait for review

## 💻 Development Guidelines

### Code Style

#### HTML

- Use semantic HTML5 elements
- Include proper ARIA labels for accessibility
- Maintain consistent indentation (2 spaces)
- Add comments for complex sections
- Keep accessibility in mind (skip links, keyboard navigation, screen reader support)

#### CSS (Tailwind)

- Use Tailwind utility classes when possible
- Follow the existing design system (Neural Depth palette)
- Add custom utilities to `tailwind.config.js` if needed
- Maintain responsive design principles
- Test on multiple screen sizes

#### JavaScript

- Use modern ES6+ syntax
- Keep inline scripts minimal
- Add comments for complex logic
- Ensure keyboard accessibility
- Test interactive features thoroughly

### Accessibility Requirements

All contributions must maintain WCAG 2.1 Level AA compliance:

- ✅ Semantic HTML structure
- ✅ ARIA labels where appropriate
- ✅ Keyboard navigation support
- ✅ High contrast text
- ✅ Screen reader compatibility
- ✅ Focus indicators
- ✅ Skip links

### Design System

Follow the established design system:

**Colors (Neural Depth Palette)**

- Primary: `#1E3A8A` (blue-900)
- Secondary: `#0891B2` (cyan-600)
- Accent: `#06B6D4` (cyan-500)
- Background: `#0F172A` (slate-900)
- Text: `#F8FAFC` (slate-50)

**Typography**

- Headlines: JetBrains Mono
- Body: Inter
- CTAs: Space Grotesk
- Code: Fira Code

**Spacing & Layout**

- Use Tailwind's spacing scale
- Mobile-first responsive approach
- Consistent breakpoints (sm, md, lg, xl, 2xl)

### Build Commands

```bash

# Build CSS for production

npm run build:css

# Watch CSS changes during development

npm run watch:css

# Start development mode

npm run dev

# Run tests

npm test

# Run tests in watch mode

npm run test:watch

# Run tests with coverage report

npm run test:coverage
```

### Testing Your Changes

Before submitting a PR:

1. ✅ Run the test suite with `npm test` and ensure all tests pass
2. ✅ Add tests for any new functionality
3. ✅ Test on multiple browsers (Chrome, Firefox, Safari, Edge)
4. ✅ Test on multiple devices (desktop, tablet, mobile)
5. ✅ Verify accessibility features work
6. ✅ Check keyboard navigation
7. ✅ Ensure no console errors
8. ✅ Build CSS and verify no issues
9. ✅ Review visual appearance matches design system

## 📝 Commit Message Guidelines

Use clear, descriptive commit messages:

```
Add feature: Brief description of what was added

More detailed explanation if needed. Wrap at 72 characters.
Include motivation and context.

- Bullet points for multiple changes
- Reference issues with #issue-number

```

**Examples:**

- `Add: XML sitemap for SEO optimization`
- `Fix: Mobile menu toggle not working on iOS`
- `Update: Accessibility improvements for screen readers`
- `Docs: Update README with new installation steps`

## 🎨 Content Contributions

### Writing Guidelines

- Use clear, concise language
- Maintain consistent tone (professional yet approachable)
- Check spelling and grammar
- Follow the existing content structure
- Cite sources when appropriate

### Adding New Pages

If adding a new page:

1. Create HTML file in `/pages/` directory
2. Follow existing page structure
3. Update navigation in all relevant pages
4. Add to sitemap.xml
5. Update README.md if needed
6. Include accessibility features

## 🐛 Bug Fix Process

1. Identify the bug and create an issue (if not exists)
2. Create a branch: `fix/bug-description`
3. Fix the bug with minimal changes
4. Test thoroughly
5. Submit PR with clear description
6. Reference the issue number

## ✨ Feature Addition Process

1. Discuss the feature in an issue first
2. Get approval from maintainers
3. Create a branch: `feature/feature-name`
4. Implement the feature
5. Update documentation
6. Test comprehensively
7. Submit PR with detailed description

## 📚 Documentation Contributions

Documentation improvements are always welcome:

- Fix typos or unclear wording
- Add examples or tutorials
- Improve README clarity
- Update outdated information
- Add inline code comments

## 🔍 Code Review Process

All PRs will be reviewed for:

- Code quality and style
- Functionality and correctness
- Accessibility compliance
- Performance impact
- Documentation completeness
- Test coverage (when applicable)

Reviewers may request changes. Please address feedback promptly and professionally.

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

## 💬 Questions?

If you have questions:

- Check existing issues and discussions
- Create a new issue with the "question" label
- Reach out to maintainers

## 🙏 Thank You!

Your contributions make The Triumvirate better for everyone. We appreciate your time and effort!

---

**Happy Contributing! 🚀**

*Built with ❤️ and deep thought*

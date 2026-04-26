---
type: index-documentation
module: web
tags: [web, nextjs, flask, documentation-index, overview]
created: 2026-04-20
status: production
related_systems: [all-web-modules]
stakeholders: [all-teams]
platform: web
---

# Project-AI Web Documentation Index

**Purpose:** Comprehensive documentation for Project-AI web application (Next.js frontend + Flask backend)  
**Audience:** Developers, DevOps, QA, and stakeholders  
**Last Updated:** 2026-04-20

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Documentation Structure](#documentation-structure)
3. [Architecture Overview](#architecture-overview)
4. [Getting Started](#getting-started)
5. [Development Workflow](#development-workflow)
6. [Deployment](#deployment)
7. [Troubleshooting](#troubleshooting)
8. [Contributing](#contributing)

---

## Quick Start

### For New Developers

**Read these in order:**
1. [Architecture Overview](#architecture-overview) (below)
2. [Flask Backend API](./01_FLASK_BACKEND_API.md) - Backend endpoints and governance integration
3. [React Frontend](./02_REACT_FRONTEND.md) - Next.js app structure and components
4. [Component Library](./06_COMPONENT_LIBRARY.md) - React component reference

**Then deep dive into:**
- [API Client Integration](./05_API_CLIENT_INTEGRATION.md) - HTTP client and state management
- [State Management](./07_STATE_MANAGEMENT.md) - Zustand stores
- [Styling Guide](./08_STYLING_GUIDE.md) - CSS variables and design system

### For DevOps

**Read these:**
1. [Deployment Guide](./03_DEPLOYMENT_GUIDE.md) - Docker, GitHub Pages, VPS
2. [Security Practices](./04_SECURITY_PRACTICES.md) - Authentication, CORS, rate limiting

### For QA

**Read this:**
1. [Testing Guide](./09_TESTING_GUIDE.md) - Unit, integration, and E2E tests

---

## Documentation Structure

### 10 Comprehensive Documents

| # | Document | Purpose | Audience |
|---|----------|---------|----------|
| **01** | [Flask Backend API](./01_FLASK_BACKEND_API.md) | API endpoints, request/response, governance pipeline | Backend, Integration |
| **02** | [React Frontend](./02_REACT_FRONTEND.md) | Next.js architecture, routing, state management | Frontend, Full-stack |
| **03** | [Deployment Guide](./03_DEPLOYMENT_GUIDE.md) | Docker, GitHub Pages, Vercel, VPS deployment | DevOps, Platform |
| **04** | [Security Practices](./04_SECURITY_PRACTICES.md) | Authentication, JWT, CORS, OWASP Top 10 | Security, Backend |
| **05** | [API Client Integration](./05_API_CLIENT_INTEGRATION.md) | Axios setup, interceptors, error handling | Frontend, Integration |
| **06** | [Component Library](./06_COMPONENT_LIBRARY.md) | React components reference | Frontend, UI/UX |
| **07** | [State Management](./07_STATE_MANAGEMENT.md) | Zustand stores, hooks, patterns | Frontend, Architecture |
| **08** | [Styling Guide](./08_STYLING_GUIDE.md) | CSS variables, design system, accessibility | Frontend, UI/UX |
| **09** | [Testing Guide](./09_TESTING_GUIDE.md) | Jest, React Testing Library, E2E | QA, Frontend |
| **10** | [**Web Documentation Index**](./10_DOCUMENTATION_INDEX.md) | This file - overview and navigation | All teams |

---

## Architecture Overview

### Technology Stack

```
┌─────────────────────────────────────────────────────────────┐
│                      CLIENT (Browser)                        │
│  Next.js 15 | React 18 | TypeScript 5 | Zustand 5           │
└────────────────────────────┬────────────────────────────────┘
                             │ HTTP/REST (Axios)
                             │ JWT Authentication
┌────────────────────────────▼────────────────────────────────┐
│                      FLASK BACKEND                           │
│  Python 3.11 | Flask | CORS | Rate Limiting                 │
└────────────────────────────┬────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────┐
│                   GOVERNANCE PIPELINE                        │
│  Runtime Router → Four Laws → AI Orchestrator               │
└────────────────────────────┬────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────┐
│                      CORE SYSTEMS                            │
│  UserManager | AIPersona | Memory | Learning | Plugins      │
└─────────────────────────────────────────────────────────────┘
```

### Key Features

**Frontend (Next.js):**
- ✅ Static export for GitHub Pages deployment
- ✅ TypeScript strict mode
- ✅ Zustand state management (1.2KB)
- ✅ Axios HTTP client with interceptors
- ✅ JWT token authentication
- ✅ 7-tab dashboard (Overview, Persona, Image Gen, Data Analysis, Learning, Security, Emergency)
- ✅ Mobile-responsive design
- ✅ Dark theme with Tron-inspired aesthetics

**Backend (Flask):**
- ✅ Thin adapter routing through governance pipeline
- ✅ JWT token generation (Argon2 password hashing)
- ✅ CORS configuration (whitelist-based)
- ✅ Rate limiting (10 login attempts/min, 30 AI requests/min)
- ✅ 5 API endpoints (status, login, chat, image, persona)
- ✅ Integration with 6 core AI systems

**Security:**
- ✅ Argon2 password hashing (not plaintext!)
- ✅ JWT with expiration (24 hours)
- ✅ CORS whitelist (no wildcards in production)
- ✅ Rate limiting per IP/user
- ✅ Input validation and sanitization
- ✅ XSS prevention (HTML escaping)
- ✅ CSRF protection (token-based)
- ✅ Security headers (CSP, X-Frame-Options)

---

## Getting Started

### Prerequisites

```bash
# Required software
node --version   # 18.0.0+
npm --version    # 9.0.0+
python --version # 3.11+
docker --version # 24.0.0+ (optional)
```

### Installation

**1. Clone Repository:**
```bash
git clone https://github.com/IAmSoThirsty/Project-AI.git
cd Project-AI
```

**2. Backend Setup:**
```bash
# Create virtual environment
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys:
# - OPENAI_API_KEY
# - HUGGINGFACE_API_KEY
# - SECRET_KEY

# Run backend
cd web/backend
python app.py
# Backend: http://localhost:5000
```

**3. Frontend Setup:**
```bash
# Navigate to web directory
cd web

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Edit .env:
# - NEXT_PUBLIC_API_URL=http://localhost:5000

# Run frontend
npm run dev
# Frontend: http://localhost:3000
```

**4. Verify Setup:**
```bash
# Test backend
curl http://localhost:5000/api/status
# Expected: {"status":"ok","component":"web-backend"}

# Test frontend
# Open browser: http://localhost:3000
# Expected: Login page with "Backend Online" indicator
```

---

## Development Workflow

### Directory Structure

```
web/
├── backend/                   # Flask API
│   ├── app.py                # Main Flask application (thin adapter)
│   └── __init__.py
│
├── app/                       # Next.js App Router
│   ├── layout.tsx            # Root layout
│   ├── page.tsx              # Login page
│   ├── error.tsx             # Error boundary
│   ├── loading.tsx           # Loading state
│   ├── not-found.tsx         # 404 page
│   └── dashboard/
│       └── page.tsx          # Dashboard page (protected route)
│
├── components/                # React components
│   ├── LoginForm.tsx         # Login form with validation
│   ├── StatusIndicator.tsx   # Backend health checker
│   ├── Dashboard.tsx         # Main dashboard (7 tabs)
│   └── ExcalidrawComponent.tsx
│
├── lib/                       # Core utilities (to be created)
│   ├── env.ts                # Environment validation (Zod)
│   ├── api-client.ts         # Axios HTTP client
│   ├── store.ts              # Zustand stores (auth, app)
│   ├── storage.ts            # localStorage wrappers
│   └── errors.ts             # Error handling utilities
│
├── utils/                     # Helper functions
│   ├── validators.ts         # Input validation
│   └── cn.ts                 # Class name utilities
│
├── styles/                    # Global styles
│   └── globals.css           # CSS variables, animations
│
├── public/                    # Static assets
│   ├── robots.txt
│   └── favicon.ico
│
├── e2e/                       # End-to-end tests (Playwright)
│   └── login-flow.spec.ts
│
├── __tests__/                 # Unit/integration tests
│   ├── components/
│   ├── lib/
│   └── utils/
│
├── next.config.js             # Next.js configuration
├── tsconfig.json              # TypeScript configuration
├── .eslintrc.json             # ESLint rules
├── .prettierrc                # Prettier formatting
├── jest.config.js             # Jest testing config
├── playwright.config.ts       # Playwright E2E config
├── package.json               # Dependencies
└── README.md                  # Frontend documentation
```

### Development Commands

```bash
# Backend (Flask)
cd web/backend
python app.py                  # Start development server

# Frontend (Next.js)
cd web
npm run dev                    # Start development server
npm run build                  # Build for production
npm run lint                   # Run ESLint
npm run type-check             # Run TypeScript type checking
npm test                       # Run Jest tests
npx playwright test            # Run E2E tests

# Combined (Docker Compose)
docker-compose up              # Start both backend and frontend
```

### Coding Standards

**TypeScript:**
- ✅ Strict mode enabled
- ✅ No implicit `any`
- ✅ Null safety
- ✅ Explicit return types for functions

**React:**
- ✅ Functional components with hooks
- ✅ `'use client'` directive for client components
- ✅ Prop validation with TypeScript interfaces
- ✅ Component composition over inheritance

**Python:**
- ✅ PEP 8 style guide
- ✅ Type hints for function signatures
- ✅ Docstrings for all functions
- ✅ Ruff linting

**Git:**
- ✅ Commit message format: `type: description`
- ✅ Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`
- ✅ Pull requests require 1 approval
- ✅ Co-authored-by trailer: `Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>`

---

## Deployment

### Quick Deploy (Development)

**GitHub Pages (Frontend Only):**
```bash
cd web
npm run build
# Deploy ./out/ directory to gh-pages branch
```

**Vercel (Full-Stack):**
```bash
cd web
vercel --prod
```

**Docker (Both):**
```bash
docker-compose up -d
```

### Production Deployment

**See:** [Deployment Guide](./03_DEPLOYMENT_GUIDE.md) for comprehensive instructions on:
- Docker multi-stage builds
- GitHub Actions CI/CD
- Vercel deployment
- VPS deployment with Nginx
- SSL/TLS certificates (Let's Encrypt)
- Environment configuration
- Health monitoring
- Log management

---

## Troubleshooting

### Common Issues

#### Issue: Backend Not Starting

**Symptom:** Flask server fails to start or crashes immediately

**Solution:**
1. Check Python version: `python --version` (must be 3.11+)
2. Verify virtual environment is activated
3. Install dependencies: `pip install -r requirements.txt`
4. Check `.env` file exists with required keys
5. View error logs: `tail -f logs/backend.log`

#### Issue: Frontend CORS Errors

**Symptom:** API requests blocked by CORS policy

**Solution:**
1. Ensure backend is running on port 5000
2. Check `NEXT_PUBLIC_API_URL` in `.env`
3. Verify CORS configuration in `app/core/security/middleware.py`
4. Add `http://localhost:3000` to CORS whitelist

#### Issue: Authentication Not Working

**Symptom:** 401 Unauthorized errors on all authenticated endpoints

**Solution:**
1. Check token is stored in localStorage: `localStorage.getItem('authToken')`
2. Verify token format in Authorization header: `Bearer <token>`
3. Check token hasn't expired (24 hour expiration)
4. Clear localStorage and re-login: `localStorage.clear()`

#### Issue: Build Errors (Next.js)

**Symptom:** `npm run build` fails with TypeScript errors

**Solution:**
1. Run type checking: `npm run type-check`
2. Fix TypeScript errors in reported files
3. Clear Next.js cache: `rm -rf .next`
4. Reinstall dependencies: `rm -rf node_modules && npm install`

#### Issue: Docker Container Not Starting

**Symptom:** Docker container exits immediately

**Solution:**
1. View logs: `docker logs project-ai-backend`
2. Check environment variables in `docker-compose.yml`
3. Verify Dockerfile syntax
4. Test image build: `docker build -t test-image .`

---

## Contributing

### Before Contributing

1. **Read the documentation** - Familiarize yourself with the architecture
2. **Check existing issues** - Avoid duplicate work
3. **Follow coding standards** - See [Development Workflow](#development-workflow)
4. **Write tests** - 80%+ coverage required

### Contribution Workflow

**1. Create Feature Branch:**
```bash
git checkout -b feature/your-feature-name
```

**2. Make Changes:**
- Follow coding standards
- Write tests for new features
- Update documentation if needed

**3. Run Quality Checks:**
```bash
# Frontend
npm run lint
npm run type-check
npm test
npm run test:coverage

# Backend
ruff check .
pytest -v
```

**4. Commit Changes:**
```bash
git add .
git commit -m "feat: add user profile page

- Add ProfilePage component
- Add API endpoint GET /api/user/profile
- Add tests for ProfilePage
- Update documentation

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

**5. Push and Create PR:**
```bash
git push origin feature/your-feature-name
# Create pull request on GitHub
```

**6. Address Review Comments:**
- Make requested changes
- Push new commits to same branch
- PR will auto-update

### Pull Request Checklist

- [ ] All tests passing
- [ ] Code linting passed
- [ ] TypeScript type checking passed
- [ ] Documentation updated
- [ ] 80%+ test coverage
- [ ] No security vulnerabilities (`npm audit`, `pip-audit`)
- [ ] Commit messages follow format
- [ ] Co-authored-by trailer added

---

## Documentation Maintenance

### Updating Documentation

**When to update:**
- New features added
- API endpoints changed
- Architecture modified
- Security practices updated
- Breaking changes introduced

**How to update:**
1. Locate relevant documentation file (see [Documentation Structure](#documentation-structure))
2. Edit Markdown file in `source-docs/web/`
3. Update `Last Updated` date in frontmatter
4. Commit with message: `docs: update [filename]`

**Documentation Review:**
- **Quarterly** - All documentation reviewed
- **On major releases** - All documentation updated
- **On breaking changes** - Immediate documentation update required

---

## Quick Reference

### Essential Commands

```bash
# Development
npm run dev                    # Start frontend dev server
python web/backend/app.py      # Start backend dev server

# Testing
npm test                       # Run Jest tests
npx playwright test            # Run E2E tests
pytest -v                      # Run backend tests

# Building
npm run build                  # Build frontend for production
docker-compose build           # Build Docker images

# Deployment
vercel --prod                  # Deploy to Vercel
docker-compose up -d           # Deploy with Docker

# Quality Checks
npm run lint                   # Lint frontend
ruff check .                   # Lint backend
npm run type-check             # TypeScript type checking
```

### Essential URLs

**Development:**
- Frontend: http://localhost:3000
- Backend: http://localhost:5000
- Backend API Status: http://localhost:5000/api/status

**Documentation:**
- GitHub Repository: https://github.com/IAmSoThirsty/Project-AI
- Issues: https://github.com/IAmSoThirsty/Project-AI/issues
- Pull Requests: https://github.com/IAmSoThirsty/Project-AI/pulls

**External Resources:**
- Next.js Docs: https://nextjs.org/docs
- React Docs: https://react.dev
- Zustand Docs: https://github.com/pmndrs/zustand
- Flask Docs: https://flask.palletsprojects.com

---

## Documentation Feedback

**Found an error or have a suggestion?**

1. Create an issue: https://github.com/IAmSoThirsty/Project-AI/issues/new
2. Tag with `documentation` label
3. Specify which document and section
4. Provide clear description of issue or suggestion

**Want to contribute to documentation?**

1. Follow [Contributing](#contributing) workflow
2. Edit Markdown files in `source-docs/web/`
3. Create pull request
4. Request review from documentation team

---

## Additional Resources

### Internal Documentation

- [Desktop App Documentation](../desktop/) - PyQt6 application docs
- [Core Systems Documentation](../core/) - AI systems, governance, runtime router
- [Architecture Quick Reference](../../.github/instructions/ARCHITECTURE_QUICK_REF.md) - Visual diagrams

### External Resources

- **Next.js:** https://nextjs.org/docs
- **React:** https://react.dev
- **TypeScript:** https://www.typescriptlang.org/docs
- **Zustand:** https://github.com/pmndrs/zustand
- **Axios:** https://axios-http.com
- **Flask:** https://flask.palletsprojects.com
- **Jest:** https://jestjs.io
- **Playwright:** https://playwright.dev

---

## Changelog

### 2026-04-20
- ✅ Created 10 comprehensive web documentation files
- ✅ Documented Flask backend API with governance pipeline
- ✅ Documented Next.js frontend architecture
- ✅ Documented deployment strategies (Docker, GitHub Pages, Vercel, VPS)
- ✅ Documented security best practices (JWT, CORS, rate limiting)
- ✅ Documented API client integration (Axios + Zustand)
- ✅ Documented component library (React components)
- ✅ Documented state management (Zustand stores)
- ✅ Documented styling guide (CSS variables, design system)
- ✅ Documented testing strategies (Jest, React Testing Library, Playwright)
- ✅ Created comprehensive documentation index

---

**Last Updated:** 2026-04-20  
**Maintainer:** Platform Team  
**Review Cycle:** Quarterly  
**Version:** 1.0.0

---

**Built with ❤️ by the Project-AI Team**

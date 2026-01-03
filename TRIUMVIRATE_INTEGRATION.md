# The_Triumvirate Integration Guide

## Overview

This document outlines the integration of **The_Triumvirate** repository as the new web interface for Project-AI. The Triumvirate will replace the current minimal web frontend with a comprehensive, production-ready web application.

## Integration Architecture

### Current State
```
Project-AI/
├── web/
│   ├── backend/          # Flask API (app.py)
│   └── frontend/         # Minimal HTML placeholder (index.html)
```

### Target State (Post-Integration)
```
Project-AI/
├── web/
│   ├── backend/          # Enhanced Flask API
│   ├── frontend/         # Legacy placeholder (deprecated)
│   └── triumvirate/      # Git submodule → The_Triumvirate repo
│       ├── src/          # React/Vite application
│       ├── public/       # Static assets
│       ├── package.json  # Node dependencies
│       └── vite.config.js
```

## Integration Methods

### Method 1: Git Submodule (Recommended)
Keeps The_Triumvirate as a separate repository while integrating it into Project-AI.

```bash
# Add The_Triumvirate as a submodule
cd /path/to/Project-AI
git submodule add https://github.com/IAmSoThirsty/The_Triumvirate.git web/triumvirate
git submodule update --init --recursive

# Update submodule to latest
git submodule update --remote web/triumvirate
```

**Advantages:**
- Maintains separate version control
- Easy to update independently
- Clear separation of concerns
- Existing pattern (Cerberus submodule already in use)

### Method 2: Direct Integration
Copy The_Triumvirate contents directly into Project-AI repository.

```bash
# Clone The_Triumvirate temporarily
git clone https://github.com/IAmSoThirsty/The_Triumvirate.git /tmp/triumvirate

# Copy contents to Project-AI
cp -r /tmp/triumvirate/* /path/to/Project-AI/web/triumvirate/
```

**Advantages:**
- Simpler deployment
- Single repository to manage
- Faster CI/CD

### Method 3: Monorepo Structure
Merge The_Triumvirate into Project-AI as a workspace.

## Pre-Integration Checklist

- [x] Document integration architecture
- [x] Identify current web structure
- [ ] Verify The_Triumvirate repository exists
- [ ] Review The_Triumvirate dependencies
- [ ] Plan API endpoint compatibility
- [ ] Update Docker configuration
- [ ] Configure build scripts
- [ ] Update deployment documentation

## Integration Steps

### Phase 1: Repository Setup
1. Verify The_Triumvirate repository is accessible
2. Choose integration method (recommend: git submodule)
3. Add repository reference to .gitmodules
4. Initialize submodule in web/triumvirate/

### Phase 2: Configuration
1. Update package.json to include Triumvirate build scripts
2. Configure environment variables (.env.example)
3. Update Docker Compose for Triumvirate services
4. Configure Vite proxy to Flask backend

### Phase 3: Backend Integration
1. Review Triumvirate API requirements
2. Extend Flask backend (web/backend/app.py)
3. Add new endpoints for Triumvirate features
4. Implement authentication bridge
5. Add WebSocket support (if needed)

### Phase 4: Build System
1. Add npm scripts for Triumvirate:
   - `npm run triumvirate:dev` - Development server
   - `npm run triumvirate:build` - Production build
   - `npm run triumvirate:preview` - Preview production build
2. Update Dockerfile for multi-stage build
3. Configure static file serving

### Phase 5: Testing
1. Test Triumvirate standalone
2. Test Flask backend connectivity
3. Integration tests for API communication
4. End-to-end tests
5. Build and deployment verification

### Phase 6: Documentation
1. Update README.md with Triumvirate information
2. Update DEPLOYMENT.md
3. Add Triumvirate-specific docs
4. Update API documentation
5. Create user guide for new web interface

## Configuration Files

### .gitmodules Update
```ini
[submodule "web/triumvirate"]
    path = web/triumvirate
    url = https://github.com/IAmSoThirsty/The_Triumvirate.git
    branch = main
```

### package.json Scripts Addition
```json
{
  "scripts": {
    "triumvirate:install": "cd web/triumvirate && npm install",
    "triumvirate:dev": "cd web/triumvirate && npm run dev",
    "triumvirate:build": "cd web/triumvirate && npm run build",
    "triumvirate:preview": "cd web/triumvirate && npm run preview",
    "web:full": "npm run triumvirate:build && python -m web.backend.app"
  }
}
```

### Docker Compose Enhancement
```yaml
services:
  web-backend:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./web/backend:/app/web/backend
    environment:
      - FLASK_ENV=development

  web-frontend:
    image: node:18
    working_dir: /app/web/triumvirate
    command: npm run dev
    ports:
      - "3000:3000"
    volumes:
      - ./web/triumvirate:/app/web/triumvirate
    depends_on:
      - web-backend
```

## API Compatibility

### Expected Endpoints (Flask Backend)
The Triumvirate frontend will likely need these endpoints:

```python
# Authentication
POST /api/auth/login
POST /api/auth/logout
GET  /api/auth/profile

# AI Persona
GET  /api/persona/state
POST /api/persona/update
GET  /api/persona/mood

# Chat/Intelligence
POST /api/chat/message
GET  /api/chat/history
POST /api/chat/clear

# Memory System
GET  /api/memory/knowledge
POST /api/memory/add
GET  /api/memory/search

# Learning Requests
GET  /api/learning/requests
POST /api/learning/submit
PUT  /api/learning/approve/:id
PUT  /api/learning/deny/:id

# Plugins
GET  /api/plugins/list
POST /api/plugins/enable/:id
POST /api/plugins/disable/:id

# Image Generation
POST /api/images/generate
GET  /api/images/history

# Status & Health
GET  /api/status
GET  /api/health
```

## Environment Variables

Add to `.env`:
```bash
# Triumvirate Web Frontend
VITE_API_URL=http://localhost:5000
VITE_WS_URL=ws://localhost:5000
TRIUMVIRATE_PORT=3000

# Feature Flags
ENABLE_TRIUMVIRATE=true
LEGACY_FRONTEND=false
```

## Deployment Scenarios

### Development
```bash
# Terminal 1: Backend
python -m web.backend.app

# Terminal 2: Triumvirate Frontend
cd web/triumvirate && npm run dev
```

### Production (Docker)
```bash
docker-compose up -d
# Triumvirate is built during image creation
# Nginx serves static files + proxies to Flask
```

### Production (Traditional)
```bash
# Build Triumvirate
cd web/triumvirate && npm run build

# Serve with Flask
python -m web.backend.app --serve-static
```

## Migration Strategy

### Backwards Compatibility
- Keep legacy `web/frontend/index.html` as fallback
- Add feature flag: `ENABLE_TRIUMVIRATE`
- Gradual rollout strategy

### User Migration
1. Phase 1: Triumvirate available at `/triumvirate` path
2. Phase 2: Both UIs available, user can choose
3. Phase 3: Triumvirate becomes default
4. Phase 4: Legacy frontend removed

## Troubleshooting

### Submodule Not Initialized
```bash
git submodule update --init --recursive
```

### Port Conflicts
- Backend: 5000 (Flask)
- Frontend: 3000 (Vite dev server)
- Adjust ports in docker-compose.yml if needed

### Build Failures
```bash
# Clean and rebuild
cd web/triumvirate
rm -rf node_modules dist
npm install
npm run build
```

### API Connection Issues
- Verify VITE_API_URL in .env
- Check CORS configuration in Flask
- Ensure backend is running

## Security Considerations

1. **CORS Configuration**: Update Flask to allow Triumvirate origin
2. **API Authentication**: Ensure token-based auth works with new frontend
3. **Environment Variables**: Never commit `.env` with secrets
4. **Content Security Policy**: Configure CSP headers for Triumvirate
5. **Dependency Scanning**: Run npm audit on Triumvirate dependencies

## Testing Strategy

### Unit Tests
- Test API endpoints in isolation
- Test React components individually

### Integration Tests
- Test API communication between frontend and backend
- Test authentication flow
- Test real-time updates (WebSocket)

### E2E Tests
- Full user workflows
- Cross-browser testing
- Mobile responsiveness

## Performance Optimization

1. **Code Splitting**: Utilize Vite's automatic code splitting
2. **Lazy Loading**: Load routes and components on demand
3. **API Caching**: Implement Redis for frequently accessed data
4. **CDN**: Serve static assets from CDN in production
5. **Compression**: Enable gzip/brotli compression

## Monitoring & Analytics

- Add application monitoring (e.g., Sentry)
- Track API performance
- Monitor user engagement
- Error logging and alerting

## References

- [Git Submodules Documentation](https://git-scm.com/book/en/v2/Git-Tools-Submodules)
- [Vite Configuration](https://vitejs.dev/config/)
- [Flask CORS](https://flask-cors.readthedocs.io/)
- Project-AI Documentation: `PROGRAM_SUMMARY.md`

## Status

**Current Status**: ⏳ Awaiting The_Triumvirate repository availability

**Last Updated**: 2026-01-03

**Integration Owner**: Project-AI Development Team

---

## Quick Start (When Available)

```bash
# 1. Add submodule
git submodule add https://github.com/IAmSoThirsty/The_Triumvirate.git web/triumvirate

# 2. Install dependencies
cd web/triumvirate && npm install

# 3. Configure environment
cp .env.example .env
# Edit .env with your settings

# 4. Start development
npm run triumvirate:dev

# Access at http://localhost:3000
```

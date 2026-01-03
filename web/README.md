# The_Triumvirate Integration - Quick Start

This document provides quick reference for integrating and working with The_Triumvirate web frontend.

## Prerequisites

- Git 2.x or higher
- Node.js 18.x or higher
- npm 9.x or higher
- Python 3.11+ (for backend)

## Quick Integration

### Option 1: Automated Integration (Recommended)

```bash
# Run the integration script
./scripts/integrate_triumvirate.sh

# Or with custom options
./scripts/integrate_triumvirate.sh --branch main --method submodule
```

### Option 2: Manual Integration

```bash
# 1. Add The_Triumvirate as a git submodule
git submodule add https://github.com/IAmSoThirsty/The_Triumvirate.git web/triumvirate

# 2. Initialize the submodule
git submodule update --init --recursive

# 3. Install dependencies
cd web/triumvirate
npm install

# 4. Configure environment
cp ../../.env.example ../../.env
# Edit .env and set ENABLE_TRIUMVIRATE=true

# 5. Start development server
npm run dev
```

## Development Workflow

### Start Full Stack Development

```bash
# Terminal 1: Flask Backend
python -m web.backend.app

# Terminal 2: Triumvirate Frontend
npm run triumvirate:dev
```

Access:
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000
- API Status: http://localhost:5000/api/status

### Using Docker

```bash
# Start with Triumvirate support
docker-compose -f docker-compose.yml -f docker-compose.triumvirate.yml up

# Or with override file
docker-compose up
```

### Build for Production

```bash
# Build Triumvirate
npm run triumvirate:build

# Run with static files
npm run web:full
```

## NPM Scripts

| Script | Description |
|--------|-------------|
| `triumvirate:install` | Install Triumvirate dependencies |
| `triumvirate:dev` | Start development server |
| `triumvirate:build` | Build for production |
| `triumvirate:preview` | Preview production build |
| `triumvirate:test` | Run tests |
| `web:backend` | Start Flask backend |
| `web:full` | Build frontend + start backend |

## Configuration

### Environment Variables

Add to `.env`:

```bash
# Enable Triumvirate
ENABLE_TRIUMVIRATE=true

# Frontend URLs
VITE_API_URL=http://localhost:5000
VITE_WS_URL=ws://localhost:5000
TRIUMVIRATE_PORT=3000

# Legacy frontend
LEGACY_FRONTEND=true
```

### CORS Configuration

CORS is automatically configured in `web/backend/app.py` to allow:
- http://localhost:3000 (Triumvirate dev server)
- http://localhost:5000 (Backend)

## Project Structure

```
web/
├── backend/              # Flask API backend
│   ├── app.py           # Main Flask application
│   └── __init__.py
├── frontend/            # Legacy minimal frontend
│   └── index.html
└── triumvirate/         # The_Triumvirate (git submodule)
    ├── src/             # React source code
    ├── public/          # Static assets
    ├── package.json     # Node dependencies
    └── vite.config.js   # Vite configuration
```

## Common Tasks

### Update Triumvirate to Latest

```bash
cd web/triumvirate
git pull origin main
npm install  # If dependencies changed
```

### Update Submodule Reference

```bash
# Pull latest changes in all submodules
git submodule update --remote

# Commit the updated reference
git add web/triumvirate
git commit -m "Update Triumvirate to latest"
```

### Switch Triumvirate Branch

```bash
cd web/triumvirate
git checkout develop  # or any branch
cd ../..
git add web/triumvirate
git commit -m "Switch Triumvirate to develop branch"
```

### Troubleshooting

#### Submodule is empty
```bash
git submodule update --init --recursive
```

#### Port already in use
```bash
# Change ports in .env
TRIUMVIRATE_PORT=3001
```

#### CORS errors
Ensure `ENABLE_TRIUMVIRATE=true` in `.env` and backend is running.

#### Build fails
```bash
cd web/triumvirate
rm -rf node_modules dist
npm install
npm run build
```

## Testing

### Frontend Tests
```bash
npm run triumvirate:test
```

### Backend Tests
```bash
pytest tests/
```

### Integration Tests
```bash
# Start both frontend and backend, then:
npm run test:integration
```

## API Endpoints

The Flask backend provides these endpoints for Triumvirate:

### Authentication
- `POST /api/auth/login` - Login user
- `GET /api/auth/profile` - Get user profile

### System
- `GET /api/status` - System status
- `GET /api/health` - Health check

See `TRIUMVIRATE_INTEGRATION.md` for complete API documentation.

## Deployment

### Production Build

```bash
# 1. Build Triumvirate
npm run triumvirate:build

# 2. Build Docker image
docker build -t project-ai:latest .

# 3. Run
docker run -p 5000:5000 project-ai:latest
```

### Docker Compose (Production)

```bash
docker-compose -f docker-compose.yml -f docker-compose.triumvirate.yml up -d
```

## Migration from Legacy Frontend

1. Both frontends can coexist:
   - Legacy: http://localhost:5000/
   - Triumvirate: http://localhost:3000/

2. Gradually migrate features to Triumvirate

3. Once stable, set `LEGACY_FRONTEND=false`

4. Remove legacy frontend when no longer needed

## Resources

- **Full Integration Guide**: `TRIUMVIRATE_INTEGRATION.md`
- **Project Documentation**: `README.md`
- **API Reference**: `docs/api/`
- **Architecture**: `PROGRAM_SUMMARY.md`

## Support

For issues or questions:
1. Check `TRIUMVIRATE_INTEGRATION.md`
2. Review existing GitHub issues
3. Create new issue with `[Triumvirate]` prefix

## License

Same as Project-AI - see LICENSE file.

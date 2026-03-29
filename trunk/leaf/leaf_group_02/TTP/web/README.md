<!-- # ============================================================================ # -->
<!-- # STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59 # -->
<!-- # COMPLIANCE: Sovereign Substrate / README.md # -->
<!-- # ============================================================================ # -->
<div align="right">
  <img src="https://img.shields.io/badge/DATE-2026-03-18-blueviolet?style=for-the-badge" alt="Date" />
  <img src="https://img.shields.io/badge/PRODUCTIVITY-ACTIVE-success?style=for-the-badge" alt="Productivity" />
</div>
<!-- # ============================================================================ #


<!-- # COMPLIANCE: Sovereign Substrate / README.md # -->
<!-- # ============================================================================ #

<!-- # Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master -->
# TTP Web Interface

Production-grade React/TypeScript web application for the Texture Pack Repository.

## Tech Stack

- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Fast build tool and dev server
- **Material-UI (MUI)** - Component library
- **TanStack Query** - Server state management
- **Zustand** - Client state management
- **React Router** - Routing
- **Axios** - HTTP client
- **Vitest** - Testing framework

## Features

- Browse texture packs with pagination and filtering
- Pack detail pages with download functionality
- User authentication (login/register)
- Profile management
- Responsive design with dark mode
- Type-safe API integration
- Optimized production builds with code splitting
- Comprehensive testing setup

## Getting Started

### Prerequisites

- Node.js 18+ and npm

### Installation

```bash
# Install dependencies
npm install
```

### Development

```bash
# Start development server
npm run dev

# Server runs at http://localhost:3000
# API proxy configured to http://localhost:8000
```

### Building

```bash
# Build for production
npm run build

# Preview production build
npm run preview
```

### Testing

```bash
# Run tests
npm test

# Run tests with UI
npm run test:ui

# Run tests with coverage
npm run test:coverage
```

### Linting

```bash
# Run ESLint
npm run lint
```

## Project Structure

```
web/
├── src/
│   ├── components/      # Reusable UI components
│   │   ├── Layout.tsx
│   │   ├── Navbar.tsx
│   │   ├── Footer.tsx
│   │   └── PackCard.tsx
│   ├── pages/           # Route pages
│   │   ├── HomePage.tsx
│   │   ├── PacksPage.tsx
│   │   ├── PackDetailPage.tsx
│   │   ├── LoginPage.tsx
│   │   ├── RegisterPage.tsx
│   │   ├── ProfilePage.tsx
│   │   └── NotFoundPage.tsx
│   ├── lib/             # API client and utilities
│   │   └── api.ts
│   ├── store/           # State management
│   │   └── authStore.ts
│   ├── types/           # TypeScript type definitions
│   │   └── index.ts
│   ├── test/            # Test setup
│   │   └── setup.ts
│   ├── theme.ts         # MUI theme configuration
│   ├── App.tsx          # Root component with routing
│   └── main.tsx         # Application entry point
├── public/              # Static assets
├── package.json
├── tsconfig.json
├── vite.config.ts
└── README.md
```

## API Integration

The app connects to the TTP API backend:
- Development: Proxied through Vite dev server to `http://localhost:8000`
- Production: Configure via environment variables

API client features:
- Automatic JWT token injection
- Request/response interceptors
- Error handling with auto-redirect on 401
- Type-safe request/response models

## State Management

### Server State (TanStack Query)
- API data caching and synchronization
- Automatic background refetching
- Optimistic updates
- Query invalidation

### Client State (Zustand)
- Authentication state
- User profile
- Persisted to localStorage

## Routing

Routes configured with React Router:
- `/` - Home page
- `/packs` - Browse packs (with filters)
- `/packs/:packId` - Pack details
- `/login` - User login
- `/register` - User registration
- `/profile` - User profile (protected)

## Environment Variables

Create `.env` file for configuration:

```bash
# API base URL (optional, defaults to /api/v1)
VITE_API_URL=http://localhost:8000/api/v1
```

## Deployment

### Docker

```bash
# Build image
docker build -t ttp-web:latest .

# Run container
docker run -p 3000:80 ttp-web:latest
```

### Static Hosting

Build and deploy the `dist/` folder to any static hosting service:
- Vercel
- Netlify
- AWS S3 + CloudFront
- Google Cloud Storage + CDN

## Performance

- Code splitting by route
- Vendor chunk optimization
- Tree shaking
- Image lazy loading
- React.memo for expensive components
- Query result caching

## Browser Support

- Chrome/Edge (latest 2 versions)
- Firefox (latest 2 versions)
- Safari (latest 2 versions)

## License

MIT License - See LICENSE file for details.

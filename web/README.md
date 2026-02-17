# Project-AI Web - Production-Grade Next.js Application

A complete, production-ready Next.js 14 web application for Project-AI, featuring TypeScript, server-side rendering, static export capabilities, and comprehensive integration with the Flask backend.

## 🚀 Features

- **Next.js 14** with App Router and React Server Components
- **TypeScript** with strict mode for type safety
- **Zustand** for lightweight state management
- **Static Export** configured for GitHub Pages deployment
- **Production-Grade Security** headers, input validation, XSS prevention
- **Comprehensive Error Handling** with error boundaries and logging
- **Backend Integration** via Axios HTTP client with interceptors
- **Responsive Design** with mobile-first approach
- **Authentication System** with JWT token management
- **Dashboard** with 7 feature tabs (Overview, Persona, Image Gen, Data Analysis, Learning, Security, Emergency)

## 📋 Prerequisites

- Node.js 18.0.0 or higher
- npm 9.0.0 or higher
- Flask backend running on port 5000 (optional for development)

## 🛠️ Installation

```bash

# Install dependencies

npm install

# Create environment file

cp .env.example .env
```

## 🏃 Development

```bash

# Start development server

npm run dev

# Open browser to http://localhost:3000

```

## 🏗️ Build

```bash

# Build for production (static export)

npm run build

# Output directory: ./out/

```

## 📦 Scripts

| Script | Description |
|--------|-------------|
| `npm run dev` | Start development server |
| `npm run build` | Build for production with static export |
| `npm run export` | Alias for build (static export) |
| `npm start` | Start production server |
| `npm run lint` | Run ESLint |
| `npm run lint:fix` | Fix linting issues |
| `npm run type-check` | Run TypeScript type checking |
| `npm run format` | Format code with Prettier |
| `npm run format:check` | Check code formatting |
| `npm test` | Run tests |
| `npm run security:audit` | Run npm security audit |

## 📁 Project Structure

```
web/
├── app/                    # Next.js App Router
│   ├── layout.tsx         # Root layout
│   ├── page.tsx           # Home/Login page
│   ├── error.tsx          # Error boundary
│   ├── loading.tsx        # Loading state
│   ├── not-found.tsx      # 404 page
│   └── dashboard/         # Dashboard route
│       └── page.tsx       # Dashboard page
├── components/            # React components
│   ├── LoginForm.tsx      # Login form with validation
│   ├── StatusIndicator.tsx# Backend status checker
│   └── Dashboard.tsx      # Main dashboard
├── lib/                   # Core utilities
│   ├── env.ts             # Environment validation
│   ├── api-client.ts      # Axios API client
│   └── store.ts           # Zustand stores
├── utils/                 # Utility functions
│   ├── validators.ts      # Input validation
│   └── cn.ts              # Class name utility
├── styles/                # Global styles
│   └── globals.css        # CSS variables and utilities
├── public/                # Static assets
│   └── robots.txt         # SEO configuration
├── types/                 # TypeScript types
├── hooks/                 # Custom React hooks
├── next.config.js         # Next.js configuration
├── tsconfig.json          # TypeScript configuration
├── .eslintrc.json         # ESLint configuration
├── .prettierrc            # Prettier configuration
├── package.json           # Dependencies and scripts
└── README.md              # This file
```

## 🔐 Environment Variables

```env

# API Configuration

NEXT_PUBLIC_API_URL=http://localhost:5000
NEXT_PUBLIC_API_TIMEOUT=30000

# Application Configuration

NEXT_PUBLIC_APP_NAME=Project-AI
NEXT_PUBLIC_APP_VERSION=1.0.0
NEXT_PUBLIC_ENV=production
```

## 🔒 Security Features

- **CSP Headers** - Content Security Policy
- **X-Frame-Options** - Clickjacking protection
- **X-XSS-Protection** - Cross-site scripting protection
- **Input Validation** - All user inputs sanitized and validated
- **Authentication** - Token-based authentication with localStorage
- **Error Handling** - Graceful error handling with user-friendly messages
- **Rate Limiting** - API client timeout and retry logic

## 🧪 Testing

```bash

# Run tests

npm test

# Run tests in watch mode

npm run test:watch

# Generate coverage report

npm run test:coverage
```

## 📊 Dashboard Features

### 1. Overview Tab

- System information
- Feature status cards
- User profile

### 2. AI Persona Tab

- Personality trait configuration
- Mood tracking
- State persistence

### 3. Image Generation Tab

- Dual backend support (HF Stable Diffusion, OpenAI DALL-E)
- 10 style presets
- Content filtering

### 4. Data Analysis Tab

- CSV/XLSX/JSON support
- K-means clustering
- Statistical analysis

### 5. Learning Paths Tab

- Learning request system
- Black Vault (denied content tracking)
- Knowledge base (6 categories)

### 6. Security Tab

- GitHub integration
- CTF challenges
- Security resources

### 7. Emergency Tab

- Emergency alert system
- Email notifications
- Contact management

## 🔌 API Integration

The application integrates with the Flask backend via Axios:

```typescript
// Login
await apiClient.login({ username, password });

// Get profile
await apiClient.getProfile();

// Check status
await apiClient.checkStatus();
```

### Available Endpoints

- `POST /api/auth/login` - User login
- `GET /api/auth/profile` - Get user profile
- `GET /api/status` - Backend health check

## 🚀 Deployment

### GitHub Pages

The workflow at `.github/workflows/nextjs.yml` automatically builds and deploys to GitHub Pages on push to main.

### Manual Deployment

```bash

# Build static export

npm run build

# Deploy the ./out/ directory to your hosting provider

```

### Docker Deployment

```dockerfile
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/out /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## 🔍 Troubleshooting

### Build Errors

```bash

# Clear Next.js cache

rm -rf .next

# Reinstall dependencies

rm -rf node_modules package-lock.json
npm install
```

### Backend Connection Issues

1. Ensure Flask backend is running on port 5000
2. Check CORS configuration in Flask
3. Verify `NEXT_PUBLIC_API_URL` in `.env`

### TypeScript Errors

```bash

# Run type checking

npm run type-check
```

## 📝 Code Style

- **ESLint** for code linting
- **Prettier** for code formatting
- **TypeScript strict mode** for type safety
- **Security plugin** for security linting

## 🤝 Contributing

1. Follow the existing code structure
2. Use TypeScript for all new files
3. Run linting and tests before committing
4. Follow the Project-AI governance profile standards

## 📄 License

Same as Project-AI main project (MIT)

## 🔗 Links

- [Next.js Documentation](https://nextjs.org/docs)
- [React Documentation](https://react.dev)
- [TypeScript Documentation](https://www.typescriptlang.org)
- [Zustand Documentation](https://github.com/pmndrs/zustand)
- [Project-AI Repository](https://github.com/IAmSoThirsty/Project-AI)

## 📞 Support

For issues and questions, please create a GitHub issue in the Project-AI repository.

---

**Built with ❤️ by the Project-AI Team**

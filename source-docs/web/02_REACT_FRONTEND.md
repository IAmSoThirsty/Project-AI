---
type: frontend-reference
module: web.frontend
tags: [nextjs, react, typescript, zustand, components]
created: 2026-04-20
status: production
related_systems: [flask-backend, api-client, state-management]
stakeholders: [frontend-team, ux-team, integration-team]
platform: web
dependencies: [nextjs@15, react@18, zustand@5, axios@1.7]
---

# React Frontend Architecture

**Framework:** Next.js 15 (App Router)  
**Language:** TypeScript (strict mode)  
**State Management:** Zustand  
**HTTP Client:** Axios  
**Styling:** CSS Modules + Global CSS Variables

---

## Architecture Overview

### Technology Stack

```
Next.js 15 (App Router + React Server Components)
├── React 18.3 (UI framework)
├── TypeScript 5.7 (type safety)
├── Zustand 5.0 (lightweight state management)
├── Axios 1.7 (HTTP client with interceptors)
├── Zod 3.24 (runtime validation)
├── date-fns 4.1 (date utilities)
└── clsx 2.1 (conditional classNames)
```

### Project Structure

```
web/
├── app/                         # Next.js App Router
│   ├── layout.tsx              # Root layout (metadata, fonts, providers)
│   ├── page.tsx                # Home/Login page
│   ├── error.tsx               # Error boundary component
│   ├── loading.tsx             # Global loading state
│   ├── not-found.tsx           # 404 page
│   └── dashboard/              # Dashboard route
│       └── page.tsx            # Protected dashboard page
│
├── components/                  # React components
│   ├── LoginForm.tsx           # Login form with validation
│   ├── StatusIndicator.tsx     # Backend health check indicator
│   ├── Dashboard.tsx           # Main dashboard with 7 tabs
│   └── ExcalidrawComponent.tsx # Excalidraw integration (optional)
│
├── lib/                         # Core utilities
│   ├── env.ts                  # Environment variable validation (Zod)
│   ├── api-client.ts           # Axios HTTP client with interceptors
│   └── store.ts                # Zustand state stores (auth, UI)
│
├── utils/                       # Helper functions
│   ├── validators.ts           # Input validation utilities
│   └── cn.ts                   # Class name merger (clsx + tailwind-merge)
│
├── styles/                      # Global styles
│   └── globals.css             # CSS variables, animations, utilities
│
├── public/                      # Static assets
│   ├── robots.txt              # SEO configuration
│   └── favicon.ico             # App icon
│
├── types/                       # TypeScript type definitions
│   └── index.ts                # Shared types
│
├── hooks/                       # Custom React hooks
│   └── useAuth.ts              # Authentication hook
│
├── next.config.js               # Next.js configuration (static export)
├── tsconfig.json                # TypeScript strict mode config
├── .eslintrc.json               # ESLint rules
├── .prettierrc                  # Prettier formatting
├── package.json                 # Dependencies and scripts
└── README.md                    # Frontend documentation
```

---

## Core Components

### 1. Login Form Component

**File:** `components/LoginForm.tsx`  
**Purpose:** User authentication with input validation and error handling

**Features:**
- Real-time input validation (username 3-20 chars, password 8+ chars)
- Loading state during API call
- Error display with auto-dismissal
- Demo credentials quick-fill
- Responsive design (mobile-first)

**Props:** None (uses Zustand store directly)

**Usage:**
```tsx
import LoginForm from '@/components/LoginForm';

export default function LoginPage() {
  return (
    <div className="container">
      <LoginForm />
    </div>
  );
}
```

**State Management:**
```tsx
const { login, error, isLoading } = useAuthStore();
```

**Validation Rules:**
```tsx
// Username: 3-20 alphanumeric characters
const usernameValid = /^[a-zA-Z0-9_]{3,20}$/.test(username);

// Password: 8+ characters
const passwordValid = password.length >= 8;
```

**API Integration:**
```tsx
const handleSubmit = async (e: React.FormEvent) => {
  e.preventDefault();
  
  try {
    await login({ username, password });
    router.push('/dashboard');
  } catch (error) {
    // Error handled by Zustand store
  }
};
```

---

### 2. Dashboard Component

**File:** `components/Dashboard.tsx`  
**Purpose:** Main application interface with 7 feature tabs

**Props:**
```tsx
interface DashboardProps {
  user: User;           // Authenticated user object
  onLogout: () => void; // Logout callback
}
```

**Tabs:**
1. **Overview** - System information, feature status cards
2. **AI Persona** - 8 personality traits configuration
3. **Image Generation** - DALL-E 3 / Stable Diffusion interface
4. **Data Analysis** - CSV/XLSX/JSON analysis with K-means
5. **Learning Paths** - Learning request system with Black Vault
6. **Security** - GitHub integration, CTF challenges
7. **Emergency** - Emergency alert system with email

**State:**
```tsx
const [activeTab, setActiveTab] = useState<TabType>('overview');
```

**Tab Navigation:**
```tsx
const tabs = [
  { id: 'overview', label: 'Overview', icon: '📊' },
  { id: 'persona', label: 'AI Persona', icon: '🤖' },
  { id: 'image-gen', label: 'Image Generation', icon: '🎨' },
  // ... 4 more tabs
];
```

**Responsive Design:**
- Sticky header with logout button
- Scrollable tab navigation (horizontal overflow)
- Active tab highlighting (gradient background)
- Mobile-first layout (flexbox)

---

### 3. Status Indicator Component

**File:** `components/StatusIndicator.tsx`  
**Purpose:** Real-time backend health monitoring

**Features:**
- Auto-polling every 10 seconds
- Color-coded status (green=online, red=offline, yellow=loading)
- Tooltip with last check time
- Dismissible alert

**States:**
```tsx
type Status = 'checking' | 'online' | 'offline';
```

**API Integration:**
```typescript
const checkBackendStatus = async () => {
  try {
    const response = await apiClient.get('/api/status');
    if (response.data.status === 'ok') {
      setStatus('online');
    }
  } catch {
    setStatus('offline');
  }
};

useEffect(() => {
  checkBackendStatus();
  const interval = setInterval(checkBackendStatus, 10000);
  return () => clearInterval(interval);
}, []);
```

**Visual Indicator:**
```tsx
<div className={`status-indicator ${status}`}>
  {status === 'online' && '✅ Backend Online'}
  {status === 'offline' && '❌ Backend Offline'}
  {status === 'checking' && '🔄 Checking...'}
</div>
```

---

## State Management (Zustand)

### Auth Store

**File:** `lib/store.ts`  
**Purpose:** Global authentication state

**Store Definition:**
```typescript
interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => void;
  checkAuth: () => void;
  clearError: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,
  
  login: async (credentials) => {
    set({ isLoading: true, error: null });
    try {
      const response = await apiClient.post('/api/auth/login', credentials);
      const { token, user } = response.data;
      
      localStorage.setItem('authToken', token);
      localStorage.setItem('user', JSON.stringify(user));
      
      set({
        user,
        token,
        isAuthenticated: true,
        isLoading: false,
      });
    } catch (error) {
      set({
        error: 'Invalid credentials',
        isLoading: false,
      });
      throw error;
    }
  },
  
  logout: () => {
    localStorage.removeItem('authToken');
    localStorage.removeItem('user');
    set({
      user: null,
      token: null,
      isAuthenticated: false,
    });
  },
  
  checkAuth: () => {
    const token = localStorage.getItem('authToken');
    const user = localStorage.getItem('user');
    
    if (token && user) {
      set({
        token,
        user: JSON.parse(user),
        isAuthenticated: true,
      });
    }
  },
  
  clearError: () => set({ error: null }),
}));
```

**Usage in Components:**
```tsx
function MyComponent() {
  const { user, isAuthenticated, login, logout } = useAuthStore();
  
  if (!isAuthenticated) {
    return <LoginForm />;
  }
  
  return <Dashboard user={user} onLogout={logout} />;
}
```

---

## API Client (Axios)

### Configuration

**File:** `lib/api-client.ts`  
**Purpose:** HTTP client with interceptors, authentication, and error handling

**Setup:**
```typescript
import axios from 'axios';

const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor (add auth token)
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor (handle errors globally)
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Unauthorized - clear auth and redirect to login
      useAuthStore.getState().logout();
      window.location.href = '/';
    }
    return Promise.reject(error);
  }
);

export default apiClient;
```

### API Methods

**Login:**
```typescript
export async function login(credentials: LoginCredentials) {
  const response = await apiClient.post('/api/auth/login', credentials);
  return response.data;
}
```

**Get Profile:**
```typescript
export async function getProfile() {
  const response = await apiClient.get('/api/user/profile');
  return response.data;
}
```

**AI Chat:**
```typescript
export async function sendChatMessage(prompt: string, model?: string) {
  const response = await apiClient.post('/api/ai/chat', {
    prompt,
    model: model || 'gpt-4',
  });
  return response.data;
}
```

**Image Generation:**
```typescript
export async function generateImage(prompt: string, options?: ImageOptions) {
  const response = await apiClient.post('/api/ai/image', {
    prompt,
    model: options?.model || 'dall-e-3',
    size: options?.size || '1024x1024',
  });
  return response.data;
}
```

---

## Routing & Navigation

### App Router Structure

**Next.js 15 App Router** uses file-system based routing:

```
app/
├── layout.tsx         → Root layout (applies to all pages)
├── page.tsx           → / (home/login)
├── error.tsx          → Error boundary (catches errors in any page)
├── loading.tsx        → Loading state (Suspense fallback)
├── not-found.tsx      → 404 page
└── dashboard/
    └── page.tsx       → /dashboard (protected route)
```

### Protected Routes

**Implementation:**
```tsx
// app/dashboard/page.tsx
'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/lib/store';
import Dashboard from '@/components/Dashboard';

export default function DashboardPage() {
  const router = useRouter();
  const { isAuthenticated, user, logout } = useAuthStore();
  
  // Redirect to login if not authenticated
  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/');
    }
  }, [isAuthenticated, router]);
  
  if (!isAuthenticated || !user) {
    return <div>Loading...</div>;
  }
  
  return <Dashboard user={user} onLogout={logout} />;
}
```

### Navigation Between Pages

**Programmatic Navigation:**
```tsx
import { useRouter } from 'next/navigation';

function MyComponent() {
  const router = useRouter();
  
  const handleLogin = () => {
    router.push('/dashboard');
  };
  
  const handleLogout = () => {
    router.push('/');
  };
  
  return (
    <button onClick={handleLogin}>Go to Dashboard</button>
  );
}
```

**Link Component:**
```tsx
import Link from 'next/link';

function Nav() {
  return (
    <nav>
      <Link href="/">Home</Link>
      <Link href="/dashboard">Dashboard</Link>
    </nav>
  );
}
```

---

## Styling & Design System

### CSS Variables

**File:** `styles/globals.css`

**Color Palette:**
```css
:root {
  /* Primary colors */
  --primary: #00d4ff;        /* Tron cyan */
  --primary-dark: #0099cc;   /* Darker cyan */
  --secondary: #ff00ff;      /* Magenta */
  
  /* Grayscale */
  --bg-dark: #0a0a0f;        /* Background */
  --bg-card: #1a1a2e;        /* Card background */
  --text-primary: #ffffff;   /* Primary text */
  --text-secondary: #a0a0a0; /* Secondary text */
  
  /* Status colors */
  --success: #00ff88;
  --warning: #ffaa00;
  --error: #ff4444;
}
```

**Typography:**
```css
:root {
  --font-mono: 'Courier New', monospace;
  --font-sans: system-ui, -apple-system, sans-serif;
  
  --text-xs: 0.75rem;   /* 12px */
  --text-sm: 0.875rem;  /* 14px */
  --text-base: 1rem;    /* 16px */
  --text-lg: 1.25rem;   /* 20px */
  --text-xl: 1.5rem;    /* 24px */
  --text-2xl: 2rem;     /* 32px */
}
```

**Spacing:**
```css
:root {
  --spacing-1: 0.25rem;  /* 4px */
  --spacing-2: 0.5rem;   /* 8px */
  --spacing-3: 0.75rem;  /* 12px */
  --spacing-4: 1rem;     /* 16px */
  --spacing-6: 1.5rem;   /* 24px */
  --spacing-8: 2rem;     /* 32px */
}
```

### Component Classes

**Card:**
```css
.card {
  background: var(--bg-card);
  border: 1px solid rgba(0, 212, 255, 0.3);
  border-radius: 12px;
  padding: var(--spacing-6);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.5);
}
```

**Button:**
```css
.button {
  padding: var(--spacing-3) var(--spacing-6);
  border-radius: 8px;
  font-weight: 600;
  transition: all 0.2s;
}

.button-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.button-secondary {
  background: transparent;
  border: 2px solid var(--primary);
  color: var(--primary);
}
```

**Input:**
```css
.input {
  width: 100%;
  padding: var(--spacing-3);
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: var(--text-base);
}

.input:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(0, 212, 255, 0.2);
}
```

---

## Environment Configuration

### Environment Variables

**File:** `.env` (create from `.env.example`)

```bash
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:5000
NEXT_PUBLIC_API_TIMEOUT=30000

# Application Configuration
NEXT_PUBLIC_APP_NAME=Project-AI
NEXT_PUBLIC_APP_VERSION=1.0.0
NEXT_PUBLIC_ENV=production

# Feature Flags (optional)
NEXT_PUBLIC_ENABLE_ANALYTICS=false
NEXT_PUBLIC_ENABLE_DEBUG=false
```

### Validation with Zod

**File:** `lib/env.ts`

```typescript
import { z } from 'zod';

const envSchema = z.object({
  NEXT_PUBLIC_API_URL: z.string().url(),
  NEXT_PUBLIC_API_TIMEOUT: z.coerce.number().positive(),
  NEXT_PUBLIC_APP_NAME: z.string().min(1),
  NEXT_PUBLIC_APP_VERSION: z.string().regex(/^\d+\.\d+\.\d+$/),
  NEXT_PUBLIC_ENV: z.enum(['development', 'production', 'test']),
});

export const env = envSchema.parse({
  NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
  NEXT_PUBLIC_API_TIMEOUT: process.env.NEXT_PUBLIC_API_TIMEOUT,
  NEXT_PUBLIC_APP_NAME: process.env.NEXT_PUBLIC_APP_NAME,
  NEXT_PUBLIC_APP_VERSION: process.env.NEXT_PUBLIC_APP_VERSION,
  NEXT_PUBLIC_ENV: process.env.NEXT_PUBLIC_ENV,
});
```

**Usage:**
```typescript
import { env } from '@/lib/env';

const apiUrl = env.NEXT_PUBLIC_API_URL;
```

---

## Testing

### Test Setup

**File:** `jest.config.js`

```javascript
module.exports = {
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/$1',
  },
  collectCoverageFrom: [
    'components/**/*.{ts,tsx}',
    'lib/**/*.{ts,tsx}',
    'utils/**/*.{ts,tsx}',
  ],
};
```

### Component Testing

**Example:**
```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import LoginForm from '@/components/LoginForm';

describe('LoginForm', () => {
  it('renders login form', () => {
    render(<LoginForm />);
    expect(screen.getByPlaceholderText('Username')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Password')).toBeInTheDocument();
  });
  
  it('validates input before submission', async () => {
    render(<LoginForm />);
    const submitButton = screen.getByRole('button', { name: /login/i });
    
    fireEvent.click(submitButton);
    
    expect(screen.getByText('Username must be 3-20 characters')).toBeInTheDocument();
  });
});
```

---

## Build & Deployment

### Development

```bash
npm run dev  # Start dev server on port 3000
```

### Production Build

```bash
npm run build  # Builds static export to ./out/
```

### Static Export Configuration

**File:** `next.config.js`

```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',  // Enable static HTML export
  images: {
    unoptimized: true,  // Required for static export
  },
  trailingSlash: true,  // Add trailing slashes to URLs
};

module.exports = nextConfig;
```

### Deployment Targets

**GitHub Pages:**
```bash
npm run build
# Deploy ./out/ directory to gh-pages branch
```

**Vercel:**
```bash
vercel deploy --prod
```

**Nginx:**
```nginx
server {
  listen 80;
  server_name example.com;
  
  root /var/www/project-ai/out;
  index index.html;
  
  location / {
    try_files $uri $uri/ /index.html;
  }
}
```

---

## Best Practices

### 1. TypeScript Strict Mode

**Always enable strict mode:**
```json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true
  }
}
```

### 2. Component Composition

**Prefer small, focused components:**
```tsx
// ❌ Bad (monolithic component)
function Dashboard() {
  return (
    <div>
      <Header />
      <Tabs />
      <Content />
      <Footer />
    </div>
  );
}

// ✅ Good (composed from smaller components)
function Dashboard() {
  return (
    <DashboardLayout>
      <DashboardHeader />
      <DashboardTabs />
      <DashboardContent />
    </DashboardLayout>
  );
}
```

### 3. Error Boundaries

**Wrap error-prone components:**
```tsx
// app/error.tsx
'use client';

export default function Error({ error, reset }: {
  error: Error;
  reset: () => void;
}) {
  return (
    <div>
      <h2>Something went wrong!</h2>
      <p>{error.message}</p>
      <button onClick={reset}>Try again</button>
    </div>
  );
}
```

### 4. Loading States

**Always show loading feedback:**
```tsx
function MyComponent() {
  const [data, setData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  
  if (isLoading) {
    return <div>Loading...</div>;
  }
  
  return <div>{data}</div>;
}
```

### 5. Input Validation

**Validate all user inputs:**
```typescript
import { z } from 'zod';

const loginSchema = z.object({
  username: z.string().min(3).max(20),
  password: z.string().min(8),
});

function validateLogin(data: unknown) {
  return loginSchema.safeParse(data);
}
```

---

## Troubleshooting

### Issue: Hydration Mismatch

**Symptom:** Server/client HTML mismatch error

**Solution:**
```tsx
const [mounted, setMounted] = useState(false);

useEffect(() => {
  setMounted(true);
}, []);

if (!mounted) return null;
```

### Issue: localStorage Not Defined (SSR)

**Symptom:** `localStorage is not defined` error

**Solution:**
```tsx
const getToken = () => {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('authToken');
};
```

### Issue: CORS Errors

**Symptom:** API requests blocked by CORS policy

**Solution:**
1. Ensure backend CORS is configured
2. Use proxy in `next.config.js`:

```javascript
module.exports = {
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:5000/api/:path*',
      },
    ];
  },
};
```

---

## Related Documentation

- [Flask Backend API](./01_FLASK_BACKEND_API.md)
- [API Client Integration](./05_API_CLIENT_INTEGRATION.md)
- [Component Library](./06_COMPONENT_LIBRARY.md)
- [Deployment Guide](./03_DEPLOYMENT_GUIDE.md)

---

**Last Updated:** 2026-04-20  
**Maintainer:** Frontend Team  
**Review Cycle:** Quarterly

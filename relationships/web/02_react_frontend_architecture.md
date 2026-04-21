# React Frontend Architecture Relationships

**System:** Next.js 14 React Frontend  
**Location:** `web/`  
**Framework:** Next.js 14 (App Router), React 18, TypeScript  

## Overview

The React frontend is a **production-grade Next.js 14 application** using the App Router pattern, TypeScript for type safety, and a custom state management solution. It implements the "Leather Book" UI design with Tron-inspired aesthetics.

## Core Technology Stack

```
Next.js 14 (App Router)
  └─ React 18 (Client Components)
      └─ TypeScript 5.x (Type Safety)
          └─ Custom Store (Auth State)
              └─ Tailwind CSS (Styling)
```

## Directory Structure

```
web/
├── app/                    # Next.js App Router
│   ├── page.tsx           # Login page (/)
│   ├── dashboard/         # Protected routes
│   │   └── page.tsx       # Dashboard (/dashboard)
│   ├── layout.tsx         # Root layout
│   ├── error.tsx          # Error boundary
│   ├── loading.tsx        # Loading UI
│   └── not-found.tsx      # 404 page
├── components/            # React components
│   ├── Dashboard.tsx      # Main dashboard with 7 tabs
│   ├── LoginForm.tsx      # Authentication form
│   ├── StatusIndicator.tsx # Backend health check
│   └── ExcalidrawComponent.tsx # Diagram editor
├── utils/                 # Utility functions
│   ├── validators.ts      # Input validation
│   └── cn.ts             # Class name utilities
├── styles/               # Global styles
├── public/               # Static assets
└── backend/              # Flask API (separate)
```

## Component Hierarchy

### Root Layout (`app/layout.tsx`)

```tsx
<html lang="en">
  <body>
    <ThemeProvider>
      {children}  // Page content injected here
    </ThemeProvider>
  </body>
</html>
```

**Responsibilities:**
- Global metadata (title, description)
- Font loading (Inter, system fonts)
- CSS variables for theming
- Root layout structure

**Tron Color Scheme:**
```css
:root {
  --primary: #00ffff;      /* Tron cyan */
  --secondary: #00ff00;    /* Tron green */
  --background: #0a0a0a;   /* Dark background */
  --foreground: #ffffff;   /* White text */
}
```

### Page Components

#### 1. **Login Page (`app/page.tsx`)**

**Route:** `/`  
**Component Tree:**
```
HomePage (Client Component)
├─ useAuthStore() → Authentication state
├─ StatusIndicator → Backend health check
├─ LoginForm → Authentication UI
└─ Router navigation → /dashboard on success
```

**State Management:**
```tsx
const { isAuthenticated, isLoading } = useAuthStore();

useEffect(() => {
  if (isAuthenticated && !isLoading) {
    router.push('/dashboard');  // Auto-redirect
  }
}, [isAuthenticated, isLoading]);
```

**Hydration Safety:**
```tsx
const [mounted, setMounted] = useState(false);

useEffect(() => {
  setMounted(true);  // Prevent hydration mismatch
}, []);

if (!mounted) return null;
```

#### 2. **Dashboard Page (`app/dashboard/page.tsx`)**

**Route:** `/dashboard`  
**Protected:** Requires authentication  
**Component Tree:**
```
DashboardPage (Client Component)
├─ useAuthStore() → User profile, logout
├─ Router guard → Redirect to / if not authenticated
└─ Dashboard → Main dashboard UI
    ├─ Header → User info, logout button
    ├─ Navigation → 7 tabs
    └─ Content → Tab-specific panels
```

**Authentication Guard:**
```tsx
useEffect(() => {
  if (mounted && !isAuthenticated) {
    router.push('/');  // Redirect to login
  }
}, [isAuthenticated, mounted]);
```

**Loading State:**
```tsx
if (!mounted || !isAuthenticated) {
  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="loading"></div>
    </div>
  );
}
```

### Feature Components

#### 3. **LoginForm Component**

**Location:** `components/LoginForm.tsx`  
**Purpose:** User authentication with validation  
**State:** Local form state + global auth store

**Component Structure:**
```tsx
LoginForm (Client Component)
├─ useState() → username, password, errors
├─ useAuthStore() → login(), isLoading, error
├─ Validation → sanitizeInput, validateUsername, validatePassword
└─ Form submission → API call via store
```

**Validation Pipeline:**
```tsx
const sanitizedUsername = sanitizeInput(username.trim());
const usernameError = validateUsername(sanitizedUsername);
const passwordError = validatePassword(password);

if (usernameError || passwordError) {
  setErrors({ username: usernameError, password: passwordError });
  return;
}

await login(sanitizedUsername, password);
```

**Security Measures:**
- Input sanitization (remove `<>` characters)
- Username: 3-50 chars, alphanumeric + `_-`
- Password: 6-128 chars
- XSS prevention via sanitization
- CSRF protection (future: CSRF tokens)

#### 4. **Dashboard Component**

**Location:** `components/Dashboard.tsx`  
**Purpose:** Main application interface  
**State:** Tab selection (local state)

**Tab System:**
```tsx
type TabType = 'overview' | 'persona' | 'image-gen' | 'data-analysis' 
             | 'learning' | 'security' | 'emergency';

const [activeTab, setActiveTab] = useState<TabType>('overview');
```

**Tab Components:**
```
Dashboard
├─ OverviewTab → System info, feature cards
├─ PersonaTab → AI personality configuration
├─ ImageGenerationTab → Image gen interface
├─ DataAnalysisTab → CSV/XLSX analysis
├─ LearningTab → Learning requests
├─ SecurityTab → Security resources
└─ EmergencyTab → Emergency alerts
```

**Styling Pattern:**
```tsx
<button
  className={`
    flex items-center gap-2 px-4 py-2 rounded-lg transition-all
    ${activeTab === tab.id
      ? 'bg-gradient-to-r from-purple-600 to-blue-500 text-white'
      : 'bg-gray-800/50 text-gray-300 hover:bg-gray-800'
    }
  `}
>
  <span>{tab.icon}</span>
  <span>{tab.label}</span>
</button>
```

#### 5. **StatusIndicator Component**

**Location:** `components/StatusIndicator.tsx`  
**Purpose:** Backend health check display  
**Pattern:** Periodic polling (missing store implementation)

**Expected Behavior:**
```tsx
// Expected (not implemented yet)
const { status, checkHealth } = useHealthStore();

useEffect(() => {
  const interval = setInterval(checkHealth, 30000);  // Poll every 30s
  return () => clearInterval(interval);
}, []);

return (
  <div className={`badge ${status === 'ok' ? 'badge-success' : 'badge-error'}`}>
    Backend: {status}
  </div>
);
```

## State Management Architecture

### Custom Store Pattern (Not Implemented)

**Expected Location:** `web/lib/store.ts` (MISSING)  
**Framework:** Likely Zustand (mentioned in docs)  
**Pattern:** Global state with React hooks

**Expected Store Structure:**
```typescript
// Expected implementation (not found in codebase)
import { create } from 'zustand';

interface User {
  username: string;
  role: 'admin' | 'user' | 'guest';
}

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: ApiError | null;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,
  
  login: async (username, password) => {
    set({ isLoading: true, error: null });
    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      });
      
      if (!response.ok) throw new Error('Login failed');
      
      const data = await response.json();
      set({
        user: data.user,
        token: data.token,
        isAuthenticated: true,
        isLoading: false,
      });
      
      // Store token for persistence
      localStorage.setItem('token', data.token);
    } catch (error) {
      set({ error, isLoading: false });
    }
  },
  
  logout: () => {
    localStorage.removeItem('token');
    set({ user: null, token: null, isAuthenticated: false });
  },
}));
```

### State Flow Diagram

```
User Action (Login Button Click)
  → LoginForm.handleSubmit()
    → useAuthStore.login(username, password)
      → API Call: POST /api/auth/login
        ← Response: {token, user}
      → Store Update: {user, token, isAuthenticated: true}
        → Component Re-render (useAuthStore subscribers)
          → DashboardPage detects isAuthenticated
            → Router.push('/dashboard')
```

## API Integration

### API Client Pattern (Not Implemented)

**Expected Location:** `web/lib/api-client.ts` (MISSING)  
**Purpose:** Centralized API calls with auth headers

**Expected Implementation:**
```typescript
// Expected (not found in codebase)
export class ApiError extends Error {
  constructor(public status: number, public message: string) {
    super(message);
  }
}

export class ApiClient {
  private baseUrl = 'http://localhost:5000/api';
  
  async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const token = localStorage.getItem('token');
    
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(token && { Authorization: `Bearer ${token}` }),
        ...options.headers,
      },
    });
    
    if (!response.ok) {
      throw new ApiError(response.status, await response.text());
    }
    
    return response.json();
  }
  
  async login(username: string, password: string) {
    return this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    });
  }
  
  async aiChat(prompt: string, model?: string) {
    return this.request('/ai/chat', {
      method: 'POST',
      body: JSON.stringify({ prompt, model }),
    });
  }
  
  async aiImage(prompt: string, size?: string) {
    return this.request('/ai/image', {
      method: 'POST',
      body: JSON.stringify({ prompt, size }),
    });
  }
}

export const apiClient = new ApiClient();
```

## Validation Utilities

### Input Validators (`utils/validators.ts`)

**Three Validation Functions:**

#### 1. `validateUsername(username: string): string | null`

**Rules:**
- Required (non-empty after trim)
- Min length: 3 characters
- Max length: 50 characters
- Pattern: `^[a-zA-Z0-9_-]+$` (alphanumeric + underscore + hyphen)

**Returns:** Error message or `null` (valid)

#### 2. `validatePassword(password: string): string | null`

**Rules:**
- Required (non-empty)
- Min length: 6 characters
- Max length: 128 characters

**Returns:** Error message or `null` (valid)

**Security Note:** Client-side validation only. Server enforces Argon2 hashing.

#### 3. `sanitizeInput(input: string): string`

**Purpose:** XSS prevention  
**Implementation:** `input.replace(/[<>]/g, '')`  
**Removes:** `<` and `>` characters (HTML injection prevention)

**Usage Pattern:**
```tsx
const sanitized = sanitizeInput(username.trim());
const error = validateUsername(sanitized);
if (error) {
  setErrors({ username: error });
  return;
}
await login(sanitized, password);
```

## Styling Architecture

### Tailwind CSS Configuration

**Global Styles:** `styles/globals.css`  
**Utility Classes:** Tailwind CSS 3.x  
**Custom Components:** Card, button, badge, input

**Component Class Patterns:**
```css
/* Card component */
.card {
  @apply bg-gray-900/50 border border-gray-800 rounded-lg p-6 backdrop-blur-sm;
}

/* Button variants */
.button {
  @apply px-4 py-2 rounded-lg font-medium transition-all;
}

.button-primary {
  @apply bg-gradient-to-r from-purple-600 to-blue-500 text-white hover:opacity-90;
}

.button-secondary {
  @apply bg-gray-800 text-gray-300 hover:bg-gray-700;
}

/* Badge variants */
.badge {
  @apply inline-block px-2 py-1 rounded text-xs font-semibold;
}

.badge-success {
  @apply bg-green-500/20 text-green-400 border border-green-500/50;
}

.badge-info {
  @apply bg-blue-500/20 text-blue-400 border border-blue-500/50;
}
```

### Responsive Design

**Breakpoints:**
- `sm`: 640px (mobile)
- `md`: 768px (tablet)
- `lg`: 1024px (desktop)
- `xl`: 1280px (large desktop)

**Grid Patterns:**
```tsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
  {/* 1 column mobile, 2 tablet, 3 desktop */}
</div>
```

## Routing Architecture

### Next.js App Router

**Pattern:** File-system based routing  
**Dynamic Routes:** Not used (static routes only)  
**Middleware:** None (auth handled in components)

**Route Map:**
```
/ (app/page.tsx)
  → Login page
  → Redirects to /dashboard if authenticated

/dashboard (app/dashboard/page.tsx)
  → Protected route
  → Redirects to / if not authenticated
  → Main application interface

/error (app/error.tsx)
  → Error boundary
  → Fallback UI for unhandled errors

/loading (app/loading.tsx)
  → Loading UI
  → Shown during navigation
```

### Client-Side Navigation

**Pattern:** `next/navigation` hooks

```tsx
import { useRouter } from 'next/navigation';

const router = useRouter();

// Programmatic navigation
router.push('/dashboard');
router.replace('/');  // No history entry
router.back();        // Browser back
```

**Link Component:**
```tsx
import Link from 'next/link';

<Link href="/dashboard" className="button button-primary">
  Go to Dashboard
</Link>
```

## Performance Optimizations

### Code Splitting

**Automatic:** Next.js splits code by route  
**Manual:** Dynamic imports for heavy components

```tsx
// Lazy load Excalidraw (diagram editor)
const ExcalidrawComponent = dynamic(
  () => import('@/components/ExcalidrawComponent'),
  { ssr: false }  // Disable server-side rendering
);
```

### Image Optimization

**Next.js Image Component:**
```tsx
import Image from 'next/image';

<Image
  src="/logo.png"
  alt="Project-AI"
  width={200}
  height={200}
  priority  // Load immediately (above fold)
/>
```

### Font Optimization

**Next.js Font Loader:**
```tsx
import { Inter } from 'next/font/google';

const inter = Inter({ subsets: ['latin'] });

export default function RootLayout({ children }) {
  return (
    <html lang="en" className={inter.className}>
      {children}
    </html>
  );
}
```

## TypeScript Integration

### Type Safety

**User Type:**
```typescript
export interface User {
  username: string;
  role: 'admin' | 'user' | 'guest';
}
```

**Component Props:**
```typescript
interface DashboardProps {
  user: User;
  onLogout: () => void;
}

export default function Dashboard({ user, onLogout }: DashboardProps) {
  // ...
}
```

**API Response Types:**
```typescript
interface LoginResponse {
  status: 'ok';
  success: true;
  token: string;
  user: User;
}

interface ErrorResponse {
  status: 'error';
  success: false;
  error: string;
  message: string;
}
```

### Path Aliases

**Configuration (`tsconfig.json`):**
```json
{
  "compilerOptions": {
    "paths": {
      "@/*": ["./*"],
      "@/components/*": ["./components/*"],
      "@/lib/*": ["./lib/*"],
      "@/utils/*": ["./utils/*"]
    }
  }
}
```

**Usage:**
```tsx
import { useAuthStore } from '@/lib/store';
import LoginForm from '@/components/LoginForm';
import { validateUsername } from '@/utils/validators';
```

## Security Considerations

### XSS Prevention

**Input Sanitization:**
```tsx
const sanitized = sanitizeInput(username.trim());
// Removes < and > characters
```

**React Auto-Escaping:**
```tsx
<p>{user.username}</p>  // Automatically escaped
```

### CSRF Protection

**Current:** None (API uses JWT only)  
**Future:** CSRF tokens for state-changing requests

```tsx
// Future implementation
const csrfToken = await fetch('/api/csrf-token').then(r => r.json());

await fetch('/api/persona/update', {
  method: 'POST',
  headers: {
    'X-CSRF-Token': csrfToken,
  },
  body: JSON.stringify({ trait, value }),
});
```

### Authentication Token Storage

**Current:** localStorage (vulnerable to XSS)  
**Future:** httpOnly cookies (more secure)

```tsx
// Current (less secure)
localStorage.setItem('token', data.token);

// Future (more secure)
// Server sets httpOnly cookie
// Client cannot access token via JavaScript
```

## Error Handling

### Error Boundary (`app/error.tsx`)

```tsx
'use client';

export default function Error({
  error,
  reset,
}: {
  error: Error;
  reset: () => void;
}) {
  return (
    <div className="card">
      <h2>Something went wrong!</h2>
      <p>{error.message}</p>
      <button onClick={reset} className="button button-primary">
        Try again
      </button>
    </div>
  );
}
```

### Component-Level Error Handling

```tsx
try {
  await login(username, password);
} catch (error) {
  const apiErr = error as ApiError;
  setErrors({ general: apiErr.message });
}
```

## Development Workflow

### Local Development

```bash
# Start Next.js dev server
cd web
npm run dev
# Runs on http://localhost:3000

# Start Flask backend (separate terminal)
python web/backend/app.py
# Runs on http://localhost:5000
```

### Environment Variables

**File:** `web/.env.local` (not committed)

```env
NEXT_PUBLIC_API_URL=http://localhost:5000
```

**Usage:**
```tsx
const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';
```

### Build Process

```bash
# Production build
npm run build

# Start production server
npm start
```

## Testing Strategy

### Unit Tests

**Framework:** Jest + React Testing Library  
**Config:** `jest.config.js`, `jest.setup.js`

**Example Test:**
```tsx
import { render, screen, fireEvent } from '@testing-library/react';
import LoginForm from '@/components/LoginForm';

test('validates username', async () => {
  render(<LoginForm />);
  
  const input = screen.getByLabelText('Username');
  fireEvent.change(input, { target: { value: 'ab' } });  // Too short
  fireEvent.submit(screen.getByRole('button'));
  
  expect(await screen.findByText(/at least 3 characters/)).toBeInTheDocument();
});
```

### Integration Tests

**Pattern:** Test user flows end-to-end

```tsx
test('login flow', async () => {
  render(<HomePage />);
  
  // Fill form
  fireEvent.change(screen.getByLabelText('Username'), {
    target: { value: 'admin' },
  });
  fireEvent.change(screen.getByLabelText('Password'), {
    target: { value: 'open-sesame' },
  });
  
  // Submit
  fireEvent.click(screen.getByText('Login'));
  
  // Verify redirect
  await waitFor(() => {
    expect(window.location.pathname).toBe('/dashboard');
  });
});
```

## Deployment

### Production Build

```bash
npm run build
# Generates .next/ directory with optimized assets
```

### Deployment Targets

**Vercel (Recommended):**
```bash
vercel --prod
```

**Docker:**
```dockerfile
FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
CMD ["npm", "start"]
```

**Static Export (Limited):**
```bash
npm run build && npm run export
# Generates out/ directory with static HTML
# Note: Does not support dynamic routes or API routes
```

## Related Systems

- **Flask API:** `web/backend/app.py`
- **Runtime Router:** `src/app/core/runtime/router.py`
- **Governance Pipeline:** `src/app/core/governance/pipeline.py`
- **Desktop UI:** `src/app/gui/` (PyQt6, separate codebase)

## Missing Implementations

**Critical:**
1. **State Management Store** (`web/lib/store.ts`) - Auth store not found
2. **API Client** (`web/lib/api-client.ts`) - Centralized API calls missing
3. **Health Check Store** - StatusIndicator has no polling logic

**Nice-to-Have:**
4. **CSRF Protection** - Not implemented
5. **httpOnly Cookies** - Using localStorage (less secure)
6. **Offline Support** - No service worker
7. **Error Monitoring** - No Sentry/logging integration

---

**Document Version:** 1.0  
**Last Updated:** 2026-01-XX  
**Maintainer:** Project-AI Team

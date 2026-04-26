# Component Hierarchy & Relationships

**System:** React Component Architecture  
**Framework:** Next.js 14 (App Router)  
**Pattern:** Composition with functional components  

## Component Tree

```
App (Root Layout)
├─ HomePage (/)
│  ├─ StatusIndicator
│  └─ LoginForm
│     └─ useAuthStore (state)
│
└─ DashboardPage (/dashboard)
   └─ Dashboard
      ├─ Header (User info, logout)
      ├─ NavigationTabs (7 tabs)
      └─ Content Panels
         ├─ OverviewTab
         ├─ PersonaTab
         ├─ ImageGenerationTab
         ├─ DataAnalysisTab
         ├─ LearningTab
         ├─ SecurityTab
         └─ EmergencyTab
```

## Root Layer

### RootLayout (`app/layout.tsx`)

**Purpose:** Global layout wrapper  
**Children:** All pages  

```typescript
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={inter.className}>
      <head>
        <title>Project-AI</title>
        <meta name="description" content="Production-Grade AI Assistant" />
      </head>
      <body>
        {children}
      </body>
    </html>
  );
}
```

**Responsibilities:**
- Font loading (Inter from Google Fonts)
- HTML lang attribute
- Global metadata
- CSS variable injection

**CSS Variables:**
```css
:root {
  --primary: #00ffff;    /* Tron cyan */
  --secondary: #00ff00;  /* Tron green */
  --background: #0a0a0a; /* Dark background */
  --foreground: #ffffff; /* White text */
}
```

## Page Layer

### HomePage (`app/page.tsx`)

**Route:** `/`  
**Purpose:** Login page  
**State:** Authentication  

**Component Structure:**
```typescript
export default function HomePage() {
  const router = useRouter();
  const { isAuthenticated, isLoading } = useAuthStore();
  const [mounted, setMounted] = useState(false);

  // Hydration safety
  useEffect(() => {
    setMounted(true);
  }, []);

  // Auto-redirect if authenticated
  useEffect(() => {
    if (mounted && isAuthenticated && !isLoading) {
      router.push('/dashboard');
    }
  }, [isAuthenticated, isLoading, mounted, router]);

  if (!mounted) return null;

  return (
    <main className="min-h-screen flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="card">
          <h1 className="text-4xl font-bold mb-2">Project-AI</h1>
          <p className="text-gray-400">Production-Grade AI Assistant</p>
          
          <StatusIndicator />
          <LoginForm />
          
          <div className="mt-6 text-center text-sm text-gray-500">
            <p>Demo credentials:</p>
            <p>admin / open-sesame</p>
            <p>guest / letmein</p>
          </div>
        </div>
      </div>
    </main>
  );
}
```

**Parent → Child Data Flow:**
- No props (uses global state)
- Child components access `useAuthStore` directly

### DashboardPage (`app/dashboard/page.tsx`)

**Route:** `/dashboard`  
**Purpose:** Protected main interface  
**Guard:** Redirects to `/` if not authenticated  

**Component Structure:**
```typescript
export default function DashboardPage() {
  const router = useRouter();
  const { isAuthenticated, user, logout } = useAuthStore();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  // Auth guard
  useEffect(() => {
    if (mounted && !isAuthenticated) {
      router.push('/');
    }
  }, [isAuthenticated, mounted, router]);

  if (!mounted || !isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="loading"></div>
      </div>
    );
  }

  return (
    <main className="min-h-screen">
      <Dashboard
        user={user || { username: 'Unknown', role: 'guest' }}
        onLogout={() => {
          logout();
          router.push('/');
        }}
      />
    </main>
  );
}
```

**Parent → Child Data Flow:**
```
DashboardPage (state: user, logout)
  ↓ props
Dashboard (props: user, onLogout)
```

## Feature Components

### LoginForm (`components/LoginForm.tsx`)

**Purpose:** User authentication UI  
**State:** Local form state + global auth state  
**Parent:** HomePage  

**Props:** None (uses global state)

**Internal State:**
```typescript
const [username, setUsername] = useState('');
const [password, setPassword] = useState('');
const [errors, setErrors] = useState<{
  username?: string;
  password?: string;
  general?: string;
}>({});
```

**External State:**
```typescript
const { login, isLoading, error: apiError } = useAuthStore();
```

**Event Handlers:**
```typescript
const handleSubmit = async (e: FormEvent) => {
  e.preventDefault();
  setErrors({});

  // Validate
  const sanitizedUsername = sanitizeInput(username.trim());
  const usernameError = validateUsername(sanitizedUsername);
  const passwordError = validatePassword(password);

  if (usernameError || passwordError) {
    setErrors({ username: usernameError, password: passwordError });
    return;
  }

  // Submit
  try {
    await login(sanitizedUsername, password);
  } catch (error) {
    setErrors({ general: (error as ApiError).message });
  }
};
```

**Child Components:** None (leaf component)

### Dashboard (`components/Dashboard.tsx`)

**Purpose:** Main application interface  
**Props:** `{ user: User, onLogout: () => void }`  
**Parent:** DashboardPage  

**Internal State:**
```typescript
type TabType = 'overview' | 'persona' | 'image-gen' | 'data-analysis' 
             | 'learning' | 'security' | 'emergency';

const [activeTab, setActiveTab] = useState<TabType>('overview');
```

**Component Structure:**
```typescript
export default function Dashboard({ user, onLogout }: DashboardProps) {
  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="bg-gray-900/50 border-b border-gray-800">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1>Project-AI Dashboard</h1>
              <p>Welcome, {user.username} ({user.role})</p>
            </div>
            <button onClick={onLogout}>Logout</button>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <nav className="bg-gray-900/30 border-b border-gray-800">
        <div className="flex gap-2 overflow-x-auto py-2">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={activeTab === tab.id ? 'active' : ''}
            >
              {tab.icon} {tab.label}
            </button>
          ))}
        </div>
      </nav>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {activeTab === 'overview' && <OverviewTab user={user} />}
        {activeTab === 'persona' && <PersonaTab />}
        {activeTab === 'image-gen' && <ImageGenerationTab />}
        {activeTab === 'data-analysis' && <DataAnalysisTab />}
        {activeTab === 'learning' && <LearningTab />}
        {activeTab === 'security' && <SecurityTab />}
        {activeTab === 'emergency' && <EmergencyTab />}
      </main>
    </div>
  );
}
```

**Child Components:**
- `OverviewTab` (props: `{ user: User }`)
- `PersonaTab` (props: none)
- `ImageGenerationTab` (props: none)
- `DataAnalysisTab` (props: none)
- `LearningTab` (props: none)
- `SecurityTab` (props: none)
- `EmergencyTab` (props: none)

### StatusIndicator (`components/StatusIndicator.tsx`)

**Purpose:** Backend health check display  
**State:** None (should poll API)  
**Parent:** HomePage  

**Expected Implementation:**
```typescript
export default function StatusIndicator() {
  const [status, setStatus] = useState<'ok' | 'error' | 'loading'>('loading');

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const response = await fetch('http://localhost:5000/api/status');
        const data = await response.json();
        setStatus(data.status === 'ok' ? 'ok' : 'error');
      } catch {
        setStatus('error');
      }
    };

    checkHealth();
    const interval = setInterval(checkHealth, 30000);  // Poll every 30s
    return () => clearInterval(interval);
  }, []);

  return (
    <div className={`badge ${status === 'ok' ? 'badge-success' : 'badge-error'}`}>
      Backend: {status}
    </div>
  );
}
```

## Tab Components (Dashboard Children)

### OverviewTab

**Purpose:** System overview, feature cards  
**Props:** `{ user: User }`  
**State:** None (static content)  

```typescript
function OverviewTab({ user }: { user: User }) {
  const features = [
    { title: 'Four Laws Ethics Engine', icon: '⚖️', status: 'Active' },
    { title: 'AI Persona System', icon: '🧠', status: 'Active' },
    // ... 6 total features
  ];

  return (
    <div className="space-y-6">
      <div className="card">
        <h2>Welcome to Project-AI</h2>
        <p>Sophisticated AI assistant with ethical decision-making</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {features.map((feature) => (
          <div key={feature.title} className="card">
            <div className="text-4xl">{feature.icon}</div>
            <h3>{feature.title}</h3>
            <p>{feature.description}</p>
            <div className="badge">{feature.status}</div>
          </div>
        ))}
      </div>

      <div className="card">
        <h3>System Information</h3>
        <p>User: {user.username}</p>
        <p>Role: {user.role}</p>
      </div>
    </div>
  );
}
```

### PersonaTab, ImageGenerationTab, etc.

**Purpose:** Feature-specific UI  
**Props:** None  
**State:** Expected to use feature-specific stores  

```typescript
function ImageGenerationTab() {
  const [prompt, setPrompt] = useState('');
  const { generateImage, isGenerating } = useAIStore();  // Expected store

  const handleGenerate = async () => {
    const imageUrl = await generateImage(prompt, 'cyberpunk');
    // Display image
  };

  return (
    <div className="card">
      <h2>Image Generation</h2>
      <input
        type="text"
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        placeholder="Describe the image..."
      />
      <button onClick={handleGenerate} disabled={isGenerating}>
        {isGenerating ? 'Generating...' : 'Generate'}
      </button>
    </div>
  );
}
```

## Data Flow Patterns

### Unidirectional Data Flow

```
User Action
  ↓
Event Handler
  ↓
Store Action (useAuthStore.login)
  ↓
API Call (fetch)
  ↓
Store Update (set state)
  ↓
Component Re-render (subscribers)
  ↓
UI Update
```

### Props vs. Global State

**Props (Parent → Child):**
- `Dashboard`: `user`, `onLogout`
- `OverviewTab`: `user`

**Global State (Store):**
- `LoginForm`: `login`, `isLoading`, `error`
- `HomePage`: `isAuthenticated`, `isLoading`
- `DashboardPage`: `isAuthenticated`, `user`, `logout`

### Event Bubbling

```
Button Click (LoginForm)
  ↓
handleSubmit (LoginForm)
  ↓
login(username, password) (useAuthStore)
  ↓
API Call → State Update
  ↓
isAuthenticated changes (global)
  ↓
HomePage detects change
  ↓
router.push('/dashboard')
  ↓
DashboardPage mounts
```

## Component Patterns

### Client Components

**All interactive components marked with `'use client'`:**
```typescript
'use client';

import { useState } from 'react';
import { useAuthStore } from '@/lib/store';

export default function LoginForm() {
  // Component code
}
```

**Why:** Next.js 14 App Router requires explicit client component marking for:
- `useState`, `useEffect` hooks
- Event handlers
- Browser APIs
- Third-party libraries with client-side code

### Loading States

**Pattern:**
```typescript
if (!mounted || !isAuthenticated) {
  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="loading"></div>
    </div>
  );
}
```

### Error Boundaries

**Global Error Boundary:** `app/error.tsx`

```typescript
'use client';

export default function Error({ error, reset }: {
  error: Error;
  reset: () => void;
}) {
  return (
    <div className="card">
      <h2>Something went wrong!</h2>
      <p>{error.message}</p>
      <button onClick={reset}>Try again</button>
    </div>
  );
}
```

### Hydration Safety

**Pattern:**
```typescript
const [mounted, setMounted] = useState(false);

useEffect(() => {
  setMounted(true);
}, []);

if (!mounted) return null;
```

**Why:** Prevents hydration mismatch between server and client rendering

## Styling Patterns

### Tailwind Utility Classes

```typescript
<div className="min-h-screen flex items-center justify-center p-4">
  <div className="w-full max-w-md">
    <div className="card">
      <h1 className="text-4xl font-bold mb-2">Project-AI</h1>
    </div>
  </div>
</div>
```

### Custom Components (CSS)

```css
.card {
  @apply bg-gray-900/50 border border-gray-800 rounded-lg p-6 backdrop-blur-sm;
}

.button {
  @apply px-4 py-2 rounded-lg font-medium transition-all;
}

.button-primary {
  @apply bg-gradient-to-r from-purple-600 to-blue-500 text-white;
}
```

### Conditional Styling

```typescript
<button
  className={`
    px-4 py-2 rounded-lg transition-all
    ${activeTab === tab.id
      ? 'bg-gradient-to-r from-purple-600 to-blue-500 text-white'
      : 'bg-gray-800/50 text-gray-300 hover:bg-gray-800'
    }
  `}
>
  {tab.label}
</button>
```

## Component Communication

### Parent → Child (Props)

```typescript
<Dashboard
  user={user}
  onLogout={() => logout()}
/>
```

### Child → Parent (Callbacks)

```typescript
// Parent
function DashboardPage() {
  const handleLogout = () => {
    logout();
    router.push('/');
  };

  return <Dashboard onLogout={handleLogout} />;
}

// Child
function Dashboard({ onLogout }: { onLogout: () => void }) {
  return <button onClick={onLogout}>Logout</button>;
}
```

### Sibling Communication (Global State)

```typescript
// Component A
function LoginForm() {
  const { login } = useAuthStore();
  await login(username, password);  // Updates global state
}

// Component B
function DashboardPage() {
  const { isAuthenticated } = useAuthStore();  // Reads global state
  
  if (!isAuthenticated) {
    router.push('/');
  }
}
```

## Testing Strategy

### Component Unit Tests

```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import LoginForm from '@/components/LoginForm';

test('renders login form', () => {
  render(<LoginForm />);
  
  expect(screen.getByLabelText('Username')).toBeInTheDocument();
  expect(screen.getByLabelText('Password')).toBeInTheDocument();
  expect(screen.getByRole('button', { name: /login/i })).toBeInTheDocument();
});

test('validates input', async () => {
  render(<LoginForm />);
  
  const usernameInput = screen.getByLabelText('Username');
  fireEvent.change(usernameInput, { target: { value: 'ab' } });  // Too short
  
  const submitButton = screen.getByRole('button', { name: /login/i });
  fireEvent.click(submitButton);
  
  expect(await screen.findByText(/at least 3 characters/)).toBeInTheDocument();
});
```

### Integration Tests

```typescript
test('login flow redirects to dashboard', async () => {
  const { getByLabelText, getByText } = render(<HomePage />);
  
  // Fill form
  fireEvent.change(getByLabelText('Username'), { target: { value: 'admin' } });
  fireEvent.change(getByLabelText('Password'), { target: { value: 'open-sesame' } });
  
  // Submit
  fireEvent.click(getByText('Login'));
  
  // Verify redirect
  await waitFor(() => {
    expect(window.location.pathname).toBe('/dashboard');
  });
});
```

## Related Systems

- **Next.js App Router:** `web/app/`
- **State Management:** `web/lib/store.ts` (expected)
- **API Client:** `web/lib/api-client.ts` (expected)
- **Flask Backend:** `web/backend/app.py`
- **Validation Utils:** `web/utils/validators.ts`

---

**Document Version:** 1.0  
**Last Updated:** 2026-01-XX  
**Maintainer:** Project-AI Team

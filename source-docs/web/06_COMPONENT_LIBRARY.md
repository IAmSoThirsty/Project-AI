---
type: component-library
module: web.components
tags: [react, components, ui, typescript, styling]
created: 2026-04-20
status: production
related_systems: [nextjs-frontend, design-system, zustand]
stakeholders: [frontend-team, ux-team]
platform: web
dependencies: [react@18, next@15, typescript@5]
---

# Component Library Reference

**Purpose:** Comprehensive reference for all React components in Project-AI web application  
**Architecture:** Functional components with hooks, TypeScript strict mode  
**Styling:** CSS Modules + Global CSS variables

---

## Table of Contents

1. [Component Architecture](#component-architecture)
2. [Core Components](#core-components)
3. [Layout Components](#layout-components)
4. [Form Components](#form-components)
5. [Dashboard Components](#dashboard-components)
6. [Utility Components](#utility-components)
7. [Component Patterns](#component-patterns)
8. [Styling Guidelines](#styling-guidelines)

---

## Component Architecture

### File Organization

```
components/
├── LoginForm.tsx           # Authentication form
├── StatusIndicator.tsx     # Backend health indicator
├── Dashboard.tsx           # Main dashboard with 7 tabs
└── ExcalidrawComponent.tsx # Excalidraw integration (optional)
```

### Component Pattern

All components follow this pattern:

```typescript
/**
 * Component description
 * 
 * @param props - Component props
 */

'use client';  // For client components only

import { useState, useEffect } from 'react';
import { PropsType } from '@/types';

interface ComponentProps {
  // Prop types
}

export default function ComponentName({ props }: ComponentProps) {
  // Hooks
  const [state, setState] = useState();
  
  // Effects
  useEffect(() => {
    // Side effects
  }, []);
  
  // Event handlers
  const handleEvent = () => {
    // Handler logic
  };
  
  // Render
  return (
    <div className="component">
      {/* JSX */}
    </div>
  );
}
```

---

## Core Components

### LoginForm

**File:** `components/LoginForm.tsx`  
**Purpose:** User authentication with validation and error handling

**Props:** None (uses Zustand store)

**Features:**
- Real-time input validation
- Password visibility toggle
- Loading state
- Error display with auto-dismissal
- Sanitized inputs
- Responsive design

**State:**
```typescript
const [username, setUsername] = useState('');
const [password, setPassword] = useState('');
const [errors, setErrors] = useState<{
  username?: string;
  password?: string;
  general?: string;
}>({});
```

**Validation:**
```typescript
import { validateUsername, validatePassword, sanitizeInput } from '@/utils/validators';

const handleSubmit = async (e: FormEvent) => {
  e.preventDefault();
  setErrors({});

  // Sanitize and validate
  const sanitizedUsername = sanitizeInput(username.trim());
  const usernameError = validateUsername(sanitizedUsername);
  const passwordError = validatePassword(password);

  if (usernameError || passwordError) {
    setErrors({
      username: usernameError || undefined,
      password: passwordError || undefined,
    });
    return;
  }

  // Submit
  try {
    await login(sanitizedUsername, password);
  } catch (error) {
    setErrors({ general: error.message });
  }
};
```

**Usage:**
```tsx
import LoginForm from '@/components/LoginForm';

export default function LoginPage() {
  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="card w-full max-w-md">
        <h1 className="text-2xl font-bold mb-6">Login</h1>
        <LoginForm />
      </div>
    </div>
  );
}
```

**Styling:**
- Uses global `input` and `button` classes
- Error messages in red (`error-message` class)
- Loading spinner during submission
- Disabled state while loading

---

### StatusIndicator

**File:** `components/StatusIndicator.tsx`  
**Purpose:** Real-time backend health monitoring

**Props:** None (uses Zustand store)

**Features:**
- Auto-polling every 5 seconds
- Color-coded status indicator
- Animated pulse during checking
- Accessible status text

**States:**
```typescript
type BackendStatus = 'checking' | 'online' | 'offline';
```

**Status Colors:**
- `online`: Green (success)
- `offline`: Red (error)
- `checking`: Cyan (primary) with pulse animation

**API Integration:**
```typescript
import { useAppStore } from '@/lib/store';

export default function StatusIndicator() {
  const { backendStatus, checkBackendStatus } = useAppStore();

  useEffect(() => {
    // Initial check
    checkBackendStatus();

    // Poll every 5 seconds
    const interval = setInterval(checkBackendStatus, 5000);
    return () => clearInterval(interval);
  }, [checkBackendStatus]);

  return (
    <div className="status-indicator">
      <div className="status-dot" style={{ background: getStatusColor() }} />
      {getStatusText()}
    </div>
  );
}
```

**Store Implementation:**
```typescript
// lib/store.ts
interface AppState {
  backendStatus: 'checking' | 'online' | 'offline';
  checkBackendStatus: () => Promise<void>;
}

export const useAppStore = create<AppState>((set) => ({
  backendStatus: 'checking',
  
  checkBackendStatus: async () => {
    try {
      const response = await fetch('/api/status');
      if (response.ok) {
        set({ backendStatus: 'online' });
      } else {
        set({ backendStatus: 'offline' });
      }
    } catch {
      set({ backendStatus: 'offline' });
    }
  },
}));
```

**Usage:**
```tsx
import StatusIndicator from '@/components/StatusIndicator';

export default function LoginPage() {
  return (
    <div>
      <StatusIndicator />
      <LoginForm />
    </div>
  );
}
```

---

### Dashboard

**File:** `components/Dashboard.tsx`  
**Purpose:** Main application interface with 7 feature tabs

**Props:**
```typescript
interface DashboardProps {
  user: User;           // Authenticated user
  onLogout: () => void; // Logout callback
}
```

**User Type:**
```typescript
interface User {
  username: string;
  role: 'superuser' | 'user';
}
```

**Architecture:**
```
Dashboard
├── Header (user info, logout button)
├── TabNavigation (7 tabs)
└── TabContent (dynamic based on activeTab)
    ├── OverviewTab
    ├── PersonaTab
    ├── ImageGenerationTab
    ├── DataAnalysisTab
    ├── LearningTab
    ├── SecurityTab
    └── EmergencyTab
```

**State:**
```typescript
type TabType = 
  | 'overview' 
  | 'persona' 
  | 'image-gen' 
  | 'data-analysis' 
  | 'learning' 
  | 'security' 
  | 'emergency';

const [activeTab, setActiveTab] = useState<TabType>('overview');
```

**Tab Configuration:**
```typescript
const tabs: { id: TabType; label: string; icon: string }[] = [
  { id: 'overview', label: 'Overview', icon: '📊' },
  { id: 'persona', label: 'AI Persona', icon: '🤖' },
  { id: 'image-gen', label: 'Image Generation', icon: '🎨' },
  { id: 'data-analysis', label: 'Data Analysis', icon: '📈' },
  { id: 'learning', label: 'Learning Paths', icon: '📚' },
  { id: 'security', label: 'Security', icon: '🔒' },
  { id: 'emergency', label: 'Emergency', icon: '🚨' },
];
```

**Header Component:**
```tsx
<header className="bg-gray-900/50 border-b border-gray-800 backdrop-blur-sm sticky top-0 z-10">
  <div className="container mx-auto px-4 py-4">
    <div className="flex items-center justify-between">
      <div>
        <h1 className="text-2xl font-bold" style={{ color: 'var(--primary)' }}>
          Project-AI Dashboard
        </h1>
        <p className="text-sm text-gray-400 mt-1">
          Welcome, <span className="font-semibold">{user.username}</span> ({user.role})
        </p>
      </div>
      <button onClick={onLogout} className="button button-secondary">
        Logout
      </button>
    </div>
  </div>
</header>
```

**Tab Navigation:**
```tsx
<nav className="bg-gray-900/30 border-b border-gray-800">
  <div className="container mx-auto px-4">
    <div className="flex gap-2 overflow-x-auto py-2">
      {tabs.map((tab) => (
        <button
          key={tab.id}
          onClick={() => setActiveTab(tab.id)}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg whitespace-nowrap transition-all ${
            activeTab === tab.id
              ? 'bg-gradient-to-r from-purple-600 to-blue-500 text-white font-semibold'
              : 'bg-gray-800/50 text-gray-300 hover:bg-gray-800'
          }`}
        >
          <span>{tab.icon}</span>
          <span>{tab.label}</span>
        </button>
      ))}
    </div>
  </div>
</nav>
```

**Tab Content:**
```tsx
<main className="container mx-auto px-4 py-8">
  {activeTab === 'overview' && <OverviewTab user={user} />}
  {activeTab === 'persona' && <PersonaTab />}
  {activeTab === 'image-gen' && <ImageGenerationTab />}
  {activeTab === 'data-analysis' && <DataAnalysisTab />}
  {activeTab === 'learning' && <LearningTab />}
  {activeTab === 'security' && <SecurityTab />}
  {activeTab === 'emergency' && <EmergencyTab />}
</main>
```

**Usage:**
```tsx
'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/lib/store';
import Dashboard from '@/components/Dashboard';

export default function DashboardPage() {
  const router = useRouter();
  const { isAuthenticated, user, logout } = useAuthStore();

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/');
    }
  }, [isAuthenticated, router]);

  if (!isAuthenticated || !user) {
    return <div>Loading...</div>;
  }

  const handleLogout = () => {
    logout();
    router.push('/');
  };

  return <Dashboard user={user} onLogout={handleLogout} />;
}
```

---

## Dashboard Tab Components

### OverviewTab

**Purpose:** System information and feature status cards

**Props:**
```typescript
interface OverviewTabProps {
  user: User;
}
```

**Features:**
- 6 feature cards (Four Laws, Persona, Memory, Learning, Image Gen, Data Analysis)
- System information grid
- Badge indicators
- Responsive grid layout

**Feature Card Structure:**
```typescript
interface Feature {
  title: string;
  description: string;
  status: 'Active' | 'Available';
  icon: string;
}
```

### PersonaTab

**Purpose:** AI personality configuration

**Features:**
- 8 personality traits (creativity, empathy, humor, etc.)
- Mood tracking display
- State persistence info
- Configuration placeholders

### ImageGenerationTab

**Purpose:** AI image generation interface

**Features:**
- Backend selection (HF Stable Diffusion, OpenAI DALL-E 3)
- Style presets (10 options)
- Content filtering info
- Generation history

### DataAnalysisTab

**Purpose:** Data file analysis

**Features:**
- Supported formats (CSV, XLSX, JSON)
- Analysis features (K-means, statistics)
- Upload interface
- Results display

### LearningTab

**Purpose:** Learning path management

**Features:**
- Request submission
- Black Vault info
- Knowledge base (6 categories)
- Approval workflow

### SecurityTab

**Purpose:** Security tools and resources

**Features:**
- GitHub integration
- CTF challenges
- Security resources
- Vulnerability scanning

### EmergencyTab

**Purpose:** Emergency alert system

**Features:**
- Contact management
- Email notification setup
- Alert triggers
- Emergency protocols

---

## Component Patterns

### Client Component Pattern

**All interactive components must be client components:**

```typescript
'use client';  // Required for useState, useEffect, event handlers

import { useState } from 'react';

export default function InteractiveComponent() {
  const [count, setCount] = useState(0);
  
  return (
    <button onClick={() => setCount(count + 1)}>
      Count: {count}
    </button>
  );
}
```

### Server Component Pattern

**Static components can be server components:**

```typescript
// No 'use client' directive

export default function StaticComponent() {
  return (
    <div>
      <h1>Static Content</h1>
      <p>This component does not use hooks or event handlers.</p>
    </div>
  );
}
```

### Composition Pattern

**Prefer composition over inheritance:**

```tsx
// ❌ Bad (prop drilling)
<Parent data={data}>
  <Child1 data={data} />
  <Child2 data={data} />
</Parent>

// ✅ Good (composition with children)
<Parent>
  <Child1 data={data} />
  <Child2 data={data} />
</Parent>
```

### Conditional Rendering Pattern

```tsx
// ✅ Short-circuit evaluation
{isLoading && <LoadingSpinner />}

// ✅ Ternary operator
{isAuthenticated ? <Dashboard /> : <LoginForm />}

// ✅ Early return
if (!isAuthenticated) {
  return <LoginForm />;
}

return <Dashboard />;
```

### List Rendering Pattern

```tsx
// ✅ Map with unique keys
{features.map((feature, index) => (
  <FeatureCard key={feature.id || index} feature={feature} />
))}

// ❌ Bad (index as key when items can be reordered)
{features.map((feature, index) => (
  <FeatureCard key={index} feature={feature} />
))}
```

---

## Styling Guidelines

### CSS Variable Usage

**Global variables defined in `styles/globals.css`:**

```css
:root {
  /* Colors */
  --primary: #00d4ff;     /* Tron cyan */
  --secondary: #ff00ff;   /* Magenta */
  --accent: #00ff88;      /* Green */
  --error: #ff4444;       /* Red */
  
  /* Backgrounds */
  --bg-dark: #0a0a0f;
  --bg-card: #1a1a2e;
  
  /* Text */
  --text-primary: #ffffff;
  --text-secondary: #a0a0a0;
}
```

**Usage in components:**
```tsx
<div style={{ color: 'var(--primary)' }}>Styled Text</div>
```

### Global CSS Classes

**Card:**
```tsx
<div className="card">
  <h2>Card Title</h2>
  <p>Card content</p>
</div>
```

**Button:**
```tsx
<button className="button button-primary">Primary</button>
<button className="button button-secondary">Secondary</button>
```

**Input:**
```tsx
<input className="input" type="text" placeholder="Enter text" />
```

**Badge:**
```tsx
<span className="badge badge-success">Active</span>
<span className="badge badge-info">Info</span>
<span className="badge badge-error">Error</span>
```

### Responsive Design

**Use Tailwind-style responsive classes:**

```tsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
  {/* Cards */}
</div>
```

**Breakpoints:**
- `sm`: 640px
- `md`: 768px
- `lg`: 1024px
- `xl`: 1280px

---

## Accessibility

### Semantic HTML

```tsx
// ✅ Good (semantic)
<nav>
  <button onClick={handleClick}>Menu</button>
</nav>

// ❌ Bad (non-semantic)
<div onClick={handleClick}>Menu</div>
```

### ARIA Labels

```tsx
<button aria-label="Close modal" onClick={closeModal}>
  ×
</button>
```

### Keyboard Navigation

```tsx
<div
  role="button"
  tabIndex={0}
  onKeyDown={(e) => e.key === 'Enter' && handleClick()}
  onClick={handleClick}
>
  Clickable
</div>
```

### Alt Text for Images

```tsx
<img src="/logo.png" alt="Project-AI Logo" />
```

---

## Performance Optimization

### React.memo

**Memoize expensive components:**

```typescript
import { memo } from 'react';

const ExpensiveComponent = memo(({ data }: { data: Data }) => {
  // Expensive render logic
  return <div>{/* ... */}</div>;
});

export default ExpensiveComponent;
```

### useMemo

**Memoize expensive calculations:**

```typescript
import { useMemo } from 'react';

const filteredData = useMemo(() => {
  return data.filter(item => item.status === 'active');
}, [data]);
```

### useCallback

**Memoize callback functions:**

```typescript
import { useCallback } from 'react';

const handleClick = useCallback(() => {
  // Handler logic
}, [dependency]);
```

---

## Testing Components

### Component Test Example

```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import LoginForm from '@/components/LoginForm';

describe('LoginForm', () => {
  it('renders login form', () => {
    render(<LoginForm />);
    
    expect(screen.getByPlaceholderText('Enter your username')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Enter your password')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /login/i })).toBeInTheDocument();
  });
  
  it('shows validation errors', async () => {
    render(<LoginForm />);
    
    const submitButton = screen.getByRole('button', { name: /login/i });
    fireEvent.click(submitButton);
    
    expect(await screen.findByText('Username is required')).toBeInTheDocument();
  });
  
  it('submits form with valid data', async () => {
    const mockLogin = vi.fn();
    render(<LoginForm />);
    
    fireEvent.change(screen.getByPlaceholderText('Enter your username'), {
      target: { value: 'admin' },
    });
    fireEvent.change(screen.getByPlaceholderText('Enter your password'), {
      target: { value: 'password' },
    });
    
    fireEvent.click(screen.getByRole('button', { name: /login/i }));
    
    expect(mockLogin).toHaveBeenCalledWith('admin', 'password');
  });
});
```

---

## Related Documentation

- [React Frontend](./02_REACT_FRONTEND.md)
- [API Client Integration](./05_API_CLIENT_INTEGRATION.md)
- [Styling Guide](./08_STYLING_GUIDE.md)
- [React Documentation](https://react.dev)
- [Next.js Documentation](https://nextjs.org/docs)

---

**Last Updated:** 2026-04-20  
**Maintainer:** Frontend Team  
**Review Cycle:** Quarterly

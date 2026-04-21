# State Management Relationships

**System:** React State Management (Expected Zustand Implementation)  
**Status:** Partially Implemented (Store Missing)  
**Pattern:** Global state with React hooks  

## Overview

The web frontend uses a **custom store pattern** (likely Zustand) for global state management. While components reference `useAuthStore`, the actual implementation is **missing from the codebase**.

## Expected Architecture

### Store Structure (Missing Implementation)

**Expected Location:** `web/lib/store.ts` (NOT FOUND)

```typescript
// Expected implementation (not in codebase)
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

// ============================================================================
// Types
// ============================================================================

export interface User {
  username: string;
  role: 'admin' | 'user' | 'guest';
}

export interface ApiError {
  message: string;
  code?: string;
}

// ============================================================================
// Auth Store
// ============================================================================

interface AuthState {
  // State
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: ApiError | null;
  
  // Actions
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  checkAuth: () => Promise<void>;
  clearError: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      // Initial state
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,
      
      // Login action
      login: async (username, password) => {
        set({ isLoading: true, error: null });
        
        try {
          const response = await fetch('http://localhost:5000/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password }),
          });
          
          if (!response.ok) {
            const error = await response.json();
            throw new Error(error.message || 'Login failed');
          }
          
          const data = await response.json();
          
          set({
            user: data.user,
            token: data.token,
            isAuthenticated: true,
            isLoading: false,
          });
        } catch (error) {
          set({
            error: { message: (error as Error).message },
            isLoading: false,
          });
          throw error;
        }
      },
      
      // Logout action
      logout: () => {
        set({
          user: null,
          token: null,
          isAuthenticated: false,
          error: null,
        });
      },
      
      // Check auth on mount
      checkAuth: async () => {
        const token = get().token;
        if (!token) return;
        
        // Validate token is still valid
        try {
          const response = await fetch('http://localhost:5000/api/status', {
            headers: { Authorization: `Bearer ${token}` },
          });
          
          if (!response.ok) {
            get().logout();
          }
        } catch {
          get().logout();
        }
      },
      
      // Clear error
      clearError: () => set({ error: null }),
    }),
    {
      name: 'auth-storage',  // localStorage key
      partialize: (state) => ({
        token: state.token,
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);

// ============================================================================
// AI Store
// ============================================================================

interface AIState {
  // State
  chatHistory: Array<{ role: 'user' | 'assistant'; content: string }>;
  isGenerating: boolean;
  currentModel: string;
  
  // Actions
  sendMessage: (prompt: string) => Promise<void>;
  generateImage: (prompt: string, style: string) => Promise<string>;
  clearHistory: () => void;
}

export const useAIStore = create<AIState>()((set, get) => ({
  chatHistory: [],
  isGenerating: false,
  currentModel: 'gpt-4',
  
  sendMessage: async (prompt) => {
    const { token } = useAuthStore.getState();
    
    set({ isGenerating: true });
    
    // Add user message
    set((state) => ({
      chatHistory: [...state.chatHistory, { role: 'user', content: prompt }],
    }));
    
    try {
      const response = await fetch('http://localhost:5000/api/ai/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ prompt, model: get().currentModel }),
      });
      
      const data = await response.json();
      
      // Add assistant message
      set((state) => ({
        chatHistory: [
          ...state.chatHistory,
          { role: 'assistant', content: data.result },
        ],
        isGenerating: false,
      }));
    } catch (error) {
      set({ isGenerating: false });
      throw error;
    }
  },
  
  generateImage: async (prompt, style) => {
    const { token } = useAuthStore.getState();
    
    set({ isGenerating: true });
    
    try {
      const response = await fetch('http://localhost:5000/api/ai/image', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ prompt, style }),
      });
      
      const data = await response.json();
      
      set({ isGenerating: false });
      
      return data.result.image_url;
    } catch (error) {
      set({ isGenerating: false });
      throw error;
    }
  },
  
  clearHistory: () => set({ chatHistory: [] }),
}));

// ============================================================================
// Persona Store
// ============================================================================

interface PersonaState {
  traits: Record<string, number>;
  isUpdating: boolean;
  
  updateTrait: (trait: string, value: number) => Promise<void>;
  loadTraits: () => Promise<void>;
}

export const usePersonaStore = create<PersonaState>()((set) => ({
  traits: {},
  isUpdating: false,
  
  updateTrait: async (trait, value) => {
    const { token } = useAuthStore.getState();
    
    set({ isUpdating: true });
    
    try {
      const response = await fetch('http://localhost:5000/api/persona/update', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ trait, value }),
      });
      
      const data = await response.json();
      
      set((state) => ({
        traits: { ...state.traits, [trait]: value },
        isUpdating: false,
      }));
    } catch (error) {
      set({ isUpdating: false });
      throw error;
    }
  },
  
  loadTraits: async () => {
    const { token } = useAuthStore.getState();
    
    try {
      const response = await fetch('http://localhost:5000/api/persona/query', {
        headers: { Authorization: `Bearer ${token}` },
      });
      
      const data = await response.json();
      
      set({ traits: data.result });
    } catch (error) {
      console.error('Failed to load persona traits:', error);
    }
  },
}));
```

## State Flow Patterns

### Authentication Flow

```typescript
// Component usage
import { useAuthStore } from '@/lib/store';

function LoginForm() {
  const { login, isLoading, error } = useAuthStore();
  
  const handleSubmit = async (username: string, password: string) => {
    try {
      await login(username, password);
      // Store automatically updates isAuthenticated
      router.push('/dashboard');
    } catch (error) {
      // Error state updated automatically
      console.error(error);
    }
  };
  
  return <form onSubmit={handleSubmit}>...</form>;
}
```

**State Transitions:**
```
Initial State:
{ user: null, token: null, isAuthenticated: false, isLoading: false }

After login() called:
{ user: null, token: null, isAuthenticated: false, isLoading: true }

After successful API response:
{ user: {username: "admin", role: "admin"}, token: "eyJ...", isAuthenticated: true, isLoading: false }

After error:
{ user: null, token: null, isAuthenticated: false, isLoading: false, error: {message: "..."} }
```

### Persistence Strategy

**Zustand Persist Middleware:**
```typescript
persist(
  (set, get) => ({ /* state */ }),
  {
    name: 'auth-storage',  // localStorage key
    partialize: (state) => ({
      token: state.token,
      user: state.user,
      isAuthenticated: state.isAuthenticated,
    }),
  }
)
```

**Storage Keys:**
- `auth-storage` - Auth state (user, token, isAuthenticated)
- `ai-chat-history` - Chat history (optional)
- `persona-traits` - Persona configuration (optional)

### Cross-Component State Sharing

```typescript
// Page 1: Login
function LoginPage() {
  const { login } = useAuthStore();
  await login(username, password);
  // State updated globally
}

// Page 2: Dashboard
function DashboardPage() {
  const { user, isAuthenticated } = useAuthStore();
  // Receives updated state automatically
  
  if (!isAuthenticated) {
    router.push('/');
  }
}
```

## Component-Store Relationships

### LoginForm → useAuthStore

**Relationships:**
- Read: `isLoading`, `error`
- Write: `login(username, password)`

```typescript
const { login, isLoading, error } = useAuthStore();
```

### Dashboard → useAuthStore

**Relationships:**
- Read: `user`, `isAuthenticated`
- Write: `logout()`

```typescript
const { user, isAuthenticated, logout } = useAuthStore();
```

### StatusIndicator → useHealthStore (Missing)

**Expected:**
```typescript
interface HealthState {
  status: 'ok' | 'error' | 'unknown';
  lastCheck: Date | null;
  checkHealth: () => Promise<void>;
}

const useHealthStore = create<HealthState>()((set) => ({
  status: 'unknown',
  lastCheck: null,
  
  checkHealth: async () => {
    try {
      const response = await fetch('http://localhost:5000/api/status');
      const data = await response.json();
      
      set({
        status: data.status === 'ok' ? 'ok' : 'error',
        lastCheck: new Date(),
      });
    } catch {
      set({ status: 'error', lastCheck: new Date() });
    }
  },
}));
```

## Selector Patterns

### Basic Selectors

```typescript
// Get single value
const user = useAuthStore((state) => state.user);
const isLoading = useAuthStore((state) => state.isLoading);

// Get multiple values
const { user, token, isAuthenticated } = useAuthStore();
```

### Computed Selectors

```typescript
// Derived state
const isAdmin = useAuthStore((state) => state.user?.role === 'admin');
const hasToken = useAuthStore((state) => !!state.token);
const isGuest = useAuthStore((state) => state.user?.role === 'guest');
```

### Shallow Comparison

```typescript
import { shallow } from 'zustand/shallow';

// Prevent unnecessary re-renders
const { user, isAuthenticated } = useAuthStore(
  (state) => ({ user: state.user, isAuthenticated: state.isAuthenticated }),
  shallow
);
```

## Performance Optimizations

### Subscription Splitting

```typescript
// Bad: Re-renders on any auth state change
const authState = useAuthStore();

// Good: Re-renders only when user changes
const user = useAuthStore((state) => state.user);
```

### Action Separation

```typescript
// Keep actions separate from state
const login = useAuthStore((state) => state.login);
const logout = useAuthStore((state) => state.logout);

// Actions don't cause re-renders when called
```

### Middleware Stacking

```typescript
const useAuthStore = create<AuthState>()(
  persist(
    devtools(
      (set, get) => ({ /* state */ }),
      { name: 'AuthStore' }
    ),
    { name: 'auth-storage' }
  )
);
```

## Testing Strategy

### Store Unit Tests

```typescript
import { renderHook, act } from '@testing-library/react';
import { useAuthStore } from '@/lib/store';

test('login updates state', async () => {
  const { result } = renderHook(() => useAuthStore());
  
  // Mock fetch
  global.fetch = jest.fn(() =>
    Promise.resolve({
      ok: true,
      json: () => Promise.resolve({
        token: 'test-token',
        user: { username: 'test', role: 'user' },
      }),
    })
  );
  
  // Call login
  await act(async () => {
    await result.current.login('test', 'password');
  });
  
  // Verify state
  expect(result.current.isAuthenticated).toBe(true);
  expect(result.current.user?.username).toBe('test');
  expect(result.current.token).toBe('test-token');
});
```

### Component Integration Tests

```typescript
test('LoginForm integrates with useAuthStore', async () => {
  const { getByLabelText, getByText } = render(<LoginForm />);
  
  fireEvent.change(getByLabelText('Username'), { target: { value: 'admin' } });
  fireEvent.change(getByLabelText('Password'), { target: { value: 'password' } });
  fireEvent.click(getByText('Login'));
  
  await waitFor(() => {
    const state = useAuthStore.getState();
    expect(state.isAuthenticated).toBe(true);
  });
});
```

## Related Systems

- **React Frontend:** `web/app/`, `web/components/`
- **Flask API:** `web/backend/app.py`
- **Runtime Router:** `src/app/core/runtime/router.py`
- **LoginForm:** `web/components/LoginForm.tsx`
- **Dashboard:** `web/components/Dashboard.tsx`

## Missing Implementations

**Critical:**
1. **Auth Store** (`web/lib/store.ts`) - Core state management MISSING
2. **API Client** (`web/lib/api-client.ts`) - Centralized API calls MISSING
3. **Health Store** - StatusIndicator has no backend integration
4. **AI Store** - Chat/image generation state management
5. **Persona Store** - Trait management state

**Future Enhancements:**
6. Offline support (Service Worker + IndexedDB)
7. Optimistic updates (immediate UI feedback)
8. Real-time sync (WebSocket integration)
9. State persistence encryption
10. State time-travel debugging (Zustand DevTools)

---

**Document Version:** 1.0  
**Last Updated:** 2026-01-XX  
**Maintainer:** Project-AI Team

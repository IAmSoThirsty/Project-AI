---
type: state-management-guide
module: web.state
tags: [zustand, state-management, react, typescript, hooks]
created: 2026-04-20
status: production
related_systems: [react-frontend, api-client, components]
stakeholders: [frontend-team, architecture-team]
platform: web
dependencies: [zustand@5, react@18]
---

# State Management with Zustand

**Purpose:** Lightweight state management for Project-AI web application  
**Technology:** Zustand 5.0 (React state library)  
**Architecture:** Multiple stores with selectors, no boilerplate, no providers

---

## Table of Contents

1. [Why Zustand](#why-zustand)
2. [Store Architecture](#store-architecture)
3. [Auth Store](#auth-store)
4. [App Store](#app-store)
5. [Custom Hooks](#custom-hooks)
6. [Best Practices](#best-practices)
7. [Testing Stores](#testing-stores)
8. [Migration Guide](#migration-guide)

---

## Why Zustand

### Comparison with Alternatives

| Feature | Zustand | Redux | Context API | Recoil |
|---------|---------|-------|-------------|--------|
| **Bundle Size** | 1.2KB | 16KB | 0KB | 14KB |
| **Boilerplate** | Minimal | High | Low | Medium |
| **DevTools** | ✅ | ✅ | ❌ | ✅ |
| **Async Support** | ✅ | ✅ (thunk) | ⚠️ | ✅ |
| **Performance** | Excellent | Good | Poor | Good |
| **Learning Curve** | Easy | Hard | Easy | Medium |
| **TypeScript** | Excellent | Good | Good | Good |

### Why We Chose Zustand

1. **Minimal boilerplate** - No providers, actions, or reducers
2. **Excellent TypeScript support** - Full type inference
3. **Tiny bundle size** - Only 1.2KB minified + gzipped
4. **No Context Provider** - Works without React Context
5. **Async out of the box** - No middleware needed
6. **Selectors for performance** - Automatic re-render optimization

---

## Store Architecture

### Multiple Store Pattern

**We use separate stores for different concerns:**

```
stores/
├── authStore.ts    # Authentication state
├── appStore.ts     # Application state (backend status, UI state)
└── index.ts        # Barrel export
```

### Store Structure

```typescript
import { create } from 'zustand';

interface StoreState {
  // State
  value: string;
  count: number;
  
  // Actions
  setValue: (value: string) => void;
  increment: () => void;
  reset: () => void;
}

export const useStore = create<StoreState>((set, get) => ({
  // Initial state
  value: '',
  count: 0,
  
  // Actions (sync)
  setValue: (value) => set({ value }),
  increment: () => set((state) => ({ count: state.count + 1 })),
  reset: () => set({ value: '', count: 0 }),
}));
```

---

## Auth Store

**File:** `lib/store.ts` (authStore section)

### State Interface

```typescript
interface User {
  username: string;
  role: 'superuser' | 'user';
}

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
  checkAuth: () => void;
  clearError: () => void;
}
```

### Implementation

```typescript
import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import apiClient from './api-client';
import { TokenStorage, UserStorage } from './storage';
import { handleApiError, ApiError } from './errors';

export const useAuthStore = create<AuthState>()(
  devtools(
    persist(
      (set, get) => ({
        // Initial state
        user: null,
        token: null,
        isAuthenticated: false,
        isLoading: false,
        error: null,
        
        // Login action
        login: async (username: string, password: string) => {
          set({ isLoading: true, error: null });
          
          try {
            const response = await apiClient.post('/api/auth/login', {
              username,
              password,
            });
            
            const { token, user } = response.data;
            
            // Persist to localStorage
            TokenStorage.set(token);
            UserStorage.set(user);
            
            // Update state
            set({
              user,
              token,
              isAuthenticated: true,
              isLoading: false,
              error: null,
            });
          } catch (error) {
            const apiError = handleApiError(error);
            set({
              isLoading: false,
              error: apiError,
            });
            throw apiError;
          }
        },
        
        // Logout action
        logout: () => {
          TokenStorage.remove();
          UserStorage.remove();
          
          set({
            user: null,
            token: null,
            isAuthenticated: false,
            error: null,
          });
        },
        
        // Check auth status (hydration)
        checkAuth: () => {
          const token = TokenStorage.get();
          const user = UserStorage.get();
          
          if (token && user && !TokenStorage.isExpired(token)) {
            set({
              user,
              token,
              isAuthenticated: true,
            });
          } else {
            // Token expired or invalid
            get().logout();
          }
        },
        
        // Clear error
        clearError: () => set({ error: null }),
      }),
      {
        name: 'auth-storage',  // localStorage key
        partialize: (state) => ({
          // Only persist these fields
          user: state.user,
          token: state.token,
          isAuthenticated: state.isAuthenticated,
        }),
      }
    ),
    { name: 'AuthStore' }  // DevTools name
  )
);
```

### Usage in Components

```typescript
// Select specific fields (automatic re-render optimization)
const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
const user = useAuthStore((state) => state.user);
const login = useAuthStore((state) => state.login);

// Select multiple fields
const { user, isAuthenticated, logout } = useAuthStore();

// Use in component
function LoginButton() {
  const login = useAuthStore((state) => state.login);
  const isLoading = useAuthStore((state) => state.isLoading);
  
  const handleLogin = async () => {
    try {
      await login('admin', 'password');
    } catch (error) {
      console.error('Login failed:', error);
    }
  };
  
  return (
    <button onClick={handleLogin} disabled={isLoading}>
      {isLoading ? 'Logging in...' : 'Login'}
    </button>
  );
}
```

---

## App Store

**File:** `lib/store.ts` (appStore section)

### State Interface

```typescript
interface AppState {
  // Backend status
  backendStatus: 'checking' | 'online' | 'offline';
  lastChecked: Date | null;
  
  // UI state
  sidebarOpen: boolean;
  theme: 'dark' | 'light';
  
  // Actions
  checkBackendStatus: () => Promise<void>;
  toggleSidebar: () => void;
  setTheme: (theme: 'dark' | 'light') => void;
}
```

### Implementation

```typescript
export const useAppStore = create<AppState>()(
  devtools(
    (set, get) => ({
      // Initial state
      backendStatus: 'checking',
      lastChecked: null,
      sidebarOpen: true,
      theme: 'dark',
      
      // Check backend status
      checkBackendStatus: async () => {
        set({ backendStatus: 'checking' });
        
        try {
          const response = await apiClient.get('/api/status', {
            timeout: 5000,  // 5 second timeout
          });
          
          if (response.data.status === 'ok') {
            set({
              backendStatus: 'online',
              lastChecked: new Date(),
            });
          } else {
            set({
              backendStatus: 'offline',
              lastChecked: new Date(),
            });
          }
        } catch (error) {
          set({
            backendStatus: 'offline',
            lastChecked: new Date(),
          });
        }
      },
      
      // Toggle sidebar
      toggleSidebar: () => {
        set((state) => ({ sidebarOpen: !state.sidebarOpen }));
      },
      
      // Set theme
      setTheme: (theme) => {
        set({ theme });
        document.documentElement.setAttribute('data-theme', theme);
      },
    }),
    { name: 'AppStore' }
  )
);
```

### Usage with Polling

```typescript
function StatusIndicator() {
  const { backendStatus, checkBackendStatus } = useAppStore();
  
  useEffect(() => {
    // Initial check
    checkBackendStatus();
    
    // Poll every 5 seconds
    const interval = setInterval(checkBackendStatus, 5000);
    
    return () => clearInterval(interval);
  }, [checkBackendStatus]);
  
  return (
    <div className="status">
      {backendStatus === 'online' && '✅ Backend Online'}
      {backendStatus === 'offline' && '❌ Backend Offline'}
      {backendStatus === 'checking' && '🔄 Checking...'}
    </div>
  );
}
```

---

## Custom Hooks

### useAuth Hook

```typescript
/**
 * Custom hook for authentication
 * 
 * Provides easy access to auth state and actions.
 */
export function useAuth() {
  const {
    user,
    isAuthenticated,
    isLoading,
    error,
    login,
    logout,
    clearError,
  } = useAuthStore();
  
  return {
    user,
    isAuthenticated,
    isLoading,
    error,
    login,
    logout,
    clearError,
  };
}

// Usage
function MyComponent() {
  const { user, isAuthenticated, logout } = useAuth();
  
  if (!isAuthenticated) {
    return <LoginForm />;
  }
  
  return <div>Hello, {user.username}!</div>;
}
```

### useBackendStatus Hook

```typescript
/**
 * Custom hook for backend status monitoring
 */
export function useBackendStatus() {
  const { backendStatus, lastChecked, checkBackendStatus } = useAppStore();
  
  // Auto-check on mount
  useEffect(() => {
    checkBackendStatus();
  }, [checkBackendStatus]);
  
  return {
    status: backendStatus,
    lastChecked,
    refresh: checkBackendStatus,
  };
}

// Usage
function MyComponent() {
  const { status, refresh } = useBackendStatus();
  
  return (
    <div>
      Status: {status}
      <button onClick={refresh}>Refresh</button>
    </div>
  );
}
```

### useAuthHydration Hook

```typescript
/**
 * Hook to hydrate auth state from localStorage on mount
 * 
 * Use in root layout to restore auth state across page reloads.
 */
export function useAuthHydration() {
  const checkAuth = useAuthStore((state) => state.checkAuth);
  
  useEffect(() => {
    checkAuth();
  }, [checkAuth]);
}

// Usage in app/layout.tsx
export default function RootLayout({ children }: { children: React.ReactNode }) {
  useAuthHydration();  // Hydrate auth state on mount
  
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
```

---

## Best Practices

### 1. Use Selectors for Performance

**❌ Bad (re-renders on any state change):**
```typescript
const store = useAuthStore();
console.log(store.user);
```

**✅ Good (only re-renders when user changes):**
```typescript
const user = useAuthStore((state) => state.user);
```

### 2. Avoid Derived State

**❌ Bad (storing derived state):**
```typescript
interface State {
  count: number;
  doubleCount: number;  // Derived from count
}
```

**✅ Good (compute on read):**
```typescript
interface State {
  count: number;
}

// In component
const count = useStore((state) => state.count);
const doubleCount = count * 2;
```

### 3. Use Immer for Complex Updates

```typescript
import { immer } from 'zustand/middleware/immer';

export const useStore = create<State>()(
  immer((set) => ({
    nested: { deep: { value: 0 } },
    
    updateNested: (value: number) => {
      set((state) => {
        // Mutate draft (immer makes it immutable)
        state.nested.deep.value = value;
      });
    },
  }))
);
```

### 4. Separate Actions from State

```typescript
// ❌ Bad (action modifying state directly)
set({ count: get().count + 1 });

// ✅ Good (action encapsulates logic)
increment: () => set((state) => ({ count: state.count + 1 }))
```

### 5. Use TypeScript Strictly

```typescript
// ✅ Always define interfaces
interface State {
  count: number;
  increment: () => void;
}

// ✅ Use generics
export const useStore = create<State>((set) => ({ ... }));
```

---

## Testing Stores

### Test Setup

```typescript
import { renderHook, act } from '@testing-library/react';
import { useAuthStore } from '@/lib/store';

describe('useAuthStore', () => {
  beforeEach(() => {
    // Reset store before each test
    useAuthStore.setState({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,
    });
    
    // Clear localStorage
    localStorage.clear();
  });
  
  it('should initialize with default state', () => {
    const { result } = renderHook(() => useAuthStore());
    
    expect(result.current.user).toBe(null);
    expect(result.current.isAuthenticated).toBe(false);
    expect(result.current.isLoading).toBe(false);
  });
  
  it('should login successfully', async () => {
    const { result } = renderHook(() => useAuthStore());
    
    // Mock API response
    apiClient.post = vi.fn().mockResolvedValue({
      data: {
        token: 'mock-token',
        user: { username: 'admin', role: 'superuser' },
      },
    });
    
    await act(async () => {
      await result.current.login('admin', 'password');
    });
    
    expect(result.current.isAuthenticated).toBe(true);
    expect(result.current.user).toEqual({ username: 'admin', role: 'superuser' });
    expect(localStorage.getItem('authToken')).toBe('mock-token');
  });
  
  it('should logout and clear state', () => {
    const { result } = renderHook(() => useAuthStore());
    
    // Set initial authenticated state
    act(() => {
      useAuthStore.setState({
        user: { username: 'admin', role: 'superuser' },
        token: 'mock-token',
        isAuthenticated: true,
      });
    });
    
    // Logout
    act(() => {
      result.current.logout();
    });
    
    expect(result.current.isAuthenticated).toBe(false);
    expect(result.current.user).toBe(null);
    expect(localStorage.getItem('authToken')).toBe(null);
  });
});
```

### Test Async Actions

```typescript
it('should handle login error', async () => {
  const { result } = renderHook(() => useAuthStore());
  
  // Mock API error
  apiClient.post = vi.fn().mockRejectedValue({
    response: {
      status: 401,
      data: { error: 'invalid-credentials' },
    },
  });
  
  await expect(
    act(async () => {
      await result.current.login('admin', 'wrong-password');
    })
  ).rejects.toThrow();
  
  expect(result.current.isAuthenticated).toBe(false);
  expect(result.current.error).toBeTruthy();
});
```

---

## Migration Guide

### From Context API to Zustand

**Before (Context API):**
```tsx
// Context
const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  
  const login = async (username: string, password: string) => {
    const response = await apiClient.post('/api/auth/login', { username, password });
    setUser(response.data.user);
    setIsAuthenticated(true);
  };
  
  return (
    <AuthContext.Provider value={{ user, isAuthenticated, login }}>
      {children}
    </AuthContext.Provider>
  );
}

// Usage
export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
}
```

**After (Zustand):**
```tsx
// Store
export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: false,
  
  login: async (username: string, password: string) => {
    const response = await apiClient.post('/api/auth/login', { username, password });
    set({ user: response.data.user, isAuthenticated: true });
  },
}));

// Usage (no provider needed!)
const { user, isAuthenticated, login } = useAuthStore();
```

### From Redux to Zustand

**Before (Redux):**
```typescript
// Actions
const LOGIN = 'LOGIN';
const LOGOUT = 'LOGOUT';

// Action creators
const login = (user: User) => ({ type: LOGIN, payload: user });
const logout = () => ({ type: LOGOUT });

// Reducer
function authReducer(state = initialState, action: Action) {
  switch (action.type) {
    case LOGIN:
      return { ...state, user: action.payload, isAuthenticated: true };
    case LOGOUT:
      return { ...state, user: null, isAuthenticated: false };
    default:
      return state;
  }
}

// Store
const store = createStore(authReducer);
```

**After (Zustand):**
```typescript
// Store (all in one!)
export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: false,
  
  login: (user: User) => set({ user, isAuthenticated: true }),
  logout: () => set({ user: null, isAuthenticated: false }),
}));
```

---

## DevTools Integration

### Install Redux DevTools Extension

```bash
# Browser extension
# Chrome: https://chrome.google.com/webstore/detail/redux-devtools
# Firefox: https://addons.mozilla.org/en-US/firefox/addon/reduxdevtools/
```

### Enable DevTools in Store

```typescript
import { devtools } from 'zustand/middleware';

export const useStore = create<State>()(
  devtools(
    (set) => ({
      // Store implementation
    }),
    { name: 'MyStore' }  // DevTools name
  )
);
```

### View in DevTools

1. Open browser DevTools
2. Go to Redux tab
3. See all store actions and state changes
4. Time-travel debugging

---

## Related Documentation

- [React Frontend](./02_REACT_FRONTEND.md)
- [API Client Integration](./05_API_CLIENT_INTEGRATION.md)
- [Component Library](./06_COMPONENT_LIBRARY.md)
- [Zustand Documentation](https://github.com/pmndrs/zustand)

---

**Last Updated:** 2026-04-20  
**Maintainer:** Frontend Team  
**Review Cycle:** Quarterly

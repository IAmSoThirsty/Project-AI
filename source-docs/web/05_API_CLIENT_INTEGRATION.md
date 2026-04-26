---
type: integration-guide
module: web
tags: [api-client, axios, http, integration, zustand]
created: 2026-04-20
status: production
related_systems: [flask-backend, react-frontend, state-management]
stakeholders: [frontend-team, backend-team, integration-team]
platform: web
dependencies: [axios@1.7, zustand@5]
---

# API Client Integration Guide

**Purpose:** HTTP client setup, request/response handling, state management integration  
**Technology:** Axios 1.7 + Zustand 5.0  
**Architecture:** Interceptor-based authentication, centralized error handling

---

## Table of Contents

1. [Axios Client Setup](#axios-client-setup)
2. [Authentication Integration](#authentication-integration)
3. [Request Interceptors](#request-interceptors)
4. [Response Interceptors](#response-interceptors)
5. [Error Handling](#error-handling)
6. [State Management Integration](#state-management-integration)
7. [API Methods](#api-methods)
8. [Testing](#testing)

---

## Axios Client Setup

### Base Configuration

**File:** `lib/api-client.ts` (to be created)

```typescript
import axios, { AxiosInstance, AxiosError } from 'axios';
import { env } from './env';

/**
 * Create configured Axios instance
 */
const apiClient: AxiosInstance = axios.create({
  baseURL: env.NEXT_PUBLIC_API_URL || 'http://localhost:5000',
  timeout: env.NEXT_PUBLIC_API_TIMEOUT || 30000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
  withCredentials: false,  // Set to true if using cookies
});

export default apiClient;
```

### Environment Validation

**File:** `lib/env.ts` (to be created)

```typescript
import { z } from 'zod';

const envSchema = z.object({
  NEXT_PUBLIC_API_URL: z.string().url().default('http://localhost:5000'),
  NEXT_PUBLIC_API_TIMEOUT: z.coerce.number().positive().default(30000),
  NEXT_PUBLIC_APP_NAME: z.string().default('Project-AI'),
  NEXT_PUBLIC_ENV: z.enum(['development', 'production', 'test']).default('development'),
});

export const env = envSchema.parse({
  NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
  NEXT_PUBLIC_API_TIMEOUT: process.env.NEXT_PUBLIC_API_TIMEOUT,
  NEXT_PUBLIC_APP_NAME: process.env.NEXT_PUBLIC_APP_NAME,
  NEXT_PUBLIC_ENV: process.env.NEXT_PUBLIC_ENV,
});
```

---

## Authentication Integration

### JWT Token Management

**Token Storage:**
```typescript
/**
 * Token storage utilities
 */
export const TokenStorage = {
  get: (): string | null => {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem('authToken');
  },
  
  set: (token: string): void => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('authToken', token);
    }
  },
  
  remove: (): void => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('authToken');
    }
  },
  
  isExpired: (token: string): boolean => {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      return payload.exp * 1000 < Date.now();
    } catch {
      return true;
    }
  },
};
```

### User Storage

```typescript
export interface User {
  username: string;
  role: 'superuser' | 'user';
}

export const UserStorage = {
  get: (): User | null => {
    if (typeof window === 'undefined') return null;
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  },
  
  set: (user: User): void => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('user', JSON.stringify(user));
    }
  },
  
  remove: (): void => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('user');
    }
  },
};
```

---

## Request Interceptors

### Add Authentication Token

```typescript
import { TokenStorage } from './storage';

/**
 * Request interceptor: Add JWT token to all requests
 */
apiClient.interceptors.request.use(
  (config) => {
    const token = TokenStorage.get();
    
    // Add token if available and not expired
    if (token && !TokenStorage.isExpired(token)) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // Add request ID for tracking
    config.headers['X-Request-ID'] = crypto.randomUUID();
    
    // Log request in development
    if (env.NEXT_PUBLIC_ENV === 'development') {
      console.log(`[API Request] ${config.method?.toUpperCase()} ${config.url}`, config.data);
    }
    
    return config;
  },
  (error) => {
    console.error('[API Request Error]', error);
    return Promise.reject(error);
  }
);
```

### Add Custom Headers

```typescript
/**
 * Add custom headers for specific routes
 */
apiClient.interceptors.request.use((config) => {
  // Add version header
  config.headers['X-API-Version'] = '1.0';
  
  // Add client info
  config.headers['X-Client'] = 'Project-AI-Web';
  
  // Add timezone
  config.headers['X-Timezone'] = Intl.DateTimeFormat().resolvedOptions().timeZone;
  
  return config;
});
```

---

## Response Interceptors

### Handle Authentication Errors

```typescript
import { useAuthStore } from './store';

/**
 * Response interceptor: Handle 401/403 errors
 */
apiClient.interceptors.response.use(
  (response) => {
    // Log response in development
    if (env.NEXT_PUBLIC_ENV === 'development') {
      console.log(`[API Response] ${response.config.url}`, response.data);
    }
    
    return response;
  },
  (error: AxiosError) => {
    const status = error.response?.status;
    
    // 401 Unauthorized - Token expired or invalid
    if (status === 401) {
      console.warn('[API] Unauthorized - clearing auth state');
      
      // Clear tokens
      TokenStorage.remove();
      UserStorage.remove();
      
      // Update auth store
      useAuthStore.getState().logout();
      
      // Redirect to login (client-side)
      if (typeof window !== 'undefined' && window.location.pathname !== '/') {
        window.location.href = '/';
      }
    }
    
    // 403 Forbidden - Insufficient permissions
    if (status === 403) {
      console.warn('[API] Forbidden - insufficient permissions');
      // Show error notification
    }
    
    // 429 Rate Limited
    if (status === 429) {
      console.warn('[API] Rate limited - too many requests');
      // Show rate limit notification
    }
    
    // 500+ Server errors
    if (status && status >= 500) {
      console.error('[API] Server error:', error.response?.data);
      // Show server error notification
    }
    
    return Promise.reject(error);
  }
);
```

### Response Transformation

```typescript
/**
 * Transform response data
 */
apiClient.interceptors.response.use((response) => {
  // Unwrap nested response structure
  if (response.data && response.data.result) {
    return {
      ...response,
      data: response.data.result,
      metadata: response.data.metadata,
    };
  }
  
  return response;
});
```

---

## Error Handling

### Custom Error Class

```typescript
export class ApiError extends Error {
  constructor(
    message: string,
    public status?: number,
    public code?: string,
    public details?: unknown
  ) {
    super(message);
    this.name = 'ApiError';
  }
  
  static fromAxiosError(error: AxiosError): ApiError {
    const data = error.response?.data as any;
    return new ApiError(
      data?.message || error.message || 'An unknown error occurred',
      error.response?.status,
      data?.error,
      data
    );
  }
}
```

### Error Handler Utility

```typescript
export function handleApiError(error: unknown): ApiError {
  if (error instanceof ApiError) {
    return error;
  }
  
  if (axios.isAxiosError(error)) {
    return ApiError.fromAxiosError(error);
  }
  
  if (error instanceof Error) {
    return new ApiError(error.message);
  }
  
  return new ApiError('An unknown error occurred');
}
```

---

## State Management Integration

### Zustand Auth Store

**File:** `lib/store.ts` (to be created)

```typescript
import { create } from 'zustand';
import apiClient from './api-client';
import { TokenStorage, UserStorage, User } from './storage';
import { handleApiError, ApiError } from './errors';

interface AuthState {
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

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  token: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,
  
  login: async (username: string, password: string) => {
    set({ isLoading: true, error: null });
    
    try {
      const response = await apiClient.post('/api/auth/login', {
        username,
        password,
      });
      
      const { token, user } = response.data;
      
      // Store in localStorage
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
  
  clearError: () => set({ error: null }),
}));
```

### Hydration Pattern

```typescript
/**
 * Initialize auth state from localStorage on mount
 */
export function useAuthHydration() {
  const checkAuth = useAuthStore((state) => state.checkAuth);
  
  useEffect(() => {
    checkAuth();
  }, [checkAuth]);
}

// Usage in app/layout.tsx
export default function RootLayout({ children }: { children: React.ReactNode }) {
  useAuthHydration();
  
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
```

---

## API Methods

### Authentication APIs

```typescript
export interface LoginCredentials {
  username: string;
  password: string;
}

export interface LoginResponse {
  status: string;
  success: boolean;
  token: string;
  user: User;
}

/**
 * User login
 */
export async function login(credentials: LoginCredentials): Promise<LoginResponse> {
  const response = await apiClient.post<LoginResponse>('/api/auth/login', credentials);
  return response.data;
}

/**
 * User logout (token revocation)
 */
export async function logout(): Promise<void> {
  await apiClient.post('/api/auth/logout');
}
```

### AI APIs

```typescript
export interface ChatRequest {
  prompt: string;
  model?: string;
  provider?: string;
}

export interface ChatResponse {
  result: {
    response: string;
    model: string;
    tokens_used: number;
  };
  metadata: {
    execution_time_ms: number;
    provider: string;
    governance_checks: string[];
  };
}

/**
 * Send chat message to AI
 */
export async function sendChatMessage(request: ChatRequest): Promise<ChatResponse> {
  const response = await apiClient.post<ChatResponse>('/api/ai/chat', request);
  return response.data;
}

export interface ImageRequest {
  prompt: string;
  model?: string;
  provider?: string;
  size?: string;
}

export interface ImageResponse {
  result: {
    image_url: string;
    prompt: string;
    model: string;
    size: string;
  };
  metadata: {
    execution_time_ms: number;
    provider: string;
  };
}

/**
 * Generate AI image
 */
export async function generateImage(request: ImageRequest): Promise<ImageResponse> {
  const response = await apiClient.post<ImageResponse>('/api/ai/image', request);
  return response.data;
}
```

### Persona APIs

```typescript
export interface PersonaUpdateRequest {
  trait: string;
  value: number;
}

export interface PersonaUpdateResponse {
  success: boolean;
  result: {
    trait: string;
    old_value: number;
    new_value: number;
  };
}

/**
 * Update AI persona trait
 */
export async function updatePersonaTrait(request: PersonaUpdateRequest): Promise<PersonaUpdateResponse> {
  const response = await apiClient.post<PersonaUpdateResponse>('/api/persona/update', request);
  return response.data;
}
```

### Health Check API

```typescript
export interface StatusResponse {
  status: string;
  component: string;
}

/**
 * Check backend health
 */
export async function checkStatus(): Promise<StatusResponse> {
  const response = await apiClient.get<StatusResponse>('/api/status');
  return response.data;
}
```

---

## Testing

### Mock API Client

**File:** `__mocks__/api-client.ts`

```typescript
import { vi } from 'vitest';

export const apiClient = {
  get: vi.fn(),
  post: vi.fn(),
  put: vi.fn(),
  delete: vi.fn(),
};

export default apiClient;
```

### Test Login Flow

```typescript
import { renderHook, act } from '@testing-library/react';
import { useAuthStore } from '@/lib/store';
import apiClient from '@/lib/api-client';

vi.mock('@/lib/api-client');

describe('useAuthStore', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });
  
  it('should login successfully', async () => {
    const mockResponse = {
      data: {
        status: 'ok',
        success: true,
        token: 'mock-token',
        user: { username: 'admin', role: 'superuser' },
      },
    };
    
    apiClient.post.mockResolvedValue(mockResponse);
    
    const { result } = renderHook(() => useAuthStore());
    
    await act(async () => {
      await result.current.login('admin', 'password');
    });
    
    expect(result.current.isAuthenticated).toBe(true);
    expect(result.current.user).toEqual({ username: 'admin', role: 'superuser' });
    expect(localStorage.getItem('authToken')).toBe('mock-token');
  });
  
  it('should handle login error', async () => {
    apiClient.post.mockRejectedValue({
      response: {
        status: 401,
        data: { error: 'invalid-credentials', message: 'Authentication failed' },
      },
    });
    
    const { result } = renderHook(() => useAuthStore());
    
    await expect(
      act(async () => {
        await result.current.login('admin', 'wrong-password');
      })
    ).rejects.toThrow();
    
    expect(result.current.isAuthenticated).toBe(false);
    expect(result.current.error).toBeTruthy();
  });
  
  it('should logout and clear storage', () => {
    localStorage.setItem('authToken', 'mock-token');
    localStorage.setItem('user', JSON.stringify({ username: 'admin', role: 'superuser' }));
    
    const { result } = renderHook(() => useAuthStore());
    
    act(() => {
      result.current.logout();
    });
    
    expect(result.current.isAuthenticated).toBe(false);
    expect(result.current.user).toBe(null);
    expect(localStorage.getItem('authToken')).toBe(null);
  });
});
```

### Test API Methods

```typescript
import { sendChatMessage } from '@/lib/api-client';
import apiClient from '@/lib/api-client';

vi.mock('@/lib/api-client');

describe('API Methods', () => {
  it('should send chat message', async () => {
    const mockResponse = {
      data: {
        result: {
          response: 'Hello!',
          model: 'gpt-4',
          tokens_used: 10,
        },
        metadata: {
          execution_time_ms: 500,
          provider: 'openai',
          governance_checks: ['four_laws'],
        },
      },
    };
    
    apiClient.post.mockResolvedValue(mockResponse);
    
    const result = await sendChatMessage({
      prompt: 'Hello',
      model: 'gpt-4',
    });
    
    expect(result.result.response).toBe('Hello!');
    expect(apiClient.post).toHaveBeenCalledWith('/api/ai/chat', {
      prompt: 'Hello',
      model: 'gpt-4',
    });
  });
});
```

---

## Best Practices

### 1. Always Handle Errors

```typescript
// ❌ Bad (no error handling)
const data = await sendChatMessage({ prompt: 'Hello' });

// ✅ Good (with error handling)
try {
  const data = await sendChatMessage({ prompt: 'Hello' });
} catch (error) {
  const apiError = handleApiError(error);
  console.error(apiError.message);
}
```

### 2. Use TypeScript Types

```typescript
// ❌ Bad (no types)
const response = await apiClient.post('/api/auth/login', { username, password });

// ✅ Good (with types)
const response = await apiClient.post<LoginResponse>('/api/auth/login', {
  username,
  password,
});
```

### 3. Check Token Expiration

```typescript
// ❌ Bad (no expiration check)
const token = TokenStorage.get();
if (token) {
  // Use token (might be expired)
}

// ✅ Good (with expiration check)
const token = TokenStorage.get();
if (token && !TokenStorage.isExpired(token)) {
  // Use token (guaranteed valid)
}
```

### 4. Centralize API Calls

```typescript
// ❌ Bad (API calls in components)
function MyComponent() {
  const [data, setData] = useState(null);
  
  useEffect(() => {
    apiClient.post('/api/ai/chat', { prompt: 'Hello' })
      .then(res => setData(res.data));
  }, []);
}

// ✅ Good (API calls in store/service)
function MyComponent() {
  const { sendMessage, response } = useChatStore();
  
  useEffect(() => {
    sendMessage('Hello');
  }, []);
}
```

### 5. Use Request Cancellation

```typescript
import { CancelTokenSource } from 'axios';

function MyComponent() {
  useEffect(() => {
    const source = axios.CancelToken.source();
    
    apiClient.get('/api/data', {
      cancelToken: source.token,
    });
    
    return () => {
      source.cancel('Component unmounted');
    };
  }, []);
}
```

---

## Troubleshooting

### Issue: CORS Errors

**Symptom:** `Access-Control-Allow-Origin` error

**Solution:**
1. Verify backend CORS configuration
2. Check `baseURL` in `api-client.ts`
3. Use proxy in `next.config.js`:

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

### Issue: Token Not Sent

**Symptom:** 401 errors despite having token

**Solution:**
1. Check `Authorization` header in browser DevTools
2. Verify token format: `Bearer <token>`
3. Ensure interceptor is registered before requests

### Issue: Request Timeout

**Symptom:** Requests fail after 30 seconds

**Solution:**
```typescript
// Increase timeout for specific requests
await apiClient.post('/api/ai/chat', data, {
  timeout: 60000,  // 60 seconds
});
```

---

## Related Documentation

- [Flask Backend API](./01_FLASK_BACKEND_API.md)
- [React Frontend](./02_REACT_FRONTEND.md)
- [Security Practices](./04_SECURITY_PRACTICES.md)
- [Zustand Documentation](https://github.com/pmndrs/zustand)
- [Axios Documentation](https://axios-http.com)

---

**Last Updated:** 2026-04-20  
**Maintainer:** Frontend Team  
**Review Cycle:** Quarterly

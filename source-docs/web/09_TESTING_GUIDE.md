---
type: testing-guide
module: web
tags: [testing, jest, react-testing-library, e2e, integration]
created: 2026-04-20
status: production
related_systems: [react-frontend, components, api-client]
stakeholders: [qa-team, frontend-team, devops-team]
platform: web
dependencies: [jest@29, @testing-library/react@16, vitest]
---

# Testing Guide for Web Application

**Purpose:** Comprehensive testing strategies for Project-AI web application  
**Frameworks:** Jest 29 + React Testing Library 16 + Vitest  
**Coverage Target:** 80%+ code coverage

---

## Table of Contents

1. [Testing Strategy](#testing-strategy)
2. [Unit Testing](#unit-testing)
3. [Integration Testing](#integration-testing)
4. [End-to-End Testing](#end-to-end-testing)
5. [Testing Components](#testing-components)
6. [Testing Stores](#testing-stores)
7. [Testing API Calls](#testing-api-calls)
8. [Test Coverage](#test-coverage)

---

## Testing Strategy

### Test Pyramid

```
       /\
      /  \     E2E Tests (10%)
     /____\    - Critical user flows
    /      \   - Login → Dashboard → Logout
   /        \
  /__________\ Integration Tests (30%)
 /            \  - Component + API integration
/______________\ - Multi-component interactions
 
________________
                 Unit Tests (60%)
                 - Individual functions
                 - Component rendering
                 - Store actions
```

### Testing Levels

1. **Unit Tests** - Test individual functions, components, and modules in isolation
2. **Integration Tests** - Test how components work together
3. **E2E Tests** - Test complete user workflows in a real browser

---

## Unit Testing

### Setup

**File:** `jest.config.js`

```javascript
module.exports = {
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/$1',
    '\\.(css|less|scss|sass)$': 'identity-obj-proxy',
  },
  collectCoverageFrom: [
    'components/**/*.{ts,tsx}',
    'lib/**/*.{ts,tsx}',
    'utils/**/*.{ts,tsx}',
    '!**/*.d.ts',
    '!**/node_modules/**',
  ],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80,
    },
  },
  transform: {
    '^.+\\.(ts|tsx)$': ['@swc/jest', {
      jsc: {
        parser: {
          syntax: 'typescript',
          tsx: true,
        },
      },
    }],
  },
};
```

**File:** `jest.setup.js`

```javascript
import '@testing-library/jest-dom';

// Mock Next.js router
jest.mock('next/navigation', () => ({
  useRouter() {
    return {
      push: jest.fn(),
      replace: jest.fn(),
      prefetch: jest.fn(),
    };
  },
  usePathname() {
    return '/';
  },
}));

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
global.localStorage = localStorageMock;
```

### Testing Utilities

**File:** `utils/validators.test.ts`

```typescript
import { validateUsername, validatePassword, sanitizeInput } from './validators';

describe('validators', () => {
  describe('validateUsername', () => {
    it('should accept valid usernames', () => {
      expect(validateUsername('admin')).toBe(null);
      expect(validateUsername('user_123')).toBe(null);
      expect(validateUsername('test-user')).toBe(null);
    });
    
    it('should reject empty usernames', () => {
      expect(validateUsername('')).toBe('Username is required');
      expect(validateUsername('  ')).toBe('Username is required');
    });
    
    it('should reject short usernames', () => {
      expect(validateUsername('ab')).toBe('Username must be at least 3 characters');
    });
    
    it('should reject long usernames', () => {
      const longUsername = 'a'.repeat(51);
      expect(validateUsername(longUsername)).toBe('Username must be less than 50 characters');
    });
    
    it('should reject invalid characters', () => {
      expect(validateUsername('user@123')).toContain('can only contain');
      expect(validateUsername('user 123')).toContain('can only contain');
    });
  });
  
  describe('validatePassword', () => {
    it('should accept valid passwords', () => {
      expect(validatePassword('password123')).toBe(null);
      expect(validatePassword('securepass')).toBe(null);
    });
    
    it('should reject empty passwords', () => {
      expect(validatePassword('')).toBe('Password is required');
    });
    
    it('should reject short passwords', () => {
      expect(validatePassword('12345')).toBe('Password must be at least 6 characters');
    });
    
    it('should reject long passwords', () => {
      const longPassword = 'a'.repeat(129);
      expect(validatePassword(longPassword)).toBe('Password must be less than 128 characters');
    });
  });
  
  describe('sanitizeInput', () => {
    it('should remove dangerous characters', () => {
      expect(sanitizeInput('<script>alert("XSS")</script>')).toBe('scriptalert("XSS")/script');
      expect(sanitizeInput('Hello<>World')).toBe('HelloWorld');
    });
    
    it('should preserve safe characters', () => {
      expect(sanitizeInput('Hello World 123')).toBe('Hello World 123');
    });
  });
});
```

---

## Integration Testing

### Testing Component + API Integration

**File:** `components/LoginForm.test.tsx`

```typescript
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { act } from 'react-dom/test-utils';
import LoginForm from './LoginForm';
import { useAuthStore } from '@/lib/store';
import apiClient from '@/lib/api-client';

// Mock API client
jest.mock('@/lib/api-client');

describe('LoginForm Integration', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
    
    // Reset auth store
    act(() => {
      useAuthStore.setState({
        user: null,
        token: null,
        isAuthenticated: false,
        isLoading: false,
        error: null,
      });
    });
  });
  
  it('should login successfully and update store', async () => {
    const mockResponse = {
      data: {
        status: 'ok',
        success: true,
        token: 'mock-jwt-token',
        user: { username: 'admin', role: 'superuser' },
      },
    };
    
    apiClient.post.mockResolvedValue(mockResponse);
    
    render(<LoginForm />);
    
    // Fill form
    const usernameInput = screen.getByPlaceholderText('Enter your username');
    const passwordInput = screen.getByPlaceholderText('Enter your password');
    const submitButton = screen.getByRole('button', { name: /login/i });
    
    fireEvent.change(usernameInput, { target: { value: 'admin' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    fireEvent.click(submitButton);
    
    // Wait for async operations
    await waitFor(() => {
      expect(apiClient.post).toHaveBeenCalledWith('/api/auth/login', {
        username: 'admin',
        password: 'password123',
      });
    });
    
    // Check store updated
    const store = useAuthStore.getState();
    expect(store.isAuthenticated).toBe(true);
    expect(store.user).toEqual({ username: 'admin', role: 'superuser' });
    expect(localStorage.getItem('authToken')).toBe('mock-jwt-token');
  });
  
  it('should handle login errors', async () => {
    const mockError = {
      response: {
        status: 401,
        data: {
          status: 'error',
          success: false,
          error: 'invalid-credentials',
          message: 'Invalid username or password',
        },
      },
    };
    
    apiClient.post.mockRejectedValue(mockError);
    
    render(<LoginForm />);
    
    // Fill form with invalid credentials
    fireEvent.change(screen.getByPlaceholderText('Enter your username'), {
      target: { value: 'admin' },
    });
    fireEvent.change(screen.getByPlaceholderText('Enter your password'), {
      target: { value: 'wrongpassword' },
    });
    fireEvent.click(screen.getByRole('button', { name: /login/i }));
    
    // Wait for error message
    await waitFor(() => {
      expect(screen.getByText(/invalid username or password/i)).toBeInTheDocument();
    });
    
    // Check store not authenticated
    const store = useAuthStore.getState();
    expect(store.isAuthenticated).toBe(false);
    expect(store.user).toBe(null);
  });
  
  it('should validate inputs before submission', async () => {
    render(<LoginForm />);
    
    const submitButton = screen.getByRole('button', { name: /login/i });
    
    // Submit without filling form
    fireEvent.click(submitButton);
    
    // Wait for validation errors
    await waitFor(() => {
      expect(screen.getByText('Username is required')).toBeInTheDocument();
    });
    
    // API should not be called
    expect(apiClient.post).not.toHaveBeenCalled();
  });
});
```

---

## End-to-End Testing

### Setup Playwright

```bash
npm install -D @playwright/test
npx playwright install
```

**File:** `playwright.config.ts`

```typescript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
  ],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
});
```

### E2E Test Example

**File:** `e2e/login-flow.spec.ts`

```typescript
import { test, expect } from '@playwright/test';

test.describe('Login Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });
  
  test('should display login page', async ({ page }) => {
    await expect(page.getByRole('heading', { name: /project-ai/i })).toBeVisible();
    await expect(page.getByPlaceholderText('Enter your username')).toBeVisible();
    await expect(page.getByPlaceholderText('Enter your password')).toBeVisible();
    await expect(page.getByRole('button', { name: /login/i })).toBeVisible();
  });
  
  test('should login successfully with valid credentials', async ({ page }) => {
    // Fill login form
    await page.getByPlaceholderText('Enter your username').fill('admin');
    await page.getByPlaceholderText('Enter your password').fill('open-sesame');
    
    // Click login button
    await page.getByRole('button', { name: /login/i }).click();
    
    // Wait for navigation to dashboard
    await expect(page).toHaveURL('/dashboard');
    
    // Check dashboard elements
    await expect(page.getByText(/welcome.*admin/i)).toBeVisible();
    await expect(page.getByRole('button', { name: /logout/i })).toBeVisible();
  });
  
  test('should show error with invalid credentials', async ({ page }) => {
    // Fill login form with invalid credentials
    await page.getByPlaceholderText('Enter your username').fill('admin');
    await page.getByPlaceholderText('Enter your password').fill('wrongpassword');
    
    // Click login button
    await page.getByRole('button', { name: /login/i }).click();
    
    // Wait for error message
    await expect(page.getByText(/invalid.*credentials/i)).toBeVisible();
    
    // Should stay on login page
    await expect(page).toHaveURL('/');
  });
  
  test('should validate form fields', async ({ page }) => {
    // Click login without filling form
    await page.getByRole('button', { name: /login/i }).click();
    
    // Wait for validation errors
    await expect(page.getByText(/username.*required/i)).toBeVisible();
  });
  
  test('should logout successfully', async ({ page }) => {
    // Login
    await page.getByPlaceholderText('Enter your username').fill('admin');
    await page.getByPlaceholderText('Enter your password').fill('open-sesame');
    await page.getByRole('button', { name: /login/i }).click();
    
    // Wait for dashboard
    await expect(page).toHaveURL('/dashboard');
    
    // Click logout
    await page.getByRole('button', { name: /logout/i }).click();
    
    // Should redirect to login page
    await expect(page).toHaveURL('/');
    await expect(page.getByPlaceholderText('Enter your username')).toBeVisible();
  });
});

test.describe('Dashboard Navigation', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto('/');
    await page.getByPlaceholderText('Enter your username').fill('admin');
    await page.getByPlaceholderText('Enter your password').fill('open-sesame');
    await page.getByRole('button', { name: /login/i }).click();
    await expect(page).toHaveURL('/dashboard');
  });
  
  test('should navigate between tabs', async ({ page }) => {
    // Check Overview tab is active
    await expect(page.getByRole('button', { name: /overview/i })).toHaveClass(/bg-gradient/);
    
    // Click Persona tab
    await page.getByRole('button', { name: /ai persona/i }).click();
    await expect(page.getByText(/personality traits/i)).toBeVisible();
    
    // Click Image Generation tab
    await page.getByRole('button', { name: /image generation/i }).click();
    await expect(page.getByText(/backends available/i)).toBeVisible();
  });
});
```

---

## Testing Components

### Component Rendering Tests

```typescript
import { render, screen } from '@testing-library/react';
import Dashboard from './Dashboard';

describe('Dashboard Component', () => {
  const mockUser = {
    username: 'admin',
    role: 'superuser' as const,
  };
  
  const mockOnLogout = jest.fn();
  
  it('should render with user info', () => {
    render(<Dashboard user={mockUser} onLogout={mockOnLogout} />);
    
    expect(screen.getByText(/welcome.*admin/i)).toBeInTheDocument();
    expect(screen.getByText(/superuser/i)).toBeInTheDocument();
  });
  
  it('should render all tabs', () => {
    render(<Dashboard user={mockUser} onLogout={mockOnLogout} />);
    
    expect(screen.getByRole('button', { name: /overview/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /ai persona/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /image generation/i })).toBeInTheDocument();
  });
  
  it('should call onLogout when logout button clicked', () => {
    render(<Dashboard user={mockUser} onLogout={mockOnLogout} />);
    
    const logoutButton = screen.getByRole('button', { name: /logout/i });
    fireEvent.click(logoutButton);
    
    expect(mockOnLogout).toHaveBeenCalledTimes(1);
  });
});
```

---

## Testing Stores

### Zustand Store Tests

```typescript
import { renderHook, act } from '@testing-library/react';
import { useAuthStore } from '@/lib/store';
import apiClient from '@/lib/api-client';

jest.mock('@/lib/api-client');

describe('useAuthStore', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
    
    // Reset store
    act(() => {
      useAuthStore.setState({
        user: null,
        token: null,
        isAuthenticated: false,
        isLoading: false,
        error: null,
      });
    });
  });
  
  it('should have initial state', () => {
    const { result } = renderHook(() => useAuthStore());
    
    expect(result.current.user).toBe(null);
    expect(result.current.isAuthenticated).toBe(false);
    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBe(null);
  });
  
  it('should login successfully', async () => {
    const mockResponse = {
      data: {
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
    expect(result.current.token).toBe('mock-token');
    expect(localStorage.getItem('authToken')).toBe('mock-token');
  });
  
  it('should handle login error', async () => {
    const mockError = {
      response: {
        status: 401,
        data: { error: 'invalid-credentials', message: 'Authentication failed' },
      },
    };
    
    apiClient.post.mockRejectedValue(mockError);
    
    const { result } = renderHook(() => useAuthStore());
    
    await expect(
      act(async () => {
        await result.current.login('admin', 'wrongpassword');
      })
    ).rejects.toThrow();
    
    expect(result.current.isAuthenticated).toBe(false);
    expect(result.current.error).toBeTruthy();
  });
  
  it('should logout and clear storage', () => {
    const { result } = renderHook(() => useAuthStore());
    
    // Set authenticated state
    act(() => {
      useAuthStore.setState({
        user: { username: 'admin', role: 'superuser' },
        token: 'mock-token',
        isAuthenticated: true,
      });
      localStorage.setItem('authToken', 'mock-token');
    });
    
    // Logout
    act(() => {
      result.current.logout();
    });
    
    expect(result.current.isAuthenticated).toBe(false);
    expect(result.current.user).toBe(null);
    expect(result.current.token).toBe(null);
    expect(localStorage.getItem('authToken')).toBe(null);
  });
});
```

---

## Testing API Calls

### Mock API Responses

```typescript
import { sendChatMessage, generateImage } from '@/lib/api-client';
import apiClient from '@/lib/api-client';

jest.mock('@/lib/api-client');

describe('API Client', () => {
  describe('sendChatMessage', () => {
    it('should send chat message successfully', async () => {
      const mockResponse = {
        data: {
          result: {
            response: 'Hello! How can I help you?',
            model: 'gpt-4',
            tokens_used: 15,
          },
          metadata: {
            execution_time_ms: 500,
            provider: 'openai',
          },
        },
      };
      
      apiClient.post.mockResolvedValue(mockResponse);
      
      const result = await sendChatMessage({
        prompt: 'Hello',
        model: 'gpt-4',
      });
      
      expect(result.result.response).toBe('Hello! How can I help you?');
      expect(apiClient.post).toHaveBeenCalledWith('/api/ai/chat', {
        prompt: 'Hello',
        model: 'gpt-4',
      });
    });
  });
  
  describe('generateImage', () => {
    it('should generate image successfully', async () => {
      const mockResponse = {
        data: {
          result: {
            image_url: 'https://example.com/image.png',
            prompt: 'A sunset',
            model: 'dall-e-3',
            size: '1024x1024',
          },
        },
      };
      
      apiClient.post.mockResolvedValue(mockResponse);
      
      const result = await generateImage({
        prompt: 'A sunset',
        model: 'dall-e-3',
      });
      
      expect(result.result.image_url).toBe('https://example.com/image.png');
    });
  });
});
```

---

## Test Coverage

### Running Tests

```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage

# Run E2E tests
npx playwright test

# Run specific test file
npm test -- LoginForm.test.tsx
```

### Coverage Report

```bash
npm run test:coverage

# Output:
----------------------|---------|----------|---------|---------|-------------------
File                  | % Stmts | % Branch | % Funcs | % Lines | Uncovered Line #s 
----------------------|---------|----------|---------|---------|-------------------
All files             |   85.2  |   78.4   |   88.1  |   85.9  |
 components/          |   92.1  |   85.3   |   94.2  |   92.5  |
  Dashboard.tsx       |   91.8  |   84.5   |   93.3  |   92.1  | 45-48,102-105
  LoginForm.tsx       |   94.2  |   88.7   |   96.1  |   94.6  | 78-82
 lib/                 |   82.5  |   75.2   |   84.3  |   83.1  |
  api-client.ts       |   88.3  |   82.1   |   90.2  |   88.9  | 102-107,145-149
  store.ts            |   79.4  |   71.3   |   81.5  |   80.2  | 23-27,89-95
 utils/               |   90.3  |   83.5   |   92.7  |   91.1  |
  validators.ts       |   95.1  |   91.2   |   97.3  |   95.8  | 18-21
```

---

## Best Practices

### 1. Test Behavior, Not Implementation

**❌ Bad:**
```typescript
it('should call setState', () => {
  const { result } = renderHook(() => useState(0));
  act(() => result.current[1](1));
  expect(result.current[1]).toHaveBeenCalled();  // Testing implementation
});
```

**✅ Good:**
```typescript
it('should update count when button clicked', () => {
  render(<Counter />);
  fireEvent.click(screen.getByRole('button'));
  expect(screen.getByText('Count: 1')).toBeInTheDocument();  // Testing behavior
});
```

### 2. Use Data-Testid Sparingly

**❌ Bad:**
```tsx
<button data-testid="submit-button">Submit</button>
screen.getByTestId('submit-button');
```

**✅ Good:**
```tsx
<button>Submit</button>
screen.getByRole('button', { name: /submit/i });
```

### 3. Clean Up After Tests

```typescript
afterEach(() => {
  jest.clearAllMocks();
  localStorage.clear();
});
```

---

## Related Documentation

- [React Frontend](./02_REACT_FRONTEND.md)
- [Component Library](./06_COMPONENT_LIBRARY.md)
- [State Management](./07_STATE_MANAGEMENT.md)
- [Jest Documentation](https://jestjs.io)
- [React Testing Library](https://testing-library.com/react)
- [Playwright](https://playwright.dev)

---

**Last Updated:** 2026-04-20  
**Maintainer:** QA Team / Frontend Team  
**Review Cycle:** Monthly

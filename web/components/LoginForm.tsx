/**
 * Login form component with validation and error handling
 */

'use client';

import { useState, FormEvent } from 'react';
import { useAuthStore } from '@/lib/store';
import { validateUsername, validatePassword, sanitizeInput } from '@/utils/validators';
import { ApiError } from '@/lib/api-client';

export default function LoginForm() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [errors, setErrors] = useState<{ username?: string; password?: string; general?: string }>({});
  const { login, isLoading, error: apiError } = useAuthStore();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setErrors({});

    // Sanitize and validate inputs
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

    try {
      await login(sanitizedUsername, password);
    } catch (error) {
      const apiErr = error as ApiError;
      setErrors({ general: apiErr.message });
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label htmlFor="username" className="block text-sm font-medium mb-2">
          Username
        </label>
        <input
          id="username"
          type="text"
          className="input"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          placeholder="Enter your username"
          disabled={isLoading}
          autoComplete="username"
          required
        />
        {errors.username && <p className="error-message">{errors.username}</p>}
      </div>

      <div>
        <label htmlFor="password" className="block text-sm font-medium mb-2">
          Password
        </label>
        <input
          id="password"
          type="password"
          className="input"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Enter your password"
          disabled={isLoading}
          autoComplete="current-password"
          required
        />
        {errors.password && <p className="error-message">{errors.password}</p>}
      </div>

      {(errors.general || apiError) && (
        <div className="error-message">
          {errors.general || apiError?.message}
        </div>
      )}

      <button
        type="submit"
        className="button button-primary w-full"
        disabled={isLoading}
      >
        {isLoading ? (
          <span className="flex items-center justify-center gap-2">
            <span className="loading"></span>
            Logging in...
          </span>
        ) : (
          'Login'
        )}
      </button>
    </form>
  );
}

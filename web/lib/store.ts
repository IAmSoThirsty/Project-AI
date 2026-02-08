/**
 * Global state management using Zustand
 */

import { create } from 'zustand';
import { apiClient, ApiError } from './api-client';

export interface User {
  username: string;
  role: string;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: ApiError | null;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  checkAuth: () => Promise<void>;
  clearError: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,

  login: async (username: string, password: string) => {
    set({ isLoading: true, error: null });
    try {
      const response = await apiClient.login({ username, password });
      set({
        user: response.user,
        token: response.token,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      });
    } catch (error) {
      set({
        user: null,
        token: null,
        isAuthenticated: false,
        isLoading: false,
        error: error as ApiError,
      });
      throw error;
    }
  },

  logout: () => {
    apiClient.clearToken();
    set({
      user: null,
      token: null,
      isAuthenticated: false,
      error: null,
    });
  },

  checkAuth: async () => {
    const token = apiClient.getToken();
    if (!token) {
      set({ isAuthenticated: false, user: null, token: null });
      return;
    }

    try {
      const response = await apiClient.getProfile();
      set({
        user: response.user,
        token,
        isAuthenticated: true,
        error: null,
      });
    } catch (error) {
      apiClient.clearToken();
      set({
        user: null,
        token: null,
        isAuthenticated: false,
        error: error as ApiError,
      });
    }
  },

  clearError: () => set({ error: null }),
}));

interface AppState {
  backendStatus: 'checking' | 'online' | 'offline';
  lastStatusCheck: Date | null;
  checkBackendStatus: () => Promise<void>;
}

export const useAppStore = create<AppState>((set) => ({
  backendStatus: 'checking',
  lastStatusCheck: null,

  checkBackendStatus: async () => {
    try {
      await apiClient.checkStatus();
      set({ backendStatus: 'online', lastStatusCheck: new Date() });
    } catch {
      set({ backendStatus: 'offline', lastStatusCheck: new Date() });
    }
  },
}));

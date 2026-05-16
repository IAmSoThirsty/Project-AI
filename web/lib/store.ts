import { create } from 'zustand';
import { apiClient, ApiError } from '@/lib/api-client';

export interface User {
  username: string;
  role: string;
}

type BackendStatus = 'checking' | 'online' | 'offline';

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: ApiError | null;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
}

interface AppState {
  backendStatus: BackendStatus;
  checkBackendStatus: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,

  async login(username: string, password: string) {
    set({ isLoading: true, error: null });
    try {
      const response = await apiClient.login(username, password);
      set({
        user: response.user,
        token: response.token,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      });
    } catch (error) {
      const apiError = error as ApiError;
      set({
        user: null,
        token: null,
        isAuthenticated: false,
        isLoading: false,
        error: apiError,
      });
      throw apiError;
    }
  },

  logout() {
    set({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,
    });
  },
}));

export const useAppStore = create<AppState>((set) => ({
  backendStatus: 'checking',

  async checkBackendStatus() {
    set({ backendStatus: 'checking' });
    const backendStatus = await apiClient.status();
    set({ backendStatus });
  },
}));

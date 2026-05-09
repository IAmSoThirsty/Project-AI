import axios, { AxiosError } from 'axios';
import { env } from '@/lib/env';

export interface ApiError {
  message: string;
  status?: number;
  code?: string;
}

export interface LoginResponse {
  success: boolean;
  token: string;
  user: {
    username: string;
    role: string;
  };
}

const client = axios.create({
  baseURL: env.NEXT_PUBLIC_API_URL,
  timeout: env.NEXT_PUBLIC_API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
});

const toApiError = (error: unknown): ApiError => {
  const axiosError = error as AxiosError<{ message?: string; error?: string }>;
  if (axiosError.response) {
    return {
      message:
        axiosError.response.data?.message ||
        axiosError.response.data?.error ||
        'Request failed',
      status: axiosError.response.status,
      code: axiosError.code,
    };
  }
  return {
    message: axiosError.message || 'Network request failed',
    code: axiosError.code,
  };
};

export const apiClient = {
  async login(username: string, password: string): Promise<LoginResponse> {
    try {
      const response = await client.post<LoginResponse>('/api/auth/login', {
        username,
        password,
      });
      return response.data;
    } catch (error) {
      throw toApiError(error);
    }
  },

  async status(): Promise<'online' | 'offline'> {
    try {
      const response = await client.get('/api/status');
      return response.status === 200 ? 'online' : 'offline';
    } catch {
      return 'offline';
    }
  },
};

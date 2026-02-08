/**
 * API client for Project-AI backend
 */

import axios, { AxiosError, AxiosInstance, AxiosRequestConfig } from 'axios';
import { env } from './env';

export interface ApiError {
  error: string;
  message: string;
  status: number;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  status: string;
  token: string;
  user: {
    username: string;
    role: string;
  };
}

export interface ProfileResponse {
  status: string;
  user: {
    username: string;
    role: string;
  };
}

export interface StatusResponse {
  status: string;
  component: string;
}

class ApiClient {
  private client: AxiosInstance;
  private token: string | null = null;

  constructor() {
    this.client = axios.create({
      baseURL: env.NEXT_PUBLIC_API_URL,
      timeout: env.NEXT_PUBLIC_API_TIMEOUT,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add request interceptor for auth token
    this.client.interceptors.request.use(
      (config) => {
        if (this.token) {
          config.headers['X-Auth-Token'] = this.token;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Add response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401 || error.response?.status === 403) {
          // Clear token on auth errors
          this.clearToken();
        }
        return Promise.reject(this.formatError(error));
      }
    );
  }

  private formatError(error: AxiosError): ApiError {
    if (error.response) {
      const data = error.response.data as { error?: string; message?: string };
      return {
        error: data.error || 'unknown_error',
        message: data.message || 'An unknown error occurred',
        status: error.response.status,
      };
    } else if (error.request) {
      return {
        error: 'network_error',
        message: 'Unable to connect to the server',
        status: 0,
      };
    } else {
      return {
        error: 'client_error',
        message: error.message || 'An error occurred',
        status: 0,
      };
    }
  }

  setToken(token: string) {
    this.token = token;
    if (typeof window !== 'undefined') {
      localStorage.setItem('auth_token', token);
    }
  }

  getToken(): string | null {
    if (!this.token && typeof window !== 'undefined') {
      this.token = localStorage.getItem('auth_token');
    }
    return this.token;
  }

  clearToken() {
    this.token = null;
    if (typeof window !== 'undefined') {
      localStorage.removeItem('auth_token');
    }
  }

  async login(credentials: LoginRequest): Promise<LoginResponse> {
    const response = await this.client.post<LoginResponse>('/api/auth/login', credentials);
    this.setToken(response.data.token);
    return response.data;
  }

  async getProfile(): Promise<ProfileResponse> {
    const response = await this.client.get<ProfileResponse>('/api/auth/profile');
    return response.data;
  }

  async checkStatus(): Promise<StatusResponse> {
    const response = await this.client.get<StatusResponse>('/api/status');
    return response.data;
  }

  async request<T>(config: AxiosRequestConfig): Promise<T> {
    const response = await this.client.request<T>(config);
    return response.data;
  }
}

// Singleton instance
export const apiClient = new ApiClient();

export interface User {
  id: string;
  username: string;
  email: string;
  role: 'admin' | 'creator' | 'viewer';
  created_at: string;
  last_login: string | null;
}

export interface TexturePack {
  id: string;
  name: string;
  slug: string;
  description: string;
  version: string;
  category: string;
  quality_tier: 'pixel' | 'standard' | 'high' | 'cinematic' | 'ultra';
  license: string;
  status: 'draft' | 'published' | 'archived';
  size_bytes: number;
  download_count: number;
  tags: string[];
  preview_image_url: string | null;
  storage_path: string | null;
  author_id: string;
  created_at: string;
  updated_at: string;
  author?: User;
}

export interface PaginatedResponse<T> {
  data: T[];
  pagination: {
    page: number;
    per_page: number;
    total_items: number;
    total_pages: number;
  };
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
}

export interface ApiError {
  detail: string;
}

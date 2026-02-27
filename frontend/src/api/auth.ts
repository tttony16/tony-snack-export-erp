import request from '@/utils/request';
import type { TokenResponse, UserRead } from '@/types/models';

export async function login(username: string, password: string): Promise<TokenResponse> {
  return request.post('/auth/login', { username, password });
}

export async function logout(): Promise<void> {
  return request.post('/auth/logout');
}

export async function refreshToken(refresh_token: string): Promise<TokenResponse> {
  return request.post('/auth/refresh', { refresh_token });
}

export async function getCurrentUser(): Promise<UserRead> {
  return request.get('/auth/me');
}

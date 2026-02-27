import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';
import { message } from 'antd';

const request = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
});

// Request interceptor: attach Bearer token
request.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor: unwrap ApiResponse.data + handle 401 refresh
let isRefreshing = false;
let pendingRequests: Array<{
  resolve: (token: string) => void;
  reject: (err: unknown) => void;
}> = [];

function onRefreshed(token: string) {
  pendingRequests.forEach(({ resolve }) => resolve(token));
  pendingRequests = [];
}

function onRefreshFailed(err: unknown) {
  pendingRequests.forEach(({ reject }) => reject(err));
  pendingRequests = [];
}

request.interceptors.response.use(
  (response) => {
    const data = response.data;
    // Blob responses (file downloads) pass through
    if (response.config.responseType === 'blob') {
      return response;
    }
    // Standard ApiResponse wrapper
    if (data && typeof data === 'object' && 'code' in data) {
      if (data.code !== 0) {
        message.error(data.message || '请求失败');
        return Promise.reject(new Error(data.message));
      }
      return data.data;
    }
    return data;
  },
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      const refreshToken = localStorage.getItem('refresh_token');

      if (!refreshToken) {
        goToLogin();
        return Promise.reject(error);
      }

      if (isRefreshing) {
        // Queue this request until refresh completes
        return new Promise<string>((resolve, reject) => {
          pendingRequests.push({ resolve, reject });
        }).then((token) => {
          originalRequest.headers.Authorization = `Bearer ${token}`;
          return request(originalRequest);
        });
      }

      isRefreshing = true;
      try {
        const res = await axios.post('/api/v1/auth/refresh', {
          refresh_token: refreshToken,
        });
        const { access_token, refresh_token } = res.data.data;
        localStorage.setItem('access_token', access_token);
        localStorage.setItem('refresh_token', refresh_token);
        originalRequest.headers.Authorization = `Bearer ${access_token}`;
        onRefreshed(access_token);
        return request(originalRequest);
      } catch (refreshError) {
        onRefreshFailed(refreshError);
        goToLogin();
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    const msg =
      (error.response?.data as { message?: string })?.message ||
      error.message ||
      '网络错误';
    message.error(msg);
    return Promise.reject(error);
  },
);

function goToLogin() {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('user');
  if (window.location.pathname !== '/login') {
    window.location.href = '/login';
  }
}

export default request;

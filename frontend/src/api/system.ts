import request from '@/utils/request';
import type { PaginatedData } from '@/types/api';
import type {
  UserRead,
  SystemUserCreate,
  SystemUserUpdate,
  AuditLogRead,
  AuditLogListParams,
  SystemConfigRead,
  SystemConfigUpdate,
} from '@/types/models';

// User management
export async function listUsers(params: Record<string, unknown>): Promise<PaginatedData<UserRead>> {
  return request.get('/system/users', { params });
}

export async function getUser(id: string): Promise<UserRead> {
  return request.get(`/system/users/${id}`);
}

export async function createUser(data: SystemUserCreate): Promise<UserRead> {
  return request.post('/system/users', data);
}

export async function updateUser(id: string, data: SystemUserUpdate): Promise<UserRead> {
  return request.put(`/system/users/${id}`, data);
}

export async function updateUserRole(id: string, role: string): Promise<UserRead> {
  return request.patch(`/system/users/${id}/role`, { role });
}

export async function updateUserStatus(id: string, is_active: boolean): Promise<UserRead> {
  return request.patch(`/system/users/${id}/status`, { is_active });
}

// Audit logs
export async function listAuditLogs(params: AuditLogListParams): Promise<PaginatedData<AuditLogRead>> {
  return request.get('/system/audit-logs', { params });
}

// System configs
export async function listConfigs(): Promise<SystemConfigRead[]> {
  return request.get('/system/configs');
}

export async function updateConfig(key: string, data: SystemConfigUpdate): Promise<SystemConfigRead> {
  return request.put(`/system/configs/${key}`, data);
}

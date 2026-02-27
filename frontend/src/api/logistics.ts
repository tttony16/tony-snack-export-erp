import request from '@/utils/request';
import type { PaginatedData } from '@/types/api';
import type {
  LogisticsRecordRead,
  LogisticsRecordListRead,
  LogisticsRecordCreate,
  LogisticsRecordUpdate,
  LogisticsRecordListParams,
  LogisticsCostCreate,
  LogisticsCostRead,
  LogisticsCostUpdate,
  LogisticsKanbanResponse,
} from '@/types/models';

export async function listLogistics(params: LogisticsRecordListParams): Promise<PaginatedData<LogisticsRecordListRead>> {
  return request.get('/logistics', { params });
}

export async function getLogistics(id: string): Promise<LogisticsRecordRead> {
  return request.get(`/logistics/${id}`);
}

export async function createLogistics(data: LogisticsRecordCreate): Promise<LogisticsRecordRead> {
  return request.post('/logistics', data);
}

export async function updateLogistics(id: string, data: LogisticsRecordUpdate): Promise<LogisticsRecordRead> {
  return request.put(`/logistics/${id}`, data);
}

export async function updateLogisticsStatus(id: string, status: string): Promise<LogisticsRecordRead> {
  return request.patch(`/logistics/${id}/status`, { status });
}

export async function getLogisticsKanban(): Promise<LogisticsKanbanResponse> {
  return request.get('/logistics/kanban');
}

export async function addLogisticsCost(id: string, data: LogisticsCostCreate): Promise<LogisticsCostRead> {
  return request.post(`/logistics/${id}/costs`, data);
}

export async function updateLogisticsCost(id: string, costId: string, data: LogisticsCostUpdate): Promise<LogisticsCostRead> {
  return request.put(`/logistics/${id}/costs/${costId}`, data);
}

export async function deleteLogisticsCost(id: string, costId: string): Promise<void> {
  return request.delete(`/logistics/${id}/costs/${costId}`);
}

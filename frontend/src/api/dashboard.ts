import request from '@/utils/request';
import type {
  OverviewResponse,
  TodoResponse,
  InTransitResponse,
  ExpiryWarningResponse,
} from '@/types/models';

export async function getOverview(): Promise<OverviewResponse> {
  return request.get('/dashboard/overview');
}

export async function getTodos(): Promise<TodoResponse> {
  return request.get('/dashboard/todos');
}

export async function getInTransit(): Promise<InTransitResponse> {
  return request.get('/dashboard/in-transit');
}

export async function getExpiryWarnings(): Promise<ExpiryWarningResponse> {
  return request.get('/dashboard/expiry-warnings');
}

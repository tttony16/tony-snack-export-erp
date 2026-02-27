import request from '@/utils/request';
import type { PaginatedData } from '@/types/api';
import type {
  SalesOrderRead,
  SalesOrderListRead,
  SalesOrderCreate,
  SalesOrderUpdate,
  SalesOrderListParams,
  KanbanResponse,
} from '@/types/models';

export async function listSalesOrders(params: SalesOrderListParams): Promise<PaginatedData<SalesOrderListRead>> {
  return request.get('/sales-orders', { params });
}

export async function getSalesOrder(id: string): Promise<SalesOrderRead> {
  return request.get(`/sales-orders/${id}`);
}

export async function createSalesOrder(data: SalesOrderCreate): Promise<SalesOrderRead> {
  return request.post('/sales-orders', data);
}

export async function updateSalesOrder(id: string, data: SalesOrderUpdate): Promise<SalesOrderRead> {
  return request.put(`/sales-orders/${id}`, data);
}

export async function confirmSalesOrder(id: string): Promise<SalesOrderRead> {
  return request.post(`/sales-orders/${id}/confirm`);
}

export async function generatePurchaseOrder(id: string): Promise<unknown> {
  return request.post(`/sales-orders/${id}/generate-purchase`);
}

export async function getSalesOrderFulfillment(id: string): Promise<unknown> {
  return request.get(`/sales-orders/${id}/fulfillment`);
}

export async function updateSalesOrderStatus(id: string, status: string): Promise<SalesOrderRead> {
  return request.patch(`/sales-orders/${id}/status`, { status });
}

export async function getSalesOrderKanban(): Promise<KanbanResponse> {
  return request.get('/sales-orders/kanban');
}

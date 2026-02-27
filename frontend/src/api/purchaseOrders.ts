import request from '@/utils/request';
import type { PaginatedData } from '@/types/api';
import type {
  PurchaseOrderRead,
  PurchaseOrderListRead,
  PurchaseOrderCreate,
  PurchaseOrderUpdate,
  PurchaseOrderListParams,
  ReceivingNoteListRead,
} from '@/types/models';

export async function listPurchaseOrders(params: PurchaseOrderListParams): Promise<PaginatedData<PurchaseOrderListRead>> {
  return request.get('/purchase-orders', { params });
}

export async function getPurchaseOrder(id: string): Promise<PurchaseOrderRead> {
  return request.get(`/purchase-orders/${id}`);
}

export async function createPurchaseOrder(data: PurchaseOrderCreate): Promise<PurchaseOrderRead> {
  return request.post('/purchase-orders', data);
}

export async function updatePurchaseOrder(id: string, data: PurchaseOrderUpdate): Promise<PurchaseOrderRead> {
  return request.put(`/purchase-orders/${id}`, data);
}

export async function confirmPurchaseOrder(id: string): Promise<PurchaseOrderRead> {
  return request.post(`/purchase-orders/${id}/confirm`);
}

export async function cancelPurchaseOrder(id: string): Promise<PurchaseOrderRead> {
  return request.post(`/purchase-orders/${id}/cancel`);
}

export async function linkSalesOrders(id: string, salesOrderIds: string[]): Promise<PurchaseOrderRead> {
  return request.post(`/purchase-orders/${id}/link-sales-orders`, { sales_order_ids: salesOrderIds });
}

export async function getPurchaseOrderReceivingNotes(id: string): Promise<ReceivingNoteListRead[]> {
  return request.get(`/purchase-orders/${id}/receiving-notes`);
}

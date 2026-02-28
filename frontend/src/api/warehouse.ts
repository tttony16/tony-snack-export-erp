import request from '@/utils/request';
import type { PaginatedData } from '@/types/api';
import type {
  ReceivingNoteRead,
  ReceivingNoteListRead,
  ReceivingNoteCreate,
  ReceivingNoteUpdate,
  ReceivingNoteListParams,
  ReceivingNoteItemRead,
  InventoryByProductRead,
  InventoryByOrderRead,
  InventoryBatchRead,
  InventoryListParams,
  ReadinessCheckResponse,
} from '@/types/models';

// Receiving Notes
export async function listReceivingNotes(params: ReceivingNoteListParams): Promise<PaginatedData<ReceivingNoteListRead>> {
  return request.get('/warehouse/receiving-notes', { params });
}

export async function getReceivingNote(id: string): Promise<ReceivingNoteRead> {
  return request.get(`/warehouse/receiving-notes/${id}`);
}

export async function createReceivingNote(data: ReceivingNoteCreate): Promise<ReceivingNoteRead> {
  return request.post('/warehouse/receiving-notes', data);
}

export async function updateReceivingNote(id: string, data: ReceivingNoteUpdate): Promise<ReceivingNoteRead> {
  return request.put(`/warehouse/receiving-notes/${id}`, data);
}

// Inventory
export async function listInventory(params: InventoryListParams): Promise<PaginatedData<InventoryByProductRead>> {
  return request.get('/warehouse/inventory', { params });
}

export async function getInventoryByOrder(salesOrderId: string): Promise<InventoryByOrderRead[]> {
  return request.get('/warehouse/inventory/by-order', { params: { sales_order_id: salesOrderId } });
}

export async function checkReadiness(salesOrderId: string): Promise<ReadinessCheckResponse> {
  return request.get(`/warehouse/inventory/readiness/${salesOrderId}`);
}

// Inventory Batches
export async function listInventoryBatches(params: {
  product_id?: string;
  sales_order_id?: string;
  destination_port?: string;
  page?: number;
  page_size?: number;
}): Promise<InventoryBatchRead[]> {
  return request.get('/warehouse/inventory/batches', { params });
}

// Pending Inspection
export async function listPendingInspection(params: InventoryListParams): Promise<PaginatedData<ReceivingNoteItemRead>> {
  return request.get('/warehouse/inventory/pending-inspection', { params });
}

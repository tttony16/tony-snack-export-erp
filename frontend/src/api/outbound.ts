import request from '@/utils/request';
import type { PaginatedData } from '@/types/api';
import type {
  OutboundOrderRead,
  OutboundOrderListRead,
  OutboundOrderCreate,
  OutboundOrderConfirm,
  OutboundOrderListParams,
} from '@/types/models';

export async function listOutboundOrders(params: OutboundOrderListParams): Promise<PaginatedData<OutboundOrderListRead>> {
  return request.get('/outbound-orders', { params });
}

export async function getOutboundOrder(id: string): Promise<OutboundOrderRead> {
  return request.get(`/outbound-orders/${id}`);
}

export async function createOutboundOrder(data: OutboundOrderCreate): Promise<OutboundOrderRead> {
  return request.post('/outbound-orders', data);
}

export async function confirmOutboundOrder(id: string, data: OutboundOrderConfirm): Promise<OutboundOrderRead> {
  return request.post(`/outbound-orders/${id}/confirm`, data);
}

export async function cancelOutboundOrder(id: string): Promise<OutboundOrderRead> {
  return request.post(`/outbound-orders/${id}/cancel`);
}

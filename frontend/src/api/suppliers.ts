import request from '@/utils/request';
import type { PaginatedData } from '@/types/api';
import type {
  SupplierRead,
  SupplierCreate,
  SupplierUpdate,
  SupplierListParams,
  SupplierProductRead,
  SupplierProductCreate,
  PurchaseOrderListRead,
} from '@/types/models';

export async function listSuppliers(params: SupplierListParams): Promise<PaginatedData<SupplierRead>> {
  return request.get('/suppliers', { params });
}

export async function getSupplier(id: string): Promise<SupplierRead> {
  return request.get(`/suppliers/${id}`);
}

export async function createSupplier(data: SupplierCreate): Promise<SupplierRead> {
  return request.post('/suppliers', data);
}

export async function updateSupplier(id: string, data: SupplierUpdate): Promise<SupplierRead> {
  return request.put(`/suppliers/${id}`, data);
}

export async function getSupplierPOs(id: string): Promise<PurchaseOrderListRead[]> {
  return request.get(`/suppliers/${id}/purchase-orders`);
}

export async function addSupplierProduct(supplierId: string, data: SupplierProductCreate): Promise<SupplierProductRead> {
  return request.post(`/suppliers/${supplierId}/products`, data);
}

export async function removeSupplierProduct(supplierId: string, productId: string): Promise<void> {
  return request.delete(`/suppliers/${supplierId}/products/${productId}`);
}

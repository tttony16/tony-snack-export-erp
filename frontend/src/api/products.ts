import request from '@/utils/request';
import type { PaginatedData } from '@/types/api';
import type { ProductRead, ProductCreate, ProductUpdate, ProductListParams } from '@/types/models';

export async function listProducts(params: ProductListParams): Promise<PaginatedData<ProductRead>> {
  return request.get('/products', { params });
}

export async function getProduct(id: string): Promise<ProductRead> {
  return request.get(`/products/${id}`);
}

export async function createProduct(data: ProductCreate): Promise<ProductRead> {
  return request.post('/products', data);
}

export async function updateProduct(id: string, data: ProductUpdate): Promise<ProductRead> {
  return request.put(`/products/${id}`, data);
}

export async function updateProductStatus(id: string, status: string): Promise<ProductRead> {
  return request.patch(`/products/${id}/status`, { status });
}

export async function importProducts(file: File): Promise<unknown> {
  const formData = new FormData();
  formData.append('file', file);
  return request.post('/products/import', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
}

export async function exportProducts(): Promise<void> {
  // handled via download util
}

export async function getProductTemplate(): Promise<void> {
  // handled via download util
}

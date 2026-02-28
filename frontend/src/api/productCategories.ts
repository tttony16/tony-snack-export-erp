import request from '@/utils/request';
import type { ProductCategoryTreeNode, ProductCategoryRead } from '@/types/models';

export async function getCategoryTree(): Promise<ProductCategoryTreeNode[]> {
  return request.get('/product-categories/tree');
}

export async function getCategoryChildren(id: string): Promise<ProductCategoryRead[]> {
  return request.get(`/product-categories/${id}/children`);
}

export async function createCategory(data: {
  name: string;
  parent_id?: string;
  sort_order?: number;
}): Promise<ProductCategoryRead> {
  return request.post('/product-categories', data);
}

export async function updateCategory(
  id: string,
  data: { name?: string; sort_order?: number },
): Promise<ProductCategoryRead> {
  return request.put(`/product-categories/${id}`, data);
}

export async function deleteCategory(id: string): Promise<void> {
  return request.delete(`/product-categories/${id}`);
}

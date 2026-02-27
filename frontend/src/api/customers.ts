import request from '@/utils/request';
import type { PaginatedData } from '@/types/api';
import type { CustomerRead, CustomerCreate, CustomerUpdate, CustomerListParams, SalesOrderListRead } from '@/types/models';

export async function listCustomers(params: CustomerListParams): Promise<PaginatedData<CustomerRead>> {
  return request.get('/customers', { params });
}

export async function getCustomer(id: string): Promise<CustomerRead> {
  return request.get(`/customers/${id}`);
}

export async function createCustomer(data: CustomerCreate): Promise<CustomerRead> {
  return request.post('/customers', data);
}

export async function updateCustomer(id: string, data: CustomerUpdate): Promise<CustomerRead> {
  return request.put(`/customers/${id}`, data);
}

export async function getCustomerOrders(id: string): Promise<SalesOrderListRead[]> {
  return request.get(`/customers/${id}/orders`);
}

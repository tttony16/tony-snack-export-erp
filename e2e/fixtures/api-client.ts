import { request, type APIRequestContext } from '@playwright/test';

const API_BASE = process.env.API_URL || 'http://localhost:8000';
const API_PREFIX = '/api/v1';

export class ApiClient {
  private token = '';
  private ctx!: APIRequestContext;

  static async create(username: string, password: string): Promise<ApiClient> {
    const client = new ApiClient();
    client.ctx = await request.newContext({ baseURL: API_BASE });
    await client.login(username, password);
    return client;
  }

  private async login(username: string, password: string) {
    const res = await this.ctx.post(`${API_PREFIX}/auth/login`, {
      data: { username, password },
    });
    if (!res.ok()) throw new Error(`Login failed: ${res.status()}`);
    const body = await res.json();
    this.token = body.data?.access_token ?? body.access_token;
  }

  private headers() {
    return { Authorization: `Bearer ${this.token}` };
  }

  private async post(path: string, data?: unknown) {
    const res = await this.ctx.post(`${API_PREFIX}${path}`, {
      data,
      headers: this.headers(),
    });
    if (!res.ok()) {
      const text = await res.text();
      throw new Error(`POST ${path} failed (${res.status()}): ${text}`);
    }
    return (await res.json()).data;
  }

  private async get(path: string, params?: Record<string, string>) {
    const res = await this.ctx.get(`${API_PREFIX}${path}`, {
      params,
      headers: this.headers(),
    });
    if (!res.ok()) {
      const text = await res.text();
      throw new Error(`GET ${path} failed (${res.status()}): ${text}`);
    }
    return (await res.json()).data;
  }

  private async put(path: string, data?: unknown) {
    const res = await this.ctx.put(`${API_PREFIX}${path}`, {
      data,
      headers: this.headers(),
    });
    if (!res.ok()) {
      const text = await res.text();
      throw new Error(`PUT ${path} failed (${res.status()}): ${text}`);
    }
    return (await res.json()).data;
  }

  private async patch(path: string, data?: unknown) {
    const res = await this.ctx.patch(`${API_PREFIX}${path}`, {
      data,
      headers: this.headers(),
    });
    if (!res.ok()) {
      const text = await res.text();
      throw new Error(`PATCH ${path} failed (${res.status()}): ${text}`);
    }
    return (await res.json()).data;
  }

  private async del(path: string) {
    const res = await this.ctx.delete(`${API_PREFIX}${path}`, {
      headers: this.headers(),
    });
    if (!res.ok() && res.status() !== 204) {
      const text = await res.text();
      throw new Error(`DELETE ${path} failed (${res.status()}): ${text}`);
    }
  }

  // --- Products ---
  async createProduct(data: Record<string, unknown>) {
    return this.post('/products', data);
  }

  async getProduct(id: string) {
    return this.get(`/products/${id}`);
  }

  async updateProduct(id: string, data: Record<string, unknown>) {
    return this.put(`/products/${id}`, data);
  }

  async updateProductStatus(id: string, status: string) {
    return this.patch(`/products/${id}/status`, { status });
  }

  async listProducts(params?: Record<string, string>) {
    return this.get('/products', params);
  }

  // --- Customers ---
  async createCustomer(data: Record<string, unknown>) {
    return this.post('/customers', data);
  }

  async getCustomer(id: string) {
    return this.get(`/customers/${id}`);
  }

  async updateCustomer(id: string, data: Record<string, unknown>) {
    return this.put(`/customers/${id}`, data);
  }

  async listCustomers(params?: Record<string, string>) {
    return this.get('/customers', params);
  }

  // --- Suppliers ---
  async createSupplier(data: Record<string, unknown>) {
    return this.post('/suppliers', data);
  }

  async getSupplier(id: string) {
    return this.get(`/suppliers/${id}`);
  }

  async updateSupplier(id: string, data: Record<string, unknown>) {
    return this.put(`/suppliers/${id}`, data);
  }

  async addSupplierProduct(supplierId: string, data: Record<string, unknown>) {
    return this.post(`/suppliers/${supplierId}/products`, data);
  }

  // --- Sales Orders ---
  async createSalesOrder(data: Record<string, unknown>) {
    return this.post('/sales-orders', data);
  }

  async getSalesOrder(id: string) {
    return this.get(`/sales-orders/${id}`);
  }

  async updateSalesOrder(id: string, data: Record<string, unknown>) {
    return this.put(`/sales-orders/${id}`, data);
  }

  async confirmSalesOrder(id: string) {
    return this.post(`/sales-orders/${id}/confirm`);
  }

  async generatePurchaseOrders(soId: string) {
    return this.post(`/sales-orders/${soId}/generate-purchase`);
  }

  async updateSalesOrderStatus(id: string, status: string) {
    return this.patch(`/sales-orders/${id}/status`, { status });
  }

  // --- Purchase Orders ---
  async createPurchaseOrder(data: Record<string, unknown>) {
    return this.post('/purchase-orders', data);
  }

  async getPurchaseOrder(id: string) {
    return this.get(`/purchase-orders/${id}`);
  }

  async confirmPurchaseOrder(id: string) {
    return this.post(`/purchase-orders/${id}/confirm`);
  }

  async cancelPurchaseOrder(id: string) {
    return this.post(`/purchase-orders/${id}/cancel`);
  }

  async listPurchaseOrders(params?: Record<string, string>) {
    return this.get('/purchase-orders', params);
  }

  // --- Warehouse ---
  async createReceivingNote(data: Record<string, unknown>) {
    return this.post('/warehouse/receiving-notes', data);
  }

  async getReceivingNote(id: string) {
    return this.get(`/warehouse/receiving-notes/${id}`);
  }

  async listReceivingNotes(params?: Record<string, string>) {
    return this.get('/warehouse/receiving-notes', params);
  }

  async getInventoryByOrder(salesOrderId: string) {
    return this.get('/warehouse/inventory/by-order', { sales_order_id: salesOrderId });
  }

  async checkReadiness(salesOrderId: string) {
    return this.get(`/warehouse/inventory/readiness/${salesOrderId}`);
  }

  // --- Containers ---
  async createContainerPlan(data: Record<string, unknown>) {
    return this.post('/containers', data);
  }

  async getContainerPlan(id: string) {
    return this.get(`/containers/${id}`);
  }

  async listContainerPlans(params?: Record<string, string>) {
    return this.get('/containers', params);
  }

  async validateContainerPlan(id: string) {
    return this.post(`/containers/${id}/validate`);
  }

  async confirmContainerPlan(id: string) {
    return this.post(`/containers/${id}/confirm`);
  }

  async getContainerSummary(id: string) {
    return this.get(`/containers/${id}/summary`);
  }

  // --- Logistics ---
  async createLogistics(data: Record<string, unknown>) {
    return this.post('/logistics', data);
  }

  async getLogistics(id: string) {
    return this.get(`/logistics/${id}`);
  }

  async advanceLogisticsStatus(id: string, status: string) {
    return this.patch(`/logistics/${id}/status`, { status });
  }

  async addLogisticsCost(id: string, data: Record<string, unknown>) {
    return this.post(`/logistics/${id}/costs`, data);
  }

  async deleteLogisticsCost(logisticsId: string, costId: string) {
    return this.del(`/logistics/${logisticsId}/costs/${costId}`);
  }

  // --- System ---
  async createUser(data: Record<string, unknown>) {
    return this.post('/system/users', data);
  }

  async listUsers(params?: Record<string, string>) {
    return this.get('/system/users', params);
  }

  async updateUserRole(userId: string, role: string) {
    return this.patch(`/system/users/${userId}/role`, { role });
  }

  async updateUserStatus(userId: string, isActive: boolean) {
    return this.patch(`/system/users/${userId}/status`, { is_active: isActive });
  }

  // --- Dashboard ---
  async getDashboardTodos() {
    return this.get('/dashboard/todos');
  }

  async getDashboardInTransit() {
    return this.get('/dashboard/in-transit');
  }

  async dispose() {
    await this.ctx.dispose();
  }
}

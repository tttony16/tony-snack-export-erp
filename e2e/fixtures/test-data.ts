function uid(): string {
  return `${Date.now()}-${Math.random().toString(36).slice(2, 7)}`;
}

export function makeProduct(overrides?: Record<string, unknown>) {
  const id = uid();
  return {
    sku_code: `SKU-E2E-${id}`,
    name_cn: `测试商品-${id}`,
    name_en: `Test Product ${id}`,
    category_id: '', // Must be set to a valid level-3 category UUID
    brand: 'E2E Brand',
    spec: '500g/袋',
    packing_spec: '20袋/箱',
    unit_weight_kg: 0.5,
    unit_volume_cbm: 0.001,
    carton_length_cm: 40,
    carton_width_cm: 30,
    carton_height_cm: 20,
    carton_gross_weight_kg: 10.5,
    shelf_life_days: 365,
    ...overrides,
  };
}

export function makeCustomer(overrides?: Record<string, unknown>) {
  const id = uid();
  return {
    name: `E2E客户-${id}`,
    country: 'Thailand',
    contact_person: `Contact ${id}`,
    phone: '1234567890',
    email: `e2e-${id}@test.com`,
    currency: 'USD',
    payment_method: 'TT',
    ...overrides,
  };
}

export function makeSupplier(overrides?: Record<string, unknown>) {
  const id = uid();
  return {
    name: `E2E供应商-${id}`,
    contact_person: `供应联系人-${id}`,
    phone: '13800138000',
    supply_categories: [] as string[], // Must be set to level-1 category UUIDs
    ...overrides,
  };
}

export function makeSalesOrder(
  customerId: string,
  items: { product_id: string; quantity: number; unit_price: number }[],
  overrides?: Record<string, unknown>,
) {
  return {
    customer_id: customerId,
    order_date: new Date().toISOString().split('T')[0],
    destination_port: 'Bangkok',
    trade_term: 'FOB',
    currency: 'USD',
    payment_method: 'TT',
    items: items.map((item) => ({
      product_id: item.product_id,
      quantity: item.quantity,
      unit: 'carton',
      unit_price: item.unit_price,
    })),
    ...overrides,
  };
}

export function makePurchaseOrder(
  supplierId: string,
  items: { product_id: string; quantity: number; unit_price: number; sales_order_item_id?: string }[],
  overrides?: Record<string, unknown>,
) {
  return {
    supplier_id: supplierId,
    order_date: new Date().toISOString().split('T')[0],
    items: items.map((item) => ({
      product_id: item.product_id,
      quantity: item.quantity,
      unit: 'carton',
      unit_price: item.unit_price,
      sales_order_item_id: item.sales_order_item_id,
    })),
    ...overrides,
  };
}

export function makeReceivingNote(
  purchaseOrderId: string,
  items: {
    purchase_order_item_id: string;
    product_id: string;
    quantity: number;
    inspection_result?: string;
  }[],
  overrides?: Record<string, unknown>,
) {
  return {
    purchase_order_id: purchaseOrderId,
    receiving_date: new Date().toISOString().split('T')[0],
    receiver: 'E2E Tester',
    items: items.map((item) => ({
      purchase_order_item_id: item.purchase_order_item_id,
      product_id: item.product_id,
      expected_quantity: item.quantity,
      actual_quantity: item.quantity,
      inspection_result: item.inspection_result || 'passed',
      failed_quantity: 0,
      production_date: new Date().toISOString().split('T')[0],
    })),
    ...overrides,
  };
}

export function makeContainerPlan(
  salesOrderIds?: string[],
  overrides?: Record<string, unknown>,
) {
  return {
    sales_order_ids: salesOrderIds || [],
    container_type: '40HQ',
    container_count: 1,
    destination_port: 'Bangkok',
    ...overrides,
  };
}

export function makeOutboundOrder(
  containerPlanId: string,
  overrides?: Record<string, unknown>,
) {
  return {
    container_plan_id: containerPlanId,
    ...overrides,
  };
}

export function makeOutboundConfirm(overrides?: Record<string, unknown>) {
  return {
    outbound_date: new Date().toISOString().split('T')[0],
    operator: 'E2E Tester',
    ...overrides,
  };
}

export function makeLogistics(
  containerPlanId: string,
  overrides?: Record<string, unknown>,
) {
  return {
    container_plan_id: containerPlanId,
    shipping_company: 'COSCO',
    vessel_voyage: `E2E-VESSEL-${uid()}`,
    port_of_loading: '上海',
    port_of_discharge: 'Bangkok',
    etd: new Date().toISOString().split('T')[0],
    ...overrides,
  };
}

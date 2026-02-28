import { test, expect } from '../fixtures/auth';
import {
  makeProduct,
  makeCustomer,
  makeSupplier,
  makeSalesOrder,
  makeReceivingNote,
} from '../fixtures/test-data';
import { waitForTableLoaded } from '../helpers/ant-helpers';
import { ApiClient } from '../fixtures/api-client';

test.describe('Inventory Module', () => {
  let soId: string;

  test.beforeAll(async () => {
    const api = await ApiClient.create('admin', 'admin123');

    // Create full chain to receiving note so inventory exists
    const product = makeProduct();
    const customer = makeCustomer();
    const supplier = makeSupplier();

    const pResult = await api.createProduct(product);
    const cResult = await api.createCustomer(customer);
    const sResult = await api.createSupplier(supplier);
    await api.updateProduct(pResult.id, { default_supplier_id: sResult.id });

    const so = makeSalesOrder(cResult.id, [{ product_id: pResult.id, quantity: 100, unit_price: 10 }]);
    const soResult = await api.createSalesOrder(so);
    soId = soResult.id;
    await api.confirmSalesOrder(soResult.id);
    await api.generatePurchaseOrders(soResult.id);

    const poList = await api.listPurchaseOrders({ page_size: '5', sort_order: 'desc' });
    const po = (poList.items || poList)[0];
    await api.confirmPurchaseOrder(po.id);

    // Get PO details for item IDs
    const poDetail = await api.getPurchaseOrder(po.id);
    const poItems = poDetail.items || [];

    // Create receiving note
    const rnItems = poItems.map((item: { id: string; product_id: string; quantity: number }) => ({
      purchase_order_item_id: item.id,
      product_id: item.product_id,
      quantity: item.quantity,
    }));
    const rn = makeReceivingNote(po.id, rnItems);
    await api.createReceivingNote(rn);

    await api.dispose();
  });

  test('by-product summary tab loads', async ({ adminPage }) => {
    await adminPage.goto('/warehouse/inventory');
    await expect(adminPage.getByRole('tab', { name: '按商品汇总' })).toBeVisible();
    await adminPage.getByRole('tab', { name: '按商品汇总' }).click();
    await adminPage.waitForTimeout(1000);
    // Use the active tabpanel's table to avoid hidden tables from other tabs
    await expect(adminPage.locator('.ant-tabs-tabpane-active .ant-table, [role="tabpanel"][class*="active"] .ant-table').first()).toBeVisible();
  });

  test('by-order tab: select SO and query inventory', async ({ adminPage }) => {
    await adminPage.goto('/warehouse/inventory');
    await adminPage.getByRole('tab', { name: '按订单查看' }).click();
    await adminPage.waitForTimeout(1000);

    // Select the sales order - Ant Select uses a span for placeholder, not input attribute
    const soSelect = adminPage.locator('.ant-select').filter({ hasText: '选择销售订单' }).first();
    await expect(soSelect).toBeVisible();

    await soSelect.click();
    await adminPage.waitForTimeout(500);
    // Select first available option
    const dropdown = adminPage.locator('.ant-select-dropdown:visible');
    await dropdown.locator('.ant-select-item').first().click();

    await adminPage.getByRole('button', { name: '查 询' }).click();
    await adminPage.waitForTimeout(2000);

    // Verify the query completed - table or empty state in the active tab
    const activePanel = adminPage.locator('.ant-tabs-tabpane-active');
    await expect(
      activePanel.locator('.ant-table-row').first().or(adminPage.getByText('暂无数据')),
    ).toBeVisible({ timeout: 10000 });
  });

  test('readiness check shows result alert', async ({ adminPage }) => {
    await adminPage.goto('/warehouse/inventory');
    await adminPage.getByRole('tab', { name: '按订单查看' }).click();
    await adminPage.waitForTimeout(1000);

    const soSelect = adminPage.locator('.ant-select').filter({ hasText: '选择销售订单' }).first();
    await soSelect.click();
    await adminPage.waitForTimeout(500);
    const dropdown = adminPage.locator('.ant-select-dropdown:visible');
    await dropdown.locator('.ant-select-item').first().click();

    await adminPage.getByRole('button', { name: '齐货检查' }).click();
    await adminPage.waitForTimeout(1000);

    // Should show an alert with readiness result
    await expect(adminPage.locator('.ant-alert').or(adminPage.locator('.ant-message'))).toBeVisible({ timeout: 10000 });
  });

  test('pending inspection tab loads', async ({ adminPage }) => {
    await adminPage.goto('/warehouse/inventory');
    await adminPage.getByRole('tab', { name: '待验货' }).click();
    await adminPage.waitForTimeout(1000);
    // Target the active tab panel to avoid hidden tables from other tabs
    const activePanel = adminPage.locator('.ant-tabs-tabpane-active');
    await expect(activePanel.locator('.ant-table').first()).toBeVisible();
  });

  test('tab switching works correctly', async ({ adminPage }) => {
    await adminPage.goto('/warehouse/inventory');

    // Switch to each tab and verify content
    await adminPage.getByRole('tab', { name: '按商品汇总' }).click();
    await adminPage.waitForTimeout(1000);
    await expect(adminPage.locator('.ant-tabs-tabpane-active .ant-table').first()).toBeVisible();

    await adminPage.getByRole('tab', { name: '按订单查看' }).click();
    await adminPage.waitForTimeout(1000);
    await expect(adminPage.locator('.ant-select').filter({ hasText: '选择销售订单' }).first()).toBeVisible();

    await adminPage.getByRole('tab', { name: '待验货' }).click();
    await adminPage.waitForTimeout(1000);
    await expect(adminPage.locator('.ant-tabs-tabpane-active .ant-table').first()).toBeVisible();
  });
});

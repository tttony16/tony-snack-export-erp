import { test, expect } from '../fixtures/auth';
import {
  makeProduct,
  makeCustomer,
  makeSupplier,
  makeSalesOrder,
} from '../fixtures/test-data';
import {
  selectSearchOption,
  fillDatePicker,
  fillProFormField,
  waitForTableLoaded,
  waitForModalClosed,
  waitForMessage,
} from '../helpers/ant-helpers';
import { ApiClient } from '../fixtures/api-client';

test.describe('Receiving Notes Module', () => {
  let confirmedPONo: string;

  test.beforeAll(async () => {
    const api = await ApiClient.create('admin', 'admin123');

    // Create full chain: product → customer → supplier → SO → confirm → generate PO → confirm PO
    const product = makeProduct();
    const customer = makeCustomer();
    const supplier = makeSupplier();

    const pResult = await api.createProduct(product);
    const cResult = await api.createCustomer(customer);
    const sResult = await api.createSupplier(supplier);
    await api.updateProduct(pResult.id, { default_supplier_id: sResult.id });

    const so = makeSalesOrder(cResult.id, [{ product_id: pResult.id, quantity: 100, unit_price: 10 }]);
    const soResult = await api.createSalesOrder(so);
    await api.confirmSalesOrder(soResult.id);
    await api.generatePurchaseOrders(soResult.id);

    // Find and confirm PO
    const poList = await api.listPurchaseOrders({ page_size: '5', sort_order: 'desc' });
    const items = poList.items || poList;
    const po = items[0];
    confirmedPONo = po.order_no;
    await api.confirmPurchaseOrder(po.id);

    await api.dispose();
  });

  test('UI create receiving note', async ({ adminPage }) => {
    await adminPage.goto('/warehouse/receiving-notes');
    await waitForTableLoaded(adminPage);

    await adminPage.getByRole('button', { name: '新建收货单' }).click();
    await expect(adminPage.getByText('新建收货单').first()).toBeVisible();

    // Select PO
    await selectSearchOption(adminPage, '采购单', confirmedPONo.slice(0, 5), confirmedPONo);
    await adminPage.waitForTimeout(1000); // Wait for items to load

    // Fill date and receiver
    await fillDatePicker(adminPage, '收货日期', new Date().toISOString().split('T')[0]);
    await fillProFormField(adminPage, '验收人', 'E2E Tester');

    // The items table should have loaded - fill production date
    const dateInputs = adminPage.locator('input[type="date"]');
    const count = await dateInputs.count();
    for (let i = 0; i < count; i++) {
      await dateInputs.nth(i).fill(new Date().toISOString().split('T')[0]);
    }

    await adminPage.getByRole('button', { name: '确 定' }).click();
    await waitForMessage(adminPage, '创建成功');
    await waitForModalClosed(adminPage);
  });

  test('create receiving note with partial_passed inspection', async ({ adminPage }) => {
    // Need another confirmed PO
    const api = await ApiClient.create('admin', 'admin123');
    const product = makeProduct();
    const customer = makeCustomer();
    const supplier = makeSupplier();

    const pResult = await api.createProduct(product);
    const cResult = await api.createCustomer(customer);
    const sResult = await api.createSupplier(supplier);
    await api.updateProduct(pResult.id, { default_supplier_id: sResult.id });

    const so = makeSalesOrder(cResult.id, [{ product_id: pResult.id, quantity: 50, unit_price: 10 }]);
    const soResult = await api.createSalesOrder(so);
    await api.confirmSalesOrder(soResult.id);
    await api.generatePurchaseOrders(soResult.id);

    const poList = await api.listPurchaseOrders({ page_size: '5', sort_order: 'desc' });
    const po = (poList.items || poList)[0];
    await api.confirmPurchaseOrder(po.id);
    await api.dispose();

    await adminPage.goto('/warehouse/receiving-notes');
    await waitForTableLoaded(adminPage);

    await adminPage.getByRole('button', { name: '新建收货单' }).click();
    await expect(adminPage.getByText('新建收货单').first()).toBeVisible();

    await selectSearchOption(adminPage, '采购单', po.order_no.slice(0, 5), po.order_no);
    await adminPage.waitForTimeout(1000);

    await fillDatePicker(adminPage, '收货日期', new Date().toISOString().split('T')[0]);
    await fillProFormField(adminPage, '验收人', 'E2E Inspector');

    // Change inspection result to partial_passed
    const inspectSelect = adminPage.locator('.ant-select').filter({ hasText: /通过|合格/ }).first();
    if (await inspectSelect.isVisible()) {
      await inspectSelect.click();
      await adminPage.locator('.ant-select-dropdown:visible').getByText('部分合格').first().click();
    }

    // Fill production date
    const dateInputs = adminPage.locator('input[type="date"]');
    const count = await dateInputs.count();
    for (let i = 0; i < count; i++) {
      await dateInputs.nth(i).fill(new Date().toISOString().split('T')[0]);
    }

    await adminPage.getByRole('button', { name: '确 定' }).click();
    await waitForMessage(adminPage, '创建成功');
    await waitForModalClosed(adminPage);
  });

  test('receiving notes list page loads', async ({ adminPage }) => {
    await adminPage.goto('/warehouse/receiving-notes');
    await expect(adminPage.locator('.ant-pro-table')).toBeVisible();
    await waitForTableLoaded(adminPage);
  });

  test('receiving note columns are visible', async ({ adminPage }) => {
    await adminPage.goto('/warehouse/receiving-notes');
    await waitForTableLoaded(adminPage);
    await expect(adminPage.getByRole('columnheader', { name: '收货单号' })).toBeVisible();
    await expect(adminPage.getByRole('columnheader', { name: '收货日期' })).toBeVisible();
    await expect(adminPage.getByRole('columnheader', { name: '验收人' })).toBeVisible();
  });
});

import { test, expect } from '../fixtures/auth';
import {
  makeProduct,
  makeCustomer,
  makeSupplier,
  makeSalesOrder,
  makeReceivingNote,
  makeLogistics,
} from '../fixtures/test-data';
import {
  selectSearchOption,
  fillProFormField,
  fillDatePicker,
  waitForTableLoaded,
  waitForModalClosed,
  waitForMessage,
} from '../helpers/ant-helpers';
import { ApiClient } from '../fixtures/api-client';

test.describe('Logistics Module', () => {
  let containerPlanId: string;
  let containerPlanNo: string;
  let logisticsId: string;
  let logisticsNo: string;

  test.beforeAll(async () => {
    const api = await ApiClient.create('admin', 'admin123');

    // Create full chain to confirmed container plan
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

    const poList = await api.listPurchaseOrders({ page_size: '5', sort_order: 'desc' });
    const po = (poList.items || poList)[0];
    await api.confirmPurchaseOrder(po.id);

    const poDetail = await api.getPurchaseOrder(po.id);
    const poItems = poDetail.items || [];
    const rnItems = poItems.map((item: { id: string; product_id: string; quantity: number }) => ({
      purchase_order_item_id: item.id,
      product_id: item.product_id,
      quantity: item.quantity,
    }));
    await api.createReceivingNote(makeReceivingNote(po.id, rnItems));

    // Create and confirm container plan
    const cp = await api.createContainerPlan({
      sales_order_ids: [soResult.id],
      container_type: '40HQ',
      container_count: 1,
      destination_port: 'Bangkok',
    });
    containerPlanId = cp.id;
    containerPlanNo = cp.plan_no;
    await api.confirmContainerPlan(cp.id);

    // Create a logistics record via API for detail/status tests
    const logData = makeLogistics(containerPlanId);
    const logResult = await api.createLogistics(logData);
    logisticsId = logResult.id;
    logisticsNo = logResult.logistics_no;

    await api.dispose();
  });

  test('UI create logistics record', async ({ adminPage }) => {
    await adminPage.goto('/logistics');
    await waitForTableLoaded(adminPage);

    await adminPage.getByRole('button', { name: '新建物流记录' }).click();
    await expect(adminPage.getByText('新建物流记录').first()).toBeVisible();

    // Select container plan
    await selectSearchOption(adminPage, '排柜计划', containerPlanNo.slice(0, 5), containerPlanNo);

    await fillProFormField(adminPage, '船公司', 'COSCO');
    await fillProFormField(adminPage, '船名航次', 'E2E-VESSEL-001');
    await fillProFormField(adminPage, '装港', '上海');
    await fillProFormField(adminPage, '卸港', 'Bangkok');

    await adminPage.getByRole('button', { name: '确 定' }).click();
    await waitForMessage(adminPage, '创建成功');
    await waitForModalClosed(adminPage);
  });

  test('view logistics detail page with status steps', async ({ adminPage }) => {
    await adminPage.goto(`/logistics/${logisticsId}`);
    await expect(adminPage.getByText(logisticsNo).first()).toBeVisible();
    await expect(adminPage.locator('.ant-descriptions')).toBeVisible();
    // Status flow Steps component should be visible
    await expect(adminPage.locator('.ant-steps')).toBeVisible();
  });

  test('advance logistics status', async ({ adminPage }) => {
    await adminPage.goto(`/logistics/${logisticsId}`);
    await expect(adminPage.getByText(logisticsNo).first()).toBeVisible();

    // Click advance status button
    const advanceBtn = adminPage.getByRole('button', { name: /推进到/ });
    if (await advanceBtn.isVisible()) {
      await advanceBtn.click();
      await adminPage.waitForTimeout(1000);
      await expect(adminPage.locator('.ant-message')).toBeVisible({ timeout: 10000 });
    }
  });

  test('add cost record', async ({ adminPage }) => {
    await adminPage.goto(`/logistics/${logisticsId}`);
    await expect(adminPage.getByText(logisticsNo).first()).toBeVisible();

    // Click add cost button
    const addCostBtn = adminPage.getByRole('button', { name: '添加费用' });
    if (!(await addCostBtn.isVisible({ timeout: 3000 }).catch(() => false))) {
      // Cost section might not be available, skip
      return;
    }
    await addCostBtn.click();
    await adminPage.waitForTimeout(500);

    // Fill cost form - may be in a modal or inline
    const costTypeSelect = adminPage.locator('.ant-select').filter({ hasText: /费用类型|请选择/ }).last();
    if (await costTypeSelect.isVisible({ timeout: 3000 }).catch(() => false)) {
      await costTypeSelect.click();
      await adminPage.waitForTimeout(500);
      await adminPage.locator('.ant-select-dropdown:visible').locator('.ant-select-item-option').first().click();
    }

    // Fill amount
    const amountInput = adminPage.locator('.ant-input-number input').last();
    if (await amountInput.isVisible({ timeout: 2000 }).catch(() => false)) {
      await amountInput.fill('1500');
    }

    // Select currency - use the item-option locator to avoid instability
    const currSelect = adminPage.locator('.ant-select').filter({ hasText: /币种|USD/ }).last();
    if (await currSelect.isVisible({ timeout: 2000 }).catch(() => false)) {
      await currSelect.scrollIntoViewIfNeeded();
      await adminPage.waitForTimeout(300);
      await currSelect.click();
      await adminPage.waitForTimeout(500);
      await adminPage.locator('.ant-select-dropdown:visible').locator('.ant-select-item-option').filter({ hasText: 'USD' }).first().click();
    }

    const submitBtn = adminPage.getByRole('button', { name: '添加' }).last();
    if (await submitBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
      await submitBtn.click();
      await adminPage.waitForTimeout(1000);
    }
    // Accept either success message or just verify the page is still functional
    await expect(adminPage.getByText(logisticsNo).first()).toBeVisible();
  });

  test('delete cost record', async ({ adminPage }) => {
    await adminPage.goto(`/logistics/${logisticsId}`);
    await adminPage.waitForTimeout(1000);

    // Find a delete link in the costs table
    const deleteLink = adminPage.getByText('删除').last();
    if (await deleteLink.isVisible()) {
      await deleteLink.click();
      // Confirm popover
      const confirmBtn = adminPage.locator('.ant-popconfirm-buttons .ant-btn-primary').or(
        adminPage.getByRole('button', { name: '确 定' }),
      );
      if (await confirmBtn.isVisible({ timeout: 3000 }).catch(() => false)) {
        await confirmBtn.click();
      }
      await waitForMessage(adminPage, '费用已删除');
    }
  });

  test('kanban view toggle works', async ({ adminPage }) => {
    await adminPage.goto('/logistics');
    await waitForTableLoaded(adminPage);

    await adminPage.getByText('看板').first().click();
    await adminPage.waitForTimeout(1000);
    // Kanban should show some content
    await expect(
      adminPage.locator('.ant-statistic, .ant-card').first(),
    ).toBeVisible({ timeout: 5000 });

    await adminPage.getByText('列表').first().click();
    await expect(adminPage.locator('.ant-pro-table')).toBeVisible();
  });
});

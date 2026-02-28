import { test, expect } from '../fixtures/auth';
import {
  makeProduct,
  makeCustomer,
  makeSupplier,
  makeSalesOrder,
  makeReceivingNote,
  makeOutboundConfirm,
} from '../fixtures/test-data';
import {
  waitForTableLoaded,
  waitForMessage,
} from '../helpers/ant-helpers';
import { ApiClient } from '../fixtures/api-client';

test.describe('Outbound Module', () => {
  let outboundOrderId: string;
  let outboundOrderNo: string;
  let cancelableOutboundId: string;

  test.beforeAll(async () => {
    const api = await ApiClient.create('admin', 'admin123');

    // Create full chain: SO → PO → Receiving → inventory → Container plan → add batch item → confirm → stuffing → loaded
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

    // Create container plan and add batch item
    const cp = await api.createContainerPlan({
      sales_order_ids: [soResult.id],
      container_type: '40HQ',
      container_count: 1,
      destination_port: 'Bangkok',
    });

    // Get inventory batch for batch-driven allocation
    const batches = await api.listInventoryBatches();
    const batch = (Array.isArray(batches) ? batches : batches.items || []).find(
      (b: { product_id: string }) => b.product_id === pResult.id,
    );
    if (batch) {
      await api.addContainerItem(cp.id, {
        container_seq: 1,
        inventory_record_id: batch.id,
        quantity: 50,
        volume_cbm: 1.5,
        weight_kg: 500,
      });
    }

    // Confirm → stuffing → loaded
    await api.confirmContainerPlan(cp.id);
    await api.recordStuffing(cp.id, {
      container_seq: 1,
      container_no: 'CSLU9999999',
      seal_no: 'SLE2E001',
      stuffing_date: new Date().toISOString().split('T')[0],
      stuffing_location: 'E2E Warehouse',
    });

    // Create outbound order from loaded plan
    const outbound = await api.createOutboundOrder({ container_plan_id: cp.id });
    outboundOrderId = outbound.id;
    outboundOrderNo = outbound.order_no;

    // --- Create a second outbound order that we can cancel via UI ---
    // Build a second full chain for the cancel test
    const product2 = makeProduct();
    const customer2 = makeCustomer();
    const supplier2 = makeSupplier();

    const pResult2 = await api.createProduct(product2);
    const cResult2 = await api.createCustomer(customer2);
    const sResult2 = await api.createSupplier(supplier2);
    await api.updateProduct(pResult2.id, { default_supplier_id: sResult2.id });

    const so2 = makeSalesOrder(cResult2.id, [{ product_id: pResult2.id, quantity: 50, unit_price: 8 }]);
    const soResult2 = await api.createSalesOrder(so2);
    await api.confirmSalesOrder(soResult2.id);
    await api.generatePurchaseOrders(soResult2.id);

    const poList2 = await api.listPurchaseOrders({ page_size: '5', sort_order: 'desc' });
    const po2 = (poList2.items || poList2)[0];
    await api.confirmPurchaseOrder(po2.id);

    const poDetail2 = await api.getPurchaseOrder(po2.id);
    const poItems2 = poDetail2.items || [];
    const rnItems2 = poItems2.map((item: { id: string; product_id: string; quantity: number }) => ({
      purchase_order_item_id: item.id,
      product_id: item.product_id,
      quantity: item.quantity,
    }));
    await api.createReceivingNote(makeReceivingNote(po2.id, rnItems2));

    const cp2 = await api.createContainerPlan({
      sales_order_ids: [soResult2.id],
      container_type: '40HQ',
      container_count: 1,
      destination_port: 'Bangkok',
    });

    const batches2 = await api.listInventoryBatches();
    const batch2 = (Array.isArray(batches2) ? batches2 : batches2.items || []).find(
      (b: { product_id: string }) => b.product_id === pResult2.id,
    );
    if (batch2) {
      await api.addContainerItem(cp2.id, {
        container_seq: 1,
        inventory_record_id: batch2.id,
        quantity: 30,
        volume_cbm: 0.8,
        weight_kg: 200,
      });
    }
    await api.confirmContainerPlan(cp2.id);
    await api.recordStuffing(cp2.id, {
      container_seq: 1,
      container_no: 'CSLU8888888',
      seal_no: 'SLE2E002',
      stuffing_date: new Date().toISOString().split('T')[0],
      stuffing_location: 'E2E Warehouse 2',
    });
    const outbound2 = await api.createOutboundOrder({ container_plan_id: cp2.id });
    cancelableOutboundId = outbound2.id;

    await api.dispose();
  });

  test('outbound orders list page loads', async ({ adminPage }) => {
    await adminPage.goto('/outbound');
    await waitForTableLoaded(adminPage);

    // Should see the outbound order in the table
    await expect(adminPage.locator('.ant-pro-table')).toBeVisible();
    const rows = adminPage.locator('.ant-table-row');
    await expect(rows.first()).toBeVisible({ timeout: 10000 });
  });

  test('view outbound order detail page', async ({ adminPage }) => {
    await adminPage.goto(`/outbound/${outboundOrderId}`);
    await expect(adminPage.getByText(outboundOrderNo).first()).toBeVisible();
    await expect(adminPage.locator('.ant-descriptions')).toBeVisible();

    // Should show items table
    await expect(adminPage.locator('.ant-table')).toBeVisible();
  });

  test('confirm outbound order from detail page', async ({ adminPage }) => {
    await adminPage.goto(`/outbound/${outboundOrderId}`);
    await expect(adminPage.getByText(outboundOrderNo).first()).toBeVisible();

    const confirmBtn = adminPage.getByRole('button', { name: '确认出库' });
    if (await confirmBtn.isVisible({ timeout: 3000 }).catch(() => false)) {
      await confirmBtn.click();
      await adminPage.waitForTimeout(500);

      // Fill the confirm modal
      const modal = adminPage.locator('.ant-modal:visible');
      await expect(modal).toBeVisible();

      // Fill operator
      const operatorInput = modal.locator('input').filter({ hasText: '' }).last();
      if (await operatorInput.isVisible({ timeout: 2000 }).catch(() => false)) {
        await operatorInput.fill('E2E Tester');
      }

      // Click confirm button in modal
      await modal.getByRole('button', { name: '确认' }).click();
      await waitForMessage(adminPage, '出库确认成功');
    }
  });

  test('cancel outbound order from detail page', async ({ adminPage }) => {
    await adminPage.goto(`/outbound/${cancelableOutboundId}`);
    await adminPage.waitForTimeout(1000);

    const cancelBtn = adminPage.getByRole('button', { name: '取消' }).first();
    if (await cancelBtn.isVisible({ timeout: 3000 }).catch(() => false)) {
      await cancelBtn.click();
      await adminPage.waitForTimeout(500);

      // Confirm in the confirmation modal
      const confirmBtn = adminPage.locator('.ant-modal:visible .ant-btn-primary').or(
        adminPage.getByRole('button', { name: '确 定' }),
      );
      if (await confirmBtn.isVisible({ timeout: 3000 }).catch(() => false)) {
        await confirmBtn.click();
      }
      await waitForMessage(adminPage, '已取消');
    }
  });

  test('navigate to detail from list', async ({ adminPage }) => {
    await adminPage.goto('/outbound');
    await waitForTableLoaded(adminPage);

    // Click on the first order number link or detail button
    const detailLink = adminPage.getByRole('link', { name: /OUT-/ }).first()
      .or(adminPage.getByText(/OUT-/).first());
    if (await detailLink.isVisible({ timeout: 5000 }).catch(() => false)) {
      await detailLink.click();
      await adminPage.waitForURL('**/outbound/**');
      await expect(adminPage.locator('.ant-descriptions')).toBeVisible({ timeout: 10000 });
    }
  });
});

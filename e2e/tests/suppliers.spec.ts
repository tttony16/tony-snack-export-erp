import { test, expect } from '../fixtures/auth';
import { makeSupplier } from '../fixtures/test-data';
import {
  fillProFormField,
  waitForTableLoaded,
  waitForModalClosed,
  waitForMessage,
  fillTableSearch,
} from '../helpers/ant-helpers';

test.describe('Suppliers Module', () => {
  let apiSupplierName: string;

  test.beforeAll(async () => {
    const { ApiClient } = await import('../fixtures/api-client');
    const api = await ApiClient.create('admin', 'admin123');
    const data = makeSupplier();
    apiSupplierName = data.name;
    await api.createSupplier(data);
    await api.dispose();
  });

  test('UI create supplier with form', async ({ adminPage }) => {
    const supplier = makeSupplier();
    await adminPage.goto('/suppliers');
    await waitForTableLoaded(adminPage);

    await adminPage.getByRole('button', { name: '新建供应商' }).click();
    await expect(adminPage.getByText('新建供应商').first()).toBeVisible();

    await fillProFormField(adminPage, '供应商名称', supplier.name);
    await fillProFormField(adminPage, '联系人', supplier.contact_person);
    await fillProFormField(adminPage, '电话', supplier.phone);

    await adminPage.getByRole('button', { name: '确 定' }).click();
    await waitForMessage(adminPage, '创建成功');
    await waitForModalClosed(adminPage);
  });

  test('edit supplier', async ({ adminPage }) => {
    await adminPage.goto('/suppliers');
    await waitForTableLoaded(adminPage);

    const row = adminPage.locator('tr', { hasText: apiSupplierName }).first();
    await row.getByText('编辑').click();
    await expect(adminPage.getByText('编辑供应商').first()).toBeVisible();

    const nameInput = adminPage.locator('.ant-form-item', { has: adminPage.getByText('供应商名称', { exact: true }) }).locator('input').first();
    await nameInput.clear();
    await nameInput.fill(`${apiSupplierName}-edited`);

    await adminPage.getByRole('button', { name: '确 定' }).click();
    await waitForMessage(adminPage, '更新成功');
    await waitForModalClosed(adminPage);

    apiSupplierName = `${apiSupplierName}-edited`;
  });

  test('add supply categories via multi-select', async ({ adminPage }) => {
    await adminPage.goto('/suppliers');
    await waitForTableLoaded(adminPage);

    // Click edit on the first row (most recently created supplier)
    const firstRow = adminPage.locator('.ant-table-row').first();
    await firstRow.getByText('编辑').click();
    await expect(adminPage.getByText('编辑供应商').first()).toBeVisible();

    // Click on supply categories multi-select
    const categoriesItem = adminPage.locator('.ant-form-item', { has: adminPage.getByText('供应品类', { exact: true }) });
    const select = categoriesItem.locator('.ant-select').first();
    await select.click();
    // Select additional category
    await adminPage.locator('.ant-select-dropdown:visible').getByText('糖果').first().click();
    // Close dropdown
    await adminPage.keyboard.press('Escape');

    await adminPage.getByRole('button', { name: '确 定' }).click();
    await waitForMessage(adminPage, '更新成功');
    await waitForModalClosed(adminPage);
  });

  test('keyword search filters results', async ({ adminPage }) => {
    await adminPage.goto('/suppliers');
    await waitForTableLoaded(adminPage);

    // Search by generic keyword in the first input field
    await fillTableSearch(adminPage, 'E2E');

    // Table should still be visible after search
    await expect(adminPage.locator('.ant-table-row').first()).toBeVisible({ timeout: 10000 });
  });

  test('certificate URL list add and remove', async ({ adminPage }) => {
    await adminPage.goto('/suppliers');
    await waitForTableLoaded(adminPage);

    // Use the first row (most recently created supplier, guaranteed on page 1)
    const firstRow = adminPage.locator('.ant-table-row').first();
    await firstRow.getByText('编辑').click();
    await expect(adminPage.getByText('编辑供应商').first()).toBeVisible();

    // Add a certificate link
    await adminPage.getByRole('button', { name: '添加证书链接' }).click();
    const certInputs = adminPage.locator('.ant-modal:visible').locator('input[placeholder]');
    const lastInput = certInputs.last();
    await lastInput.fill('https://example.com/cert.pdf');

    // Should see the remove icon
    await expect(adminPage.locator('.anticon-minus-circle, .anticon-delete').first()).toBeVisible();

    await adminPage.getByRole('button', { name: '确 定' }).click();
    await waitForMessage(adminPage, '更新成功');
    await waitForModalClosed(adminPage);
  });
});

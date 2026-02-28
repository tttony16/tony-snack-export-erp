import { test, expect } from '../fixtures/auth';
import { makeCustomer } from '../fixtures/test-data';
import {
  fillProFormField,
  selectAntOption,
  waitForTableLoaded,
  waitForModalClosed,
  waitForMessage,
  fillTableSearch,
} from '../helpers/ant-helpers';

test.describe('Customers Module', () => {
  let apiCustomerName: string;
  let apiCustomerId: string;

  test.beforeAll(async () => {
    const { ApiClient } = await import('../fixtures/api-client');
    const api = await ApiClient.create('admin', 'admin123');
    const data = makeCustomer();
    apiCustomerName = data.name;
    const result = await api.createCustomer(data);
    apiCustomerId = result.id;
    await api.dispose();
  });

  test('UI create customer with form', async ({ adminPage }) => {
    const customer = makeCustomer();
    await adminPage.goto('/customers');
    await waitForTableLoaded(adminPage);

    await adminPage.getByRole('button', { name: '新建客户' }).click();
    await expect(adminPage.getByText('新建客户').first()).toBeVisible();

    await fillProFormField(adminPage, '客户名称', customer.name);
    await fillProFormField(adminPage, '国家', customer.country);
    await fillProFormField(adminPage, '联系人', customer.contact_person);
    await selectAntOption(adminPage, '币种', 'USD');
    await selectAntOption(adminPage, '付款方式', 'T/T');

    await adminPage.getByRole('button', { name: '确 定' }).click();
    await waitForMessage(adminPage, '创建成功');
    await waitForModalClosed(adminPage);
  });

  test('edit customer', async ({ adminPage }) => {
    await adminPage.goto('/customers');
    await waitForTableLoaded(adminPage);

    const row = adminPage.locator('tr', { hasText: apiCustomerName }).first();
    await row.getByText('编辑').click();
    await expect(adminPage.getByText('编辑客户').first()).toBeVisible();

    const nameInput = adminPage.locator('.ant-form-item', { has: adminPage.getByText('客户名称', { exact: true }) }).locator('input').first();
    await nameInput.clear();
    await nameInput.fill(`${apiCustomerName}-edited`);

    await adminPage.getByRole('button', { name: '确 定' }).click();
    await waitForMessage(adminPage, '更新成功');
    await waitForModalClosed(adminPage);

    apiCustomerName = `${apiCustomerName}-edited`;
  });

  test('keyword search filters results', async ({ adminPage }) => {
    await adminPage.goto('/customers');
    await waitForTableLoaded(adminPage);

    // Use the first search field (客户编码 or generic keyword) and verify results load
    await fillTableSearch(adminPage, 'E2E');

    // Should still show table with E2E test customers
    await expect(adminPage.locator('.ant-table-row').first()).toBeVisible();
  });

  test('empty form submission shows validation errors', async ({ adminPage }) => {
    await adminPage.goto('/customers');
    await waitForTableLoaded(adminPage);

    await adminPage.getByRole('button', { name: '新建客户' }).click();
    await expect(adminPage.getByText('新建客户').first()).toBeVisible();

    await adminPage.getByRole('button', { name: '确 定' }).click();
    await expect(adminPage.locator('.ant-form-item-explain-error').first()).toBeVisible();
  });

  test('view orders link navigates to sales orders', async ({ adminPage }) => {
    await adminPage.goto('/customers');
    await waitForTableLoaded(adminPage);

    // Use the first table row that has a 查看订单 link (any customer will do)
    const viewOrdersLink = adminPage.locator('.ant-table-row').locator('text=查看订单').first();
    await expect(viewOrdersLink).toBeVisible({ timeout: 5000 });
    await viewOrdersLink.click();
    await adminPage.waitForURL('**/sales-orders?customer_id=*', { timeout: 10000 });
  });
});

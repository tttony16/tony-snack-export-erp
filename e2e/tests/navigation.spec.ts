import { test, expect } from '../fixtures/auth';

test.describe('Navigation', () => {
  test('sidebar shows all main modules', async ({ adminPage }) => {
    const sidebar = adminPage.locator('.ant-layout-sider');

    const modules = [
      '工作台',
      '商品管理',
      '客户管理',
      '供应商管理',
      '销售订单',
      '采购订单',
      '仓储管理',
      '排柜管理',
      '物流管理',
    ];

    for (const mod of modules) {
      await expect(sidebar.getByText(mod)).toBeVisible();
    }
  });

  test('global search navigates correctly', async ({ adminPage }) => {
    const searchInput = adminPage.getByPlaceholder('搜索单号/商品名...');
    await expect(searchInput).toBeVisible();

    await searchInput.fill('SO-test');
    await searchInput.press('Enter');
    await adminPage.waitForURL('**/sales-orders?keyword=SO-test');
  });
});

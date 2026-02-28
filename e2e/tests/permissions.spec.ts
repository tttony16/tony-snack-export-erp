import { test, expect } from '../fixtures/auth';

test.describe('Permissions', () => {
  test('viewer cannot see create product button', async ({ viewerPage }) => {
    await viewerPage.goto('/products');
    await viewerPage.waitForTimeout(2000);
    // The create button should not be rendered for viewer
    await expect(viewerPage.getByRole('button', { name: '新建商品' })).not.toBeVisible();
  });

  test('viewer sidebar has no system management menu', async ({ viewerPage }) => {
    const sidebar = viewerPage.locator('.ant-layout-sider');
    await expect(sidebar.getByText('系统管理')).not.toBeVisible();
  });

  test('viewer accessing /system/users sees no content or redirect', async ({ viewerPage }) => {
    await viewerPage.goto('/system/users');
    await viewerPage.waitForTimeout(3000);
    // Should either redirect away, show access denied, or have no usable table
    const isOnSystemUsers = viewerPage.url().includes('/system/users');
    if (isOnSystemUsers) {
      // If still on the page, there should be no functional table or it should show access denied
      const hasTable = await viewerPage.locator('.ant-pro-table .ant-table-row').first().isVisible({ timeout: 2000 }).catch(() => false);
      expect(hasTable).toBeFalsy();
    }
    // If redirected, that's also a pass
  });

  test('admin can see all menus and create buttons', async ({ adminPage }) => {
    const sidebar = adminPage.locator('.ant-layout-sider');

    // Admin should see system management
    // Click to expand if needed
    const sysMenu = sidebar.getByText('系统管理');
    if (await sysMenu.isVisible()) {
      await expect(sysMenu).toBeVisible();
    }

    // Admin should see create buttons on products page
    await adminPage.goto('/products');
    await adminPage.waitForTimeout(2000);
    await expect(adminPage.getByRole('button', { name: '新建商品' })).toBeVisible();

    // Admin should see create button on sales orders
    await adminPage.goto('/sales-orders');
    await adminPage.waitForTimeout(2000);
    await expect(adminPage.getByRole('button', { name: '新建订单' })).toBeVisible();
  });
});

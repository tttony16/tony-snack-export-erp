import { test, expect } from '../fixtures/auth';
import { test as base } from '@playwright/test';

test.describe('Authentication', () => {
  test('admin can login and see dashboard', async ({ adminPage }) => {
    await expect(adminPage).toHaveURL(/\/dashboard/);
    await expect(adminPage.locator('.ant-pro-page-container')).toBeVisible();
  });

  base('wrong password stays on login page', async ({ page }) => {
    await page.goto('/login');
    await page.getByPlaceholder('用户名').fill('admin');
    await page.getByPlaceholder('密码').fill('wrongpassword');
    await page.getByRole('button', { name: '登 录' }).click();
    // Should stay on login page
    await page.waitForTimeout(2000);
    await expect(page).toHaveURL(/\/login/);
  });

  test('logout returns to login page', async ({ adminPage }) => {
    // Hover over user dropdown trigger in header to open the menu
    const header = adminPage.locator('.ant-pro-global-header');
    const dropdownTrigger = header.locator('.ant-dropdown-trigger').first();
    await dropdownTrigger.hover();
    await adminPage.waitForTimeout(500);
    // If hover didn't work, try click
    if (!(await adminPage.getByText('退出登录').isVisible().catch(() => false))) {
      await dropdownTrigger.click();
    }
    await adminPage.getByText('退出登录').click();
    await adminPage.waitForURL('**/login', { timeout: 10000 });
    await expect(adminPage).toHaveURL(/\/login/);
  });

  base('unauthenticated access to /products redirects to login', async ({ page }) => {
    await page.goto('/products');
    await page.waitForURL('**/login', { timeout: 10000 });
    await expect(page).toHaveURL(/\/login/);
  });
});

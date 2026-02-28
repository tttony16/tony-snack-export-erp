import { test, expect } from '@playwright/test';

test.describe('Smoke Tests', () => {
  test('login page loads with form elements', async ({ page }) => {
    await page.goto('/login');
    await expect(page.getByPlaceholder('用户名')).toBeVisible();
    await expect(page.getByPlaceholder('密码')).toBeVisible();
    await expect(page.getByRole('button', { name: '登 录' })).toBeVisible();
  });

  test('unauthenticated user redirects to login', async ({ page }) => {
    await page.goto('/dashboard');
    await page.waitForURL('**/login');
    await expect(page).toHaveURL(/\/login/);
  });
});

import { test, expect } from '../fixtures/auth';

test.describe('Dashboard', () => {
  test('KPI stat cards are visible', async ({ adminPage }) => {
    await adminPage.goto('/dashboard');
    // 4 KPI cards
    await expect(adminPage.getByText('待确认销售单')).toBeVisible();
    await expect(adminPage.getByText('待收货采购单')).toBeVisible();
    await expect(adminPage.getByText('备货完成')).toBeVisible();
    await expect(adminPage.getByText('即将到港')).toBeVisible();
  });

  test('in-transit logistics section renders', async ({ adminPage }) => {
    await adminPage.goto('/dashboard');
    await expect(adminPage.getByText('在途物流').first()).toBeVisible();
  });

  test('expiry warnings section renders', async ({ adminPage }) => {
    await adminPage.goto('/dashboard');
    await adminPage.waitForTimeout(2000);
    await expect(adminPage.getByText('保质期预警').first()).toBeVisible();
  });
});

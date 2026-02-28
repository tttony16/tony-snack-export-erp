import { test as base, type Page, type BrowserContext } from '@playwright/test';
import { ApiClient } from './api-client';

const ADMIN_USERNAME = process.env.E2E_ADMIN_USERNAME || 'admin';
const ADMIN_PASSWORD = process.env.E2E_ADMIN_PASSWORD || 'admin123';

export async function login(page: Page, username: string, password: string) {
  await page.goto('/login');
  await page.getByPlaceholder('用户名').fill(username);
  await page.getByPlaceholder('密码').fill(password);
  await page.getByRole('button', { name: '登 录' }).click();
  await page.waitForURL('**/dashboard', { timeout: 15000 });
}

type Fixtures = {
  adminPage: Page;
  apiClient: ApiClient;
  viewerPage: Page;
};

export const test = base.extend<Fixtures>({
  adminPage: async ({ page }, use) => {
    await login(page, ADMIN_USERNAME, ADMIN_PASSWORD);
    await use(page);
  },

  apiClient: async ({}, use) => {
    const client = await ApiClient.create(ADMIN_USERNAME, ADMIN_PASSWORD);
    await use(client);
    await client.dispose();
  },

  viewerPage: async ({ browser }, use) => {
    const context: BrowserContext = await browser.newContext();
    const page = await context.newPage();
    await login(page, 'e2e_viewer', 'test123456');
    await use(page);
    await context.close();
  },
});

export { expect } from '@playwright/test';

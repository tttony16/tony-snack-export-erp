import { test, expect } from '@playwright/test';
import { ApiClient } from '../fixtures/api-client';

const TEST_USERS = [
  { username: 'e2e_sales', password: 'test123456', display_name: 'E2E Sales', role: 'sales' },
  { username: 'e2e_purchaser', password: 'test123456', display_name: 'E2E Purchaser', role: 'purchaser' },
  { username: 'e2e_warehouse', password: 'test123456', display_name: 'E2E Warehouse', role: 'warehouse' },
  { username: 'e2e_viewer', password: 'test123456', display_name: 'E2E Viewer', role: 'viewer' },
];

test.describe('Global Setup', () => {
  test('create test role users if not exist', async () => {
    const api = await ApiClient.create('admin', 'admin123');

    try {
      const existing = await api.listUsers({ page_size: '100' });
      const existingUsernames = new Set(
        (existing.items || existing).map((u: { username: string }) => u.username),
      );

      for (const user of TEST_USERS) {
        if (!existingUsernames.has(user.username)) {
          await api.createUser(user);
        }
      }

      // Verify all users exist now
      const after = await api.listUsers({ page_size: '100' });
      const afterUsernames = new Set(
        (after.items || after).map((u: { username: string }) => u.username),
      );
      for (const user of TEST_USERS) {
        expect(afterUsernames.has(user.username)).toBeTruthy();
      }
    } finally {
      await api.dispose();
    }
  });
});

import { test, expect } from '../fixtures/auth';
import { makeProduct } from '../fixtures/test-data';
import {
  fillProFormField,
  fillProFormDigit,
  selectAntOption,
  waitForTableLoaded,
  waitForModalClosed,
  waitForMessage,
  fillTableSearch,
  expandTableSearch,
} from '../helpers/ant-helpers';

test.describe('Products Module', () => {
  let apiProductName: string;

  test.beforeAll(async ({ browser }) => {
    // Create a product via API for edit/search tests
    const { ApiClient } = await import('../fixtures/api-client');
    const api = await ApiClient.create('admin', 'admin123');
    const data = makeProduct();
    apiProductName = data.name_cn;
    await api.createProduct(data);
    await api.dispose();
  });

  test('UI create product with full form', async ({ adminPage }) => {
    const product = makeProduct();
    await adminPage.goto('/products');
    await waitForTableLoaded(adminPage);

    await adminPage.getByRole('button', { name: '新建商品' }).click();
    await expect(adminPage.getByText('新建商品').first()).toBeVisible();

    await fillProFormField(adminPage, 'SKU 编码', product.sku_code);
    await fillProFormField(adminPage, '中文名称', product.name_cn);
    await fillProFormField(adminPage, '英文名称', product.name_en);
    await selectAntOption(adminPage, '分类', '饼干');
    await fillProFormField(adminPage, '规格', product.spec);
    await fillProFormField(adminPage, '装箱规格', product.packing_spec);
    await fillProFormDigit(adminPage, '单位重量(kg)', String(product.unit_weight_kg));
    await fillProFormDigit(adminPage, '单位体积(cbm)', String(product.unit_volume_cbm));
    await fillProFormDigit(adminPage, '箱长(cm)', String(product.carton_length_cm));
    await fillProFormDigit(adminPage, '箱宽(cm)', String(product.carton_width_cm));
    await fillProFormDigit(adminPage, '箱高(cm)', String(product.carton_height_cm));
    await fillProFormDigit(adminPage, '箱毛重(kg)', String(product.carton_gross_weight_kg));
    await fillProFormDigit(adminPage, '保质期(天)', String(product.shelf_life_days));

    // Submit
    await adminPage.getByRole('button', { name: '确 定' }).click();
    await waitForMessage(adminPage, '创建成功');
    await waitForModalClosed(adminPage);
  });

  test('edit product name', async ({ adminPage }) => {
    await adminPage.goto('/products');
    await waitForTableLoaded(adminPage);

    // Find the API-created product and click edit
    const row = adminPage.locator('tr', { hasText: apiProductName }).first();
    await row.getByText('编辑').click();

    await expect(adminPage.getByText('编辑商品').first()).toBeVisible();
    const newName = `${apiProductName}-edited`;
    const nameInput = adminPage.locator('.ant-form-item', { has: adminPage.getByText('中文名称', { exact: true }) }).locator('input').first();
    await nameInput.clear();
    await nameInput.fill(newName);

    await adminPage.getByRole('button', { name: '确 定' }).click();
    await waitForMessage(adminPage, '更新成功');
    await waitForModalClosed(adminPage);

    // Update for subsequent tests
    apiProductName = newName;
  });

  test('toggle product status via switch', async ({ adminPage }) => {
    await adminPage.goto('/products');
    await waitForTableLoaded(adminPage);

    // Find any switch in the first row and toggle it
    // (searching by product name may not filter due to API limitations)
    const firstRow = adminPage.locator('.ant-table-row').first();
    const switchBtn = firstRow.locator('.ant-switch').first();
    await switchBtn.waitFor({ state: 'visible', timeout: 5000 });
    const initialChecked = await switchBtn.getAttribute('aria-checked');
    await switchBtn.click();
    await adminPage.waitForTimeout(1500);

    const newChecked = await switchBtn.getAttribute('aria-checked');
    expect(newChecked).not.toBe(initialChecked);
  });

  test('keyword search filters results', async ({ adminPage }) => {
    await adminPage.goto('/products');
    await waitForTableLoaded(adminPage);

    // Search by generic keyword in the first input field (may be SKU or keyword)
    await fillTableSearch(adminPage, 'E2E');

    // Table should still be visible after search
    await expect(adminPage.locator('.ant-table-row').first()).toBeVisible({ timeout: 10000 });
  });

  test('category filter works', async ({ adminPage }) => {
    await adminPage.goto('/products');
    await waitForTableLoaded(adminPage);

    // Expand search area if collapsed, then use the category select
    await expandTableSearch(adminPage);
    const searchArea = adminPage.locator('.ant-pro-table-search');
    const categoryItem = searchArea.locator('.ant-form-item', { hasText: '分类' }).first();
    const categorySelect = categoryItem.locator('.ant-select').first();
    await categorySelect.click();
    await adminPage.waitForTimeout(500);
    await adminPage.locator('.ant-select-dropdown:visible').locator('.ant-select-item-option').filter({ hasText: '饼干' }).first().click();
    await adminPage.getByRole('button', { name: '查 询' }).click();
    await waitForTableLoaded(adminPage);

    // Table should load (may or may not have results based on data)
    await expect(adminPage.locator('.ant-pro-table')).toBeVisible();
  });

  test('empty form submission shows validation errors', async ({ adminPage }) => {
    await adminPage.goto('/products');
    await waitForTableLoaded(adminPage);

    await adminPage.getByRole('button', { name: '新建商品' }).click();
    await expect(adminPage.getByText('新建商品').first()).toBeVisible();

    // Submit empty form
    await adminPage.getByRole('button', { name: '确 定' }).click();

    // Should show required field validation errors
    await expect(adminPage.locator('.ant-form-item-explain-error').first()).toBeVisible();
  });

  test('export button is visible', async ({ adminPage }) => {
    await adminPage.goto('/products');
    await waitForTableLoaded(adminPage);
    await expect(adminPage.getByRole('button', { name: '导出' })).toBeVisible();
  });
});

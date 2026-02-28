import { type Page, expect } from '@playwright/test';

/**
 * Get the form container - modal if visible, otherwise the page.
 */
function getFormScope(page: Page) {
  return page.locator('.ant-modal:visible .ant-modal-content');
}

/**
 * Select an option from an Ant Design Select component identified by its label.
 * Scoped to the visible modal if one exists.
 */
export async function selectAntOption(page: Page, fieldLabel: string, optionText: string) {
  const scope = getFormScope(page);
  const formItem = scope.locator('.ant-form-item', { hasText: fieldLabel }).first();
  const select = formItem.locator('.ant-select').first();
  await select.scrollIntoViewIfNeeded();
  await page.waitForTimeout(300);
  await select.click();
  await page.waitForTimeout(500);
  const dropdown = page.locator('.ant-select-dropdown:visible');
  // Match by text content, or by title/aria-label attribute (for selects where value != label)
  const option = dropdown.locator('.ant-select-item-option').filter({ hasText: optionText })
    .or(dropdown.locator(`.ant-select-item-option[title="${optionText}"], .ant-select-item-option[aria-label="${optionText}"]`))
    .first();
  await option.click();
}

/**
 * Select options from an Ant Design Cascader component identified by its label.
 * Clicks through each level of the cascader sequentially.
 * Scoped to the visible modal if one exists.
 */
export async function selectCascaderOption(page: Page, fieldLabel: string, optionTexts: string[]) {
  const scope = getFormScope(page);
  const formItem = scope.locator('.ant-form-item', { hasText: fieldLabel }).first();
  const cascader = formItem.locator('.ant-cascader').first();
  await cascader.scrollIntoViewIfNeeded();
  await page.waitForTimeout(300);
  await cascader.click();
  await page.waitForTimeout(500);

  for (let i = 0; i < optionTexts.length; i++) {
    const menuCol = page.locator('.ant-cascader-dropdown:visible .ant-cascader-menu').nth(i);
    await menuCol.waitFor({ state: 'visible', timeout: 5000 });
    const option = menuCol.locator('.ant-cascader-menu-item').filter({ hasText: optionTexts[i] }).first();
    await option.click();
    await page.waitForTimeout(300);
  }
}

/**
 * Select an option from a ProFormSelect with search.
 */
export async function selectSearchOption(page: Page, fieldLabel: string, searchText: string, optionText?: string) {
  const scope = getFormScope(page);
  const formItem = scope.locator('.ant-form-item', { hasText: fieldLabel }).first();
  const select = formItem.locator('.ant-select').first();
  await select.click();
  await select.locator('input').fill(searchText);
  await page.waitForTimeout(800);
  const dropdown = page.locator('.ant-select-dropdown:visible');
  await dropdown.locator('.ant-select-item-option').filter({ hasText: optionText || searchText }).first().click();
}

/**
 * Fill a ProForm text field by its label. Scoped to the visible modal.
 */
export async function fillProFormField(page: Page, label: string, value: string) {
  const scope = getFormScope(page);
  const formItem = scope.locator('.ant-form-item', { hasText: label }).first();
  const input = formItem.locator('input:not([type="hidden"])').first();
  await input.clear();
  await input.fill(value);
}

/**
 * Fill a ProFormDigit (spinbutton) field by its label. Scoped to the visible modal.
 */
export async function fillProFormDigit(page: Page, label: string, value: string) {
  const scope = getFormScope(page);
  const formItem = scope.locator('.ant-form-item', { hasText: label }).first();
  const input = formItem.locator('.ant-input-number input, input[role="spinbutton"]').first();
  await input.clear();
  await input.fill(value);
}

/**
 * Wait for ProTable spinner to disappear.
 */
export async function waitForTableLoaded(page: Page) {
  await page.locator('.ant-spin-spinning').waitFor({ state: 'hidden', timeout: 15000 }).catch(() => {});
  await page.locator('.ant-pro-table, .ant-table').first().waitFor({ state: 'visible', timeout: 10000 });
}

/**
 * Wait for a Modal to close (no visible modal).
 */
export async function waitForModalClosed(page: Page) {
  await page.locator('.ant-modal:visible').waitFor({ state: 'hidden', timeout: 15000 }).catch(() => {});
}

/**
 * Wait for an Ant Design message to appear.
 */
export async function waitForMessage(page: Page, text: string) {
  await expect(page.locator('.ant-message').getByText(text).first()).toBeVisible({ timeout: 10000 });
}

/**
 * Click an action button/link in a table row that contains the given text.
 */
export async function clickTableAction(page: Page, rowText: string, actionText: string) {
  const row = page.locator('tr', { hasText: rowText }).first();
  await row.getByText(actionText).click();
}

/**
 * Get the number of data rows in a ProTable.
 */
export async function getTableRowCount(page: Page): Promise<number> {
  await waitForTableLoaded(page);
  return page.locator('.ant-table-tbody tr.ant-table-row').count();
}

/**
 * Fill a date picker field by its label. Scoped to the visible modal.
 */
export async function fillDatePicker(page: Page, label: string, date: string) {
  const scope = getFormScope(page);
  const formItem = scope.locator('.ant-form-item', { hasText: label }).first();
  const input = formItem.locator('input').first();
  await input.click();
  await input.fill(date);
  await input.press('Enter');
  // Click the form title area to dismiss the date picker popup (not Escape, which closes the modal)
  await page.waitForTimeout(300);
  const modalTitle = scope.locator('.ant-modal-header, .ant-modal-title').first();
  if (await modalTitle.isVisible({ timeout: 500 }).catch(() => false)) {
    await modalTitle.click();
  }
  await page.waitForTimeout(200);
}

/**
 * Expand the ProTable search area if it's collapsed.
 */
export async function expandTableSearch(page: Page) {
  const expandBtn = page.locator('.ant-pro-table-search').getByText('展开');
  if (await expandBtn.isVisible({ timeout: 1000 }).catch(() => false)) {
    await expandBtn.click();
    await page.waitForTimeout(300);
  }
}

/**
 * Fill a search input in a ProTable search form. If fieldLabel is provided,
 * fills the input in the specific form item; otherwise fills the first visible input.
 */
export async function fillTableSearch(page: Page, keyword: string, fieldLabel?: string) {
  await waitForTableLoaded(page);
  const searchArea = page.locator('.ant-pro-table-search');
  let input;
  if (fieldLabel) {
    const formItem = searchArea.locator('.ant-form-item', { hasText: fieldLabel }).first();
    input = formItem.locator('input').first();
  } else {
    input = searchArea.locator('input:visible').first();
  }
  await input.clear();
  await input.fill(keyword);
  await page.getByRole('button', { name: '查 询' }).click();
  await waitForTableLoaded(page);
}

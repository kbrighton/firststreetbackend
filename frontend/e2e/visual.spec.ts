import { expect, test, type Page } from '@playwright/test';

const reactBase = 'http://127.0.0.1:5173';
const classicBase = 'http://127.0.0.1:5000';
const dueoutStart = '2099-12-10';
const dueoutEnd = '2099-12-11';

async function signIn(page: Page) {
  await page.goto(`${reactBase}/login`);
  await page.getByLabel('Username').fill('smokeuser');
  await page.getByLabel('Password').fill('SmokePass123');
  await page.getByRole('button', { name: 'Sign In' }).click();
  await expect(page.locator('nav .nav-link', { hasText: 'Search Form' })).toBeVisible();
}

async function signInAs(page: Page, username: string) {
  await page.goto(`${reactBase}/login`);
  await page.getByLabel('Username').fill(username);
  await page.getByLabel('Password').fill('SmokePass123');
  await page.getByRole('button', { name: 'Sign In' }).click();
  await expect(page.locator('nav .nav-link', { hasText: 'User Management' })).toBeVisible();
}

async function formStructure(page: Page, url: string) {
  await page.goto(url);
  await expect(page.locator('main h2').first()).toBeVisible();
  return {
    heading: (await page.locator('main h2').first().innerText()).trim(),
    labels: (await page.locator('main label').allInnerTexts()).map((label) => label.trim()),
  };
}

async function currentTableStructure(page: Page) {
  const table = page.locator('main table');
  await expect(table).toBeVisible();
  return {
    heading: (await page.locator('main h2').first().innerText()).trim(),
    caption: (await table.locator('caption').innerText()).trim(),
    headers: await table.locator('thead th').evaluateAll((headers) =>
      headers.slice(0, 12).map((header) => header.textContent?.trim() ?? ''),
    ),
    striped: await table.evaluate((element) => element.classList.contains('table-striped')),
    darkHeader: await table.locator('thead').evaluate((element) =>
      element.classList.contains('thead-dark') || element.classList.contains('table-dark'),
    ),
    responsive: (await page.locator('main .table-responsive').count()) > 0,
    pagination: (await page.locator('main .pagination').count()) > 0,
  };
}

async function tableStructure(page: Page, url: string) {
  await page.goto(url);
  return currentTableStructure(page);
}

async function usersTableStructure(page: Page, url: string) {
  await page.goto(url);
  const table = page.locator('main table');
  await expect(table).toBeVisible();
  return {
    heading: (await page.locator('main h2').first().innerText()).trim(),
    headers: (await table.locator('thead th').allInnerTexts()).map((header) => header.trim()),
    striped: await table.evaluate((element) => element.classList.contains('table-striped')),
  };
}

async function expectReactScreenshot(page: Page, name: string) {
  await expect(page).toHaveScreenshot(name, {
    fullPage: true,
    maxDiffPixelRatio: 0.02,
  });
}

test('React read-only pages preserve Jinja structure and visual baselines', async ({ page }) => {
  test.setTimeout(120_000);
  await signIn(page);

  const reactSearchForm = await formStructure(page, `${reactBase}/search`);
  await expectReactScreenshot(page, 'search-form.png');
  const classicSearchForm = await formStructure(page, `${classicBase}/search`);
  expect(reactSearchForm).toEqual(classicSearchForm);

  const reactResults = await tableStructure(
    page,
    `${reactBase}/order_search?cust=E2E01&title=E2E+Search`,
  );
  await expectReactScreenshot(page, 'search-results.png');
  expect(reactResults.pagination).toBe(true);
  expect(reactResults.responsive).toBe(false);
  const classicResults = await tableStructure(
    page,
    `${classicBase}/order_search/?cust=E2E01&title=E2E+Search`,
  );
  expect(reactResults).toEqual(classicResults);

  const reactLogSearch = await formStructure(page, `${reactBase}/search_log`);
  await expectReactScreenshot(page, 'search-log.png');
  const classicLogSearch = await formStructure(page, `${classicBase}/search_log`);
  expect(reactLogSearch).toEqual(classicLogSearch);

  const reactOrder = await formStructure(page, `${reactBase}/order/E2001`);
  await expectReactScreenshot(page, 'order-detail.png');
  const classicOrder = await formStructure(page, `${classicBase}/order/E2001`);
  expect(reactOrder).toEqual(classicOrder);

  const reactDueoutForm = await formStructure(page, `${reactBase}/dueouts`);
  await expectReactScreenshot(page, 'dueouts-form.png');
  const classicDueoutForm = await formStructure(page, `${classicBase}/dueouts`);
  expect(reactDueoutForm).toEqual(classicDueoutForm);

  const reactDueouts = await tableStructure(
    page,
    `${reactBase}/dueouts?start_date=${dueoutStart}&end_date=${dueoutEnd}`,
  );
  await expectReactScreenshot(page, 'dueouts-table.png');
  expect(reactDueouts.pagination).toBe(false);
  expect(reactDueouts.responsive).toBe(true);
  const classicDueoutPage = await page.goto(`${classicBase}/dueouts`);
  expect(classicDueoutPage?.status()).toBe(200);
  await page.getByLabel('Start Due Outs Date').fill(dueoutStart);
  await page.getByLabel('End Due Outs Date').fill(dueoutEnd);
  await page.getByRole('button', { name: 'Submit' }).click();
  const classicDueouts = await currentTableStructure(page);
  expect(reactDueouts).toEqual(classicDueouts);

  const reactAllDueouts = await tableStructure(page, `${reactBase}/dueouts_all`);
  await expectReactScreenshot(page, 'all-dueouts.png');
  const classicAllDueouts = await tableStructure(page, `${classicBase}/dueouts_all`);
  expect(reactAllDueouts).toEqual(classicAllDueouts);
});

test('React write pages preserve classic form/table structure and visual baselines', async ({ page }) => {
  test.setTimeout(120_000);
  await signInAs(page, 'smokeadmin');

  const reactNewOrder = await formStructure(page, `${reactBase}/order`);
  await expectReactScreenshot(page, 'order-create.png');
  const classicNewOrder = await formStructure(page, `${classicBase}/order`);
  expect(reactNewOrder).toEqual(classicNewOrder);

  const reactOrderEdit = await formStructure(page, `${reactBase}/order/E2001`);
  await expectReactScreenshot(page, 'order-edit.png');
  const classicOrderEdit = await formStructure(page, `${classicBase}/order/E2001`);
  expect(reactOrderEdit).toEqual(classicOrderEdit);

  const reactNewUser = await formStructure(page, `${reactBase}/user/new`);
  await expectReactScreenshot(page, 'user-create.png');
  const classicNewUser = await formStructure(page, `${classicBase}/user/new`);
  expect(reactNewUser).toEqual(classicNewUser);

  const reactUsers = await usersTableStructure(page, `${reactBase}/users`);
  await expectReactScreenshot(page, 'users-list.png');
  const classicUsers = await usersTableStructure(page, `${classicBase}/users`);
  expect(reactUsers).toEqual(classicUsers);

  await page.goto(`${reactBase}/newsearch`);
  const gridHeaders = await page.locator('main thead th').allInnerTexts();
  const expectedGridHeaders = [
    'Log#', 'Artlog', 'Customer', 'Title', 'Priority', 'Date In', 'Due Out', 'Colors',
    'Print Number', 'Logtype', 'Rush', 'Date Out',
  ];
  const normalizeHeaders = (headers: string[]) => headers.map((header) => header.trim().toLowerCase());
  expect(normalizeHeaders(gridHeaders)).toEqual(normalizeHeaders(expectedGridHeaders));
  await expectReactScreenshot(page, 'orders-grid.png');

  await page.goto(`${classicBase}/newsearch`);
  const classicHeaders = await page.locator('.gridjs-th:visible').allInnerTexts();
  expect(normalizeHeaders(classicHeaders)).toEqual(normalizeHeaders(expectedGridHeaders));
});
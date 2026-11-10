import { expect, test, type Page } from '@playwright/test';

const dueoutStart = '2099-12-10';
const dueoutEnd = '2099-12-11';

async function signIn(page: Page) {
  await page.goto('/login');
  await page.getByLabel('Username').fill('smokeuser');
  await page.getByLabel('Password').fill('SmokePass123');
  await page.getByRole('button', { name: 'Sign In' }).click();
  await expect(page.locator('nav .nav-link', { hasText: 'Search Form' })).toBeVisible();
}

test('search results paginate and cycle server-side sorting in the URL', async ({ page }) => {
  await signIn(page);
  await page.goto('/search');
  await page.getByLabel('Customer ID').fill('E2E01');
  await page.getByLabel('Title').fill('E2E Search');
  await page.getByRole('button', { name: 'Submit' }).click();

  await expect(page).toHaveURL(/\/order_search\?cust=E2E01&title=E2E\+Search$/);
  await expect(page.locator('h2')).toHaveText('Search');
  await expect(page.locator('table caption')).toHaveText('Searches');
  await expect(page.locator('tbody tr')).toHaveCount(20);
  await expect(page.getByRole('link', { name: 'Edit order E2025' })).toBeVisible();
  expect((await page.locator('thead th').allInnerTexts()).slice(0, 12)).toEqual([
    'Log#', 'Artlog', 'Customer', 'Title', 'Priority', 'Date In', 'Due Out', 'Colors',
    'Print Number', 'Logtype', 'Rush', 'Artist ID',
  ]);

  await page.getByLabel('Next').click();
  await expect.poll(() => new URL(page.url()).searchParams.get('page')).toBe('2');
  await expect(page.locator('tbody tr')).toHaveCount(5);

  const logHeader = page.getByRole('button', { name: 'Log#' });
  const logColumn = page.getByRole('columnheader', { name: 'Log#' });
  await logHeader.click();
  await expect.poll(() => new URL(page.url()).searchParams.get('sort')).toBe('+log');
  await expect.poll(() => new URL(page.url()).searchParams.get('page')).toBeNull();
  await expect(logColumn).toHaveAttribute('aria-sort', 'ascending');

  await logHeader.click();
  await expect.poll(() => new URL(page.url()).searchParams.get('sort')).toBe('-log');
  await logHeader.click();
  await expect.poll(() => new URL(page.url()).searchParams.has('sort')).toBe(false);
});

test('empty order search returns to Search Form with the legacy alert', async ({ page }) => {
  await signIn(page);
  await page.goto('/search');
  await page.getByLabel('Customer ID').fill('NO001');
  await page.getByRole('button', { name: 'Submit' }).click();

  await expect(page).toHaveURL('/search');
  await expect(page.getByRole('heading', { name: 'Search Form' })).toBeVisible();
  await expect(page.getByRole('alert')).toContainText('Could not find any orders that match');
});

test('log search opens read-only order details and handles missing orders', async ({ page }) => {
  await signIn(page);
  await page.goto('/search_log');
  await page.getByLabel('LOG #').fill('E2001');
  await page.getByRole('button', { name: 'Submit' }).click();

  await expect(page).toHaveURL(/\/order\/E2001$/);
  await expect(page.getByRole('heading', { name: 'Order Form' })).toBeVisible();
  await expect(page.getByLabel('LOG#')).toHaveValue('E2001');
  await expect(page.getByLabel('Customer#')).toHaveValue('E2E01');
  await expect(page.getByRole('link', { name: 'Edit in classic app' }))
    .toHaveAttribute('href', 'http://localhost:5000/order/E2001');

  await page.goto('/search_log');
  await page.getByLabel('LOG #').fill('ZZZZZ');
  await page.getByRole('button', { name: 'Submit' }).click();
  await expect(page.getByRole('alert')).toContainText('Log number does not exist');
  await expect(page).toHaveURL('/search_log');

  await page.goto('/order/ZZZZZ');
  await expect(page).toHaveURL('/search');
  await expect(page.getByRole('alert')).toContainText('Order with log number ZZZZZ not found');
});

test('date-range and all-dueout pages include filters, exclude invalid rows, and sort locally', async ({ page }) => {
  await signIn(page);
  await page.goto('/dueouts');
  await page.getByLabel('Start Due Outs Date').fill(dueoutStart);
  await page.getByLabel('End Due Outs Date').fill(dueoutEnd);
  await page.getByRole('button', { name: 'Submit' }).click();

  const resultsUrl = new URL(page.url());
  expect(resultsUrl.pathname).toBe('/dueouts');
  expect(resultsUrl.searchParams.get('start_date')).toBe(dueoutStart);
  expect(resultsUrl.searchParams.get('end_date')).toBe(dueoutEnd);
  await expect(page.locator('table caption')).toHaveText('Due Outs');
  const rangeRows = page.locator('tbody tr');
  await expect(rangeRows).toHaveCount(2);
  await expect(rangeRows.nth(0)).toContainText('E2001');
  await expect(rangeRows.nth(1)).toContainText('E2002');

  await page.goto('/dueouts_all');
  const allRows = page.locator('tbody tr');
  await expect(allRows).toHaveCount(23);
  await expect(allRows.filter({ hasText: 'DEL01' })).toHaveCount(0);
  await expect(allRows.filter({ hasText: 'E2005' })).toHaveCount(0);
  await expect(allRows.filter({ hasText: 'E2006' })).toHaveCount(0);

  const dueOutHeader = page.getByRole('columnheader', { name: 'Due Out' });
  await page.getByRole('button', { name: 'Due Out' }).click();
  await expect(dueOutHeader).toHaveAttribute('aria-sort', 'ascending');
  await page.getByRole('button', { name: 'Due Out' }).click();
  await expect(dueOutHeader).toHaveAttribute('aria-sort', 'descending');
  await expect(allRows.first()).toContainText('E2025');
});

test('creates, edits, grid-saves, and confirms deletion of an order', async ({ page }) => {
  await signIn(page);
  await page.goto('/order');
  await page.getByLabel('LOG#').fill('W0001');
  await page.getByLabel('Customer#').fill('E2E01');
  await page.getByLabel('Title').fill('E2E Grid Test order');
  await page.getByLabel('Date In').fill('2025-01-02');
  await page.getByLabel('Log Type').selectOption('TR');
  await page.getByLabel('Artist ID').fill('W1234');

  const createResponsePromise = page.waitForResponse((response) => (
    new URL(response.url()).pathname === '/api/orders'
    && response.request().method() === 'POST'
  ));
  await page.getByRole('button', { name: 'Submit' }).click();
  const createResponse = await createResponsePromise;
  expect(createResponse.status()).toBe(201);
  const createdOrder = await createResponse.json() as { id: number };
  await expect(page).toHaveURL('/order/W0001');
  await expect(page.getByLabel('Artist ID')).toHaveValue('W1234');

  await page.getByLabel('Title').fill('E2E Grid Test edited');
  const updateResponsePromise = page.waitForResponse((response) => (
    new URL(response.url()).pathname === `/api/orders/${createdOrder.id}`
    && response.request().method() === 'PUT'
  ));
  await page.getByRole('button', { name: 'Submit' }).click();
  expect((await updateResponsePromise).status()).toBe(200);
  await expect(page.getByRole('alert').filter({ hasText: 'Order updated successfully' })).toBeVisible();

  await page.goto('/newsearch');
  await page.getByLabel('Search orders').fill('E2E Grid Test');
  const gridTitle = page.getByLabel('Edit Title for W0001');
  await expect(gridTitle).toHaveValue('E2E Grid Test edited');
  await gridTitle.fill('E2E Grid Test saved');
  const gridUpdatePromise = page.waitForResponse((response) => (
    new URL(response.url()).pathname === `/api/orders/${createdOrder.id}`
    && response.request().method() === 'PUT'
  ));
  await gridTitle.press('Enter');
  expect((await gridUpdatePromise).status()).toBe(200);

  await page.reload();
  await page.getByLabel('Search orders').fill('E2E Grid Test');
  await expect(page.getByLabel('Edit Title for W0001')).toHaveValue('E2E Grid Test saved');

  await page.goto('/order/W0001');
  await expect(page.getByLabel('Title')).toHaveValue('E2E Grid Test saved');
  await page.getByRole('button', { name: 'Delete Order' }).click();
  await page.getByRole('dialog').getByRole('button', { name: 'Delete order' }).click();
  await expect(page).toHaveURL('/search');
  await expect(page.getByRole('alert').filter({ hasText: 'Order deleted successfully' })).toBeVisible();
});
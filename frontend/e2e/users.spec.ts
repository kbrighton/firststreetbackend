import { expect, test, type Page } from '@playwright/test';

async function signInAs(page: Page, username: string) {
  await page.goto('/login');
  await page.getByLabel('Username').fill(username);
  await page.getByLabel('Password').fill('SmokePass123');
  await page.getByRole('button', { name: 'Sign In' }).click();
  await expect(page.locator('nav .nav-link', { hasText: 'User Management' })).toBeVisible();
}

test('admins create and edit users through the React management pages', async ({ page }) => {
  let createdUserId: number | undefined;
  await signInAs(page, 'smokeadmin');

  try {
    await page.goto('/users');
    await page.getByRole('link', { name: 'Create New User' }).click();
    await page.getByLabel('Username').fill('phase4user');
    await page.getByLabel('Email').fill('phase4user@example.com');
    await page.getByLabel('Password').fill('Phase4Pass123');

    const createResponsePromise = page.waitForResponse((response) => (
      new URL(response.url()).pathname === '/api/users'
      && response.request().method() === 'POST'
    ));
    await page.getByRole('button', { name: 'Submit' }).click();
    const createResponse = await createResponsePromise;
    expect(createResponse.status()).toBe(201);
    const createdUser = await createResponse.json() as { id: number };
    createdUserId = createdUser.id;
    await expect(page.getByRole('heading', { name: 'User Management' })).toBeVisible();

    const userRow = page.getByRole('row').filter({ hasText: 'phase4user@example.com' });
    await expect(userRow).toContainText('phase4user');
    await userRow.getByRole('link', { name: 'Edit' }).click();
    await expect(page.getByRole('heading', { name: 'Edit User: phase4user' })).toBeVisible();
    await expect(page.getByLabel('Role')).toBeVisible();
    await page.getByLabel('Password').fill('Phase4Updated123');
    await page.getByLabel('Role').selectOption('admin');

    const updateResponsePromise = page.waitForResponse((response) => (
      new URL(response.url()).pathname === `/api/users/${createdUserId}`
      && response.request().method() === 'PUT'
    ));
    await page.getByRole('button', { name: 'Submit' }).click();
    expect((await updateResponsePromise).status()).toBe(200);
    const updatedUserRow = page.getByRole('row').filter({ hasText: 'phase4user@example.com' });
    await expect(updatedUserRow).toContainText('admin');
  } finally {
    if (createdUserId !== undefined) {
      const status = await page.evaluate(async (id) => {
        const tokenResponse = await fetch('/api/auth/csrf');
        const { csrf_token: csrfToken } = await tokenResponse.json() as { csrf_token: string };
        const deleteResponse = await fetch(`/api/users/${id}`, {
          method: 'DELETE',
          headers: { 'X-CSRFToken': csrfToken },
        });
        return deleteResponse.status;
      }, createdUserId);
      expect(status).toBe(204);
    }
  }
});

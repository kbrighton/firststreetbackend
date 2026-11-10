import { expect, test, type Page } from '@playwright/test';

const login = async (page: Page, username: string, password: string) => {
  await page.getByLabel('Username').fill(username);
  await page.getByLabel('Password').fill(password);
  await page.getByRole('button', { name: 'Sign In' }).click();
};

test('staff login validation, session persistence, and logout', async ({ page }) => {
  await page.goto('/dueouts');
  await expect(page).toHaveURL(/\/login\?next=/);
  await expect(page.getByRole('heading', { name: 'Login Page' })).toBeVisible();

  await login(page, 'ab', 'short');
  await expect(page.getByText('Username must be between 3 and 64 characters')).toBeVisible();
  await expect(page.getByText('Password must be at least 8 characters')).toBeVisible();

  await login(page, 'smokeuser', 'WrongPass123');
  const invalidCredentialsAlert = page.locator('.alert-danger', {
    hasText: 'Invalid username or password',
  });
  await expect(invalidCredentialsAlert).toBeVisible();
  await invalidCredentialsAlert.getByRole('button', { name: 'Close' }).click();
  await expect(invalidCredentialsAlert).toHaveCount(0);

  await login(page, 'SmokeUser', 'SmokePass123');
  await expect(page).toHaveURL(/\/dueouts$/);
  await expect(page.locator('nav .nav-link', { hasText: 'Manage My Profile' })).toBeVisible();
  await page.reload();
  await expect(page.locator('nav .nav-link', { hasText: 'Logout' })).toBeVisible();

  await page.locator('nav .nav-link', { hasText: 'Logout' }).click();
  await expect(page).toHaveURL(/\/login$/);
  await expect(page.getByText('You have been logged out')).toBeVisible();
  const currentUserStatus = await page.evaluate(async () => (await fetch('/api/auth/me')).status);
  expect(currentUserStatus).toBe(401);
});

test('admin login shows user management navigation', async ({ page }) => {
  await page.goto('/login');
  await login(page, 'smokeadmin', 'SmokePass123');
  await expect(page.locator('nav .nav-link', { hasText: 'User Management' })).toBeVisible();
  await expect(page.locator('nav .nav-link', { hasText: 'Manage My Profile' })).toHaveCount(0);
});

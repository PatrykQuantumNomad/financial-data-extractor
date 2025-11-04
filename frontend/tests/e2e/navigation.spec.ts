import { test, expect } from '@playwright/test';

test.describe('Navigation', () => {
  test('should navigate through all main pages', async ({ page }) => {
    // Start at home
    await page.goto('/');
    await expect(page).toHaveURL('/');
    await expect(page.getByRole('heading', { name: /companies/i })).toBeVisible();

    // Navigate to extraction page
    await page.getByRole('link', { name: /extraction/i }).click();
    await expect(page).toHaveURL('/extraction');
    await expect(page.getByRole('heading', { name: /data extraction/i })).toBeVisible();

    // Navigate back to home
    await page.getByRole('link', { name: /companies/i }).click();
    await expect(page).toHaveURL('/');
    await expect(page.getByRole('heading', { name: /companies/i })).toBeVisible();
  });

  test('should have consistent navbar on all pages', async ({ page }) => {
    const pages = ['/', '/extraction'];

    for (const path of pages) {
      await page.goto(path);

      // Check navbar is present
      const navbar = page.getByRole('navigation');
      await expect(navbar).toBeVisible();

      // Check all nav links are present
      await expect(page.getByRole('link', { name: /companies/i })).toBeVisible();
      await expect(page.getByRole('link', { name: /extraction/i })).toBeVisible();
    }
  });
});

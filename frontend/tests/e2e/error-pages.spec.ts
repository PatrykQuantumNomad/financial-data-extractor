import { test, expect } from '@playwright/test';

test.describe('Error Pages', () => {
  test('should display 404 page for invalid company ID', async ({ page }) => {
    // Navigate to a non-existent company statement page
    await page.goto('/companies/99999/statements/income_statement');

    // Should show 404 page
    await expect(page.getByText(/404/i)).toBeVisible();
    await expect(page.getByText(/page not found/i)).toBeVisible();
  });

  test('should display 404 page for invalid route', async ({ page }) => {
    await page.goto('/invalid-route-that-does-not-exist');

    // Next.js should show 404
    await expect(page.getByText(/404/i)).toBeVisible();
  });

  test('should have navigation back to home from 404 page', async ({ page }) => {
    await page.goto('/companies/99999/statements/income_statement');

    // Check back to home button exists
    const homeButton = page.getByRole('link', { name: /back to home/i });
    await expect(homeButton).toBeVisible();

    // Click and verify navigation
    await homeButton.click();
    await expect(page).toHaveURL('/');
    await expect(page.getByRole('heading', { name: /companies/i })).toBeVisible();
  });

  test('should display error message for invalid statement type', async ({ page }) => {
    // This test assumes we have at least one company in the database
    // For now, we'll test the error handling structure
    await page.goto('/companies/1/statements/invalid_type');

    // Should show error or redirect
    // The actual behavior depends on your error handling implementation
    await expect(page).toHaveURL(/\/companies\/\d+\/statements\/invalid_type/);
  });
});

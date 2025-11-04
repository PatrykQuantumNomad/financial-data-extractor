import { test, expect } from '@playwright/test';

test.describe('Company Statements', () => {
  test('should navigate to income statement from company list', async ({ page }) => {
    await page.goto('/');

    // Wait for companies to load (if any exist)
    await page.waitForLoadState('networkidle');

    // Try to find a "View Statements" button - this will work if companies exist
    const viewStatementsButton = page.getByRole('button', { name: /view statements/i }).first();

    // Check if companies exist, if not, skip the rest of the test
    const companiesLoaded = await viewStatementsButton.isVisible().catch(() => false);

    if (companiesLoaded) {
      await viewStatementsButton.click();

      // Should navigate to income statement page
      await expect(page).toHaveURL(/\/companies\/\d+\/statements\/income_statement/);

      // Should show some content on the statement page
      // The exact content depends on whether data exists
      const pageContent = page.locator('main');
      await expect(pageContent).toBeVisible();
    } else {
      test.info().annotations.push({
        type: 'skip',
        description: 'No companies found in database - skipping navigation test',
      });
    }
  });

  test('should handle loading state for statements', async ({ page }) => {
    // Navigate directly to a statement page
    await page.goto('/companies/1/statements/income_statement');

    // Should show some loading state or content
    // The page should either show data, loading state, or error
    await page.waitForLoadState('networkidle');

    // Check that the page has rendered something
    const main = page.locator('main');
    await expect(main).toBeVisible();
  });

  test('should show error for non-existent company', async ({ page }) => {
    await page.goto('/companies/99999/statements/income_statement');

    // Should show 404 or error page
    await expect(page.getByText(/404|not found|error/i).first()).toBeVisible({ timeout: 10000 });
  });

  test('should handle different statement types', async ({ page }) => {
    const statementTypes = ['income_statement', 'balance_sheet', 'cash_flow'];

    for (const type of statementTypes) {
      await page.goto(`/companies/1/statements/${type}`);
      await page.waitForLoadState('networkidle');

      // Page should load (either with data, loading, or error state)
      const main = page.locator('main');
      await expect(main).toBeVisible();
    }
  });
});

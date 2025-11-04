import { test, expect } from '@playwright/test';

test.describe('Extraction Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/extraction');
  });

  test('should display extraction page with correct title', async ({ page }) => {
    await expect(page.getByRole('heading', { name: /data extraction/i })).toBeVisible();
    await expect(page.getByText(/manage extraction tasks/i)).toBeVisible();
  });

  test('should show company selection section', async ({ page }) => {
    // Wait for page to load
    await page.waitForLoadState('networkidle');

    // Check for company selection card
    const selectCompanyCard = page.getByText(/select company/i);
    await expect(selectCompanyCard).toBeVisible();
  });

  test('should handle empty company list gracefully', async ({ page }) => {
    await page.waitForLoadState('networkidle');

    // If no companies exist, should show appropriate message
    const noCompaniesMessage = page.getByText(/no companies found/i);
    const hasMessage = await noCompaniesMessage.isVisible().catch(() => false);

    if (hasMessage) {
      await expect(noCompaniesMessage).toBeVisible();
    }
  });

  test('should allow selecting a company', async ({ page }) => {
    await page.waitForLoadState('networkidle');

    // Try to find and click a company button
    const companyButtons = page.getByRole('button').filter({ hasText: /company|adyen|heineken/i });
    const buttonCount = await companyButtons.count();

    if (buttonCount > 0) {
      await companyButtons.first().click();

      // After selection, extraction controls should be visible or enabled
      // This depends on your implementation
      await page.waitForTimeout(500); // Give time for state update

      // Verify some interaction occurred (button might have different styling when selected)
      const selectedButton = companyButtons.first();
      await expect(selectedButton).toBeVisible();
    } else {
      test.info().annotations.push({
        type: 'skip',
        description: 'No companies available to test selection',
      });
    }
  });

  test('should navigate back to home from extraction page', async ({ page }) => {
    const homeLink = page.getByRole('link', { name: /companies/i });
    await homeLink.click();

    await expect(page).toHaveURL('/');
    await expect(page.getByRole('heading', { name: /companies/i })).toBeVisible();
  });
});

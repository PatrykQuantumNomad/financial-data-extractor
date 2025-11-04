import { test, expect } from '@playwright/test';

test.describe('Home Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should display the home page with correct title', async ({ page }) => {
    await expect(page).toHaveTitle(/Financial Data Extractor/i);
  });

  test('should render the navbar with logo and navigation links', async ({ page }) => {
    // Check navbar is visible
    const navbar = page.getByRole('navigation');
    await expect(navbar).toBeVisible();

    // Check logo
    const logo = page.getByAltText(/Financial Data Extractor Logo/i);
    await expect(logo).toBeVisible();

    // Check navigation links
    await expect(page.getByRole('link', { name: /companies/i })).toBeVisible();
    await expect(page.getByRole('link', { name: /extraction/i })).toBeVisible();
  });

  test('should display the Companies heading', async ({ page }) => {
    await expect(page.getByRole('heading', { name: /companies/i })).toBeVisible();
  });

  test('should navigate to extraction page from navbar', async ({ page }) => {
    const extractionLink = page.getByRole('link', { name: /extraction/i });
    await extractionLink.click();

    await expect(page).toHaveURL(/\/extraction/);
    await expect(page.getByRole('heading', { name: /data extraction/i })).toBeVisible();
  });

  test('should navigate back to home from navbar logo', async ({ page }) => {
    // Navigate to extraction first
    await page.goto('/extraction');

    // Click on logo/home link
    const homeLink = page.getByText(/Financial Data Extractor/i).first();
    await homeLink.click();

    await expect(page).toHaveURL('/');
    await expect(page.getByRole('heading', { name: /companies/i })).toBeVisible();
  });
});

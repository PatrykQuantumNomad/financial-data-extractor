# End-to-End (E2E) Tests

This directory contains Playwright end-to-end tests for the Financial Data Extractor frontend application.

## Overview

E2E tests verify the complete user flows and interactions across the entire application, including:

- Page navigation and routing
- Component rendering and interactions
- API integration and data loading
- Error handling and edge cases
- User interface consistency

## Running Tests

### Run all E2E tests

```bash
npm run test:e2e
```

### Run tests in UI mode (interactive)

```bash
npm run test:e2e:ui
```

### Run tests in headed mode (see browser)

```bash
npm run test:e2e:headed
```

### Debug tests

```bash
npm run test:e2e:debug
```

### View test report

```bash
npm run test:e2e:report
```

## Prerequisites

### Backend API

For full E2E testing, the backend API should be running. The tests expect:

- API available at `http://localhost:3030` (default)
- Database seeded with test data (optional - tests handle empty states)

### Frontend Server

The Playwright config automatically starts the Next.js dev server at `http://localhost:3000` before running tests. If a server is already running, it will be reused (unless in CI mode).

## Test Configuration

Configuration is in `playwright.config.ts` at the project root. Key settings:

- **Base URL**: `http://localhost:3000`
- **Browser**: Chromium (can be extended to Firefox/WebKit)
- **Retries**: 2 retries on CI, 0 locally
- **Artifacts**: Screenshots, videos, and traces on failure

## Writing Tests

### Basic Test Structure

```typescript
import { test, expect } from "@playwright/test";

test.describe("Feature Name", () => {
  test("should do something", async ({ page }) => {
    await page.goto("/");
    await expect(
      page.getByRole("heading", { name: /something/i })
    ).toBeVisible();
  });
});
```

### Best Practices

1. **Use semantic selectors**: Prefer `getByRole`, `getByLabel`, `getByText` over CSS selectors
2. **Wait for network idle**: Use `await page.waitForLoadState('networkidle')` when waiting for API calls
3. **Handle conditional content**: Tests should gracefully handle cases where data might not exist
4. **Use test annotations**: Mark skipped tests with annotations for clarity
5. **Test user flows**: Focus on testing what users actually do, not implementation details

### API Mocking

For tests that don't require a real backend, you can mock API responses:

```typescript
test("should display mocked data", async ({ page }) => {
  await page.route("**/api/v1/companies", async (route) => {
    await route.fulfill({
      status: 200,
      body: JSON.stringify([{ id: 1, name: "Test Company" }]),
    });
  });

  await page.goto("/");
  // ... assertions
});
```

## CI/CD Integration

In CI environments:

- Tests run in headless mode
- Browsers are installed automatically
- Test results are published as artifacts
- Retries are enabled (2 attempts)

## Debugging Failed Tests

1. **Check test report**: Run `npm run test:e2e:report` to view HTML report
2. **View traces**: Traces are captured on first retry - use Playwright trace viewer
3. **Run in headed mode**: Use `npm run test:e2e:headed` to see what's happening
4. **Use debug mode**: Use `npm run test:e2e:debug` to step through tests

## Troubleshooting

### Tests fail because backend is not available

- Ensure backend is running at `http://localhost:3030`
- Or mock API responses in your tests

### Tests are flaky

- Add explicit waits for dynamic content
- Use `waitForLoadState('networkidle')` for API-dependent pages
- Increase timeouts if needed (but prefer fixing root cause)

### Browser not found

Run: `npx playwright install chromium`

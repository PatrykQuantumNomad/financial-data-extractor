---
layout: default
title: Frontend Testing
description: Vitest unit testing setup, React Testing Library, and frontend testing strategies
parent: Testing Overview
nav_order: 3
---

# Frontend Testing

The Financial Data Extractor frontend uses **Vitest** and **React Testing Library** for comprehensive unit testing of React components, ensuring reliability, maintainability, and confidence in code changes.

## Overview

The frontend testing setup provides:

- **Fast Unit Tests**: Vitest's blazing-fast test execution with minimal configuration
- **Component Testing**: React Testing Library for user-centric component testing
- **Integration Testing**: Component + hooks and API + hooks integration tests
- **End-to-End Testing**: Playwright for complete user workflow testing
- **100% Coverage**: Target coverage for UI components and utilities
- **Type Safety**: Full TypeScript support with type checking in tests

## Technology Stack

### Testing Framework

#### Unit & Integration Testing

- **Vitest** - Fast, Vite-native unit test framework
- **React Testing Library** - Component testing utilities
- **@testing-library/jest-dom** - Custom DOM matchers (toBeInTheDocument, etc.)
- **@testing-library/user-event** - User interaction simulation
- **jsdom** - DOM environment for running tests in Node.js
- **@vitest/ui** - Interactive test UI for better debugging
- **@vitest/coverage-v8** - Code coverage reporting

#### End-to-End Testing

- **Playwright** - Modern browser automation framework
- **TypeScript** - Type-safe E2E test authoring
- **Auto-Server Management** - Automatic FastAPI and Next.js startup

## Project Structure

Tests are organized in the `tests/` directory, mirroring the `src/` structure:

```text
frontend/
├── src/
│   ├── components/
│   │   ├── ui/
│   │   │   ├── button.tsx
│   │   │   ├── card.tsx
│   │   │   └── ...
│   │   └── layout/
│   │       └── navbar.tsx
│   └── lib/
│       └── utils.ts
├── tests/
│   ├── components/
│   │   ├── ui/
│   │   │   ├── button.test.tsx
│   │   │   ├── card.test.tsx
│   │   │   └── ...
│   │   └── layout/
│   │       └── navbar.test.tsx
│   ├── vitest.config.mjs
│   └── vitest.setup.ts
└── package.json
```

### Why Separate Tests Directory?

- **Clean Separation**: Keeps test code separate from source code
- **Better Organization**: Easier to find and maintain tests
- **Parallel Structure**: Mirrors `src/` organization for clarity
- **Professional Standard**: Aligns with industry best practices

## Configuration

### Vitest Configuration

The main configuration is in `tests/vitest.config.mjs`:

```javascript
import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: "jsdom",
    setupFiles: [path.resolve(__dirname, "./vitest.setup.ts")],
    transformMode: {
      web: [/\.tsx?$/, /\.jsx?$/],
      ssr: [/\.tsx?$/, /\.jsx?$/],
    },
    coverage: {
      provider: "v8",
      reporter: ["text", "json", "html"],
      exclude: [
        "node_modules/",
        "tests/",
        "**/*.test.{ts,tsx}",
        "**/*.spec.{ts,tsx}",
        "**/__tests__/**",
        "**/.next/**",
        "**/coverage/**",
        "**/*.config.{ts,js}",
        "**/*.d.ts",
        "next.config.js",
        "tailwind.config.ts",
        "postcss.config.mjs",
        "eslint.config.mjs",
      ],
    },
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "../src"),
      "@/lib": path.resolve(__dirname, "../src/lib"),
      "@/types": path.resolve(__dirname, "../src/types"),
      "@/components": path.resolve(__dirname, "../src/components"),
    },
  },
});
```

**Key Configuration Features:**

- **React Plugin**: Enables JSX/TSX transformation
- **jsdom Environment**: Provides browser-like DOM for tests
- **Path Aliases**: Same aliases as `src/` for consistent imports
- **Coverage**: v8 provider with text, JSON, and HTML reporters
- **Transform Mode**: Supports both web and SSR transformations

### Setup File

`tests/vitest.setup.ts` configures global test environment:

```typescript
import "@testing-library/jest-dom";
import { cleanup } from "@testing-library/react";
import { afterEach, vi } from "vitest";
import React from "react";

// Cleanup after each test
afterEach(() => {
  cleanup();
});

// Mock Next.js modules
vi.mock("next/image", () => ({
  default: (props: any) => {
    const { priority, ...imgProps } = props;
    return React.createElement("img", imgProps);
  },
}));

vi.mock("next/link", () => ({
  default: ({ children, href, ...props }: any) => {
    return React.createElement("a", { href, ...props }, children);
  },
}));

vi.mock("next/navigation", () => ({
  useRouter: () => ({
    push: vi.fn(),
    replace: vi.fn(),
    prefetch: vi.fn(),
    back: vi.fn(),
  }),
  usePathname: () => "/",
  useSearchParams: () => new URLSearchParams(),
}));
```

**Setup Features:**

- **jest-dom Matchers**: Adds custom matchers like `toBeInTheDocument`
- **Automatic Cleanup**: Cleans up DOM after each test
- **Next.js Mocks**: Mocks Image, Link, and navigation modules
- **React Import**: Required for `React.createElement` in mocks

## Running Tests

### NPM Scripts

```bash
# Run tests in watch mode (default)
npm test

# Run tests once
npm test -- --run

# Run tests with UI
npm run test:ui

# Generate coverage report
npm run test:coverage

# Watch mode (same as npm test)
npm run test:watch
```

### Command-Line Options

```bash
# Run specific test file
npm test -- tests/components/ui/button.test.tsx

# Run tests in a directory
npm test -- tests/components/ui/

# Update snapshots
npm test -- -u

# Run in coverage mode
npm test -- --coverage

# Run with specific reporter
npm test -- --reporter=verbose
```

## Writing Tests

### Basic Test Structure

Following the **AAA pattern** (Arrange, Act, Assert):

```typescript
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { Button } from "@/components/ui/button";

describe("Button", () => {
  it("renders with default variant", () => {
    // Arrange: Render the component
    render(<Button>Click me</Button>);

    // Act: Query for elements (implicit in Assert)
    const button = screen.getByRole("button", { name: /click me/i });

    // Assert: Verify the expected outcome
    expect(button).toBeInTheDocument();
    expect(button).toHaveClass("bg-primary");
  });
});
```

### Testing User Interactions

```typescript
import userEvent from "@testing-library/user-event";

it("handles click events", async () => {
  const handleClick = vi.fn();
  const user = userEvent.setup();

  render(<Button onClick={handleClick}>Click me</Button>);
  const button = screen.getByRole("button");

  await user.click(button);

  expect(handleClick).toHaveBeenCalledTimes(1);
});
```

### Testing Variants and Props

```typescript
it("renders different variants", () => {
  const { rerender } = render(<Button variant="destructive">Delete</Button>);
  let button = screen.getByRole("button");
  expect(button).toHaveClass("bg-destructive");

  rerender(<Button variant="outline">Outline</Button>);
  button = screen.getByRole("button");
  expect(button).toHaveClass("border-input");
});
```

### Testing Accessibility

```typescript
it("is accessible", () => {
  render(<Button>Accessible Button</Button>);

  const button = screen.getByRole("button");

  // Check keyboard accessibility
  expect(button).toHaveAttribute("type", "button");

  // Check disabled state
  expect(button).not.toBeDisabled();
});
```

### Testing Component Composition

```typescript
describe("Complete Card Structure", () => {
  it("renders all card components", () => {
    render(
      <Card>
        <CardHeader>
          <CardTitle>Test Title</CardTitle>
          <CardDescription>Test Description</CardDescription>
        </CardHeader>
        <CardContent>Test Content</CardContent>
        <CardFooter>Test Footer</CardFooter>
      </Card>
    );

    expect(screen.getByText("Test Title")).toBeInTheDocument();
    expect(screen.getByText("Test Description")).toBeInTheDocument();
    expect(screen.getByText("Test Content")).toBeInTheDocument();
    expect(screen.getByText("Test Footer")).toBeInTheDocument();
  });
});
```

## Current Test Coverage

### Unit Tests

**Location:** `frontend/tests/components/`, `frontend/tests/lib/`

**Status:** ✅ **Comprehensive unit test coverage** for UI components, hooks, API clients, and utilities

#### UI Components

✅ **Button Component** - 10 tests

- Variants (default, destructive, outline, secondary, ghost, link)
- Sizes (default, sm, lg, icon)
- Click events and keyboard interactions
- Disabled state
- asChild prop
- Custom className

✅ **Badge Component** - 8 tests

- Variants (default, secondary, destructive, outline)
- Custom className and props
- Focus styles
- Default styling

✅ **Card Components** - 18 tests

- Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter
- Correct HTML elements (div, h3, p, etc.)
- Styling and layout
- Complete card structure

✅ **Table Components** - 16 tests

- Table wrapper and elements
- TableHeader, TableBody, TableHead, TableRow, TableCell
- Proper HTML structure
- Hover styles and alignment

✅ **Tabs Components** - 6 tests

- TabsList, TabsTrigger, TabsContent
- Styling and layout
- Tab navigation and switching

#### Layout Components

✅ **Navbar Component** - 7 tests

- Logo and title rendering
- Navigation links
- Styling and layout
- Hover effects

#### Dashboard Components

✅ **CompanyList Component** - Unit tests for company listing

- Loading states
- Error handling
- Empty states
- Company card rendering

#### Statement Components

✅ **StatementError Component** - Error handling for statements
✅ **StatementTypeNav Component** - Statement type navigation
✅ **StatementPageLoading Component** - Loading states

#### API Client Tests

✅ **Companies API** - API client tests for company operations
✅ **Documents API** - Document listing and retrieval
✅ **Statements API** - Compiled statement retrieval
✅ **Tasks API** - Task status and triggering

#### React Query Hooks Tests

✅ **useCompanies** - Company data fetching hooks
✅ **useDocuments** - Document data fetching hooks
✅ **useStatements** - Statement data fetching hooks
✅ **useTasks** - Task mutation and status hooks

#### Utility Tests

✅ **formatters** - Currency, number, and percentage formatting
✅ **query-utils** - React Query utility functions

### Integration Tests

**Location:** `frontend/tests/integration/`

**Status:** ✅ **Integration tests** for components + hooks and API + hooks workflows

#### Component + Hooks Integration

✅ **Components with React Query** - Tests that components properly integrate with hooks

- `CompanyList` with `useCompanies` hook
- `StatementPageContent` with statement and company hooks
- Loading states and error handling
- Empty states

**Example Test:**

```typescript
it("should render companies after loading", async () => {
  mockApiClient.get.mockResolvedValue({ data: mockCompanies });
  const wrapper = createWrapper(queryClient);
  render(<CompanyList />, { wrapper });

  await waitFor(() => {
    expect(screen.getByText("Test Company 1")).toBeInTheDocument();
  });
});
```

#### API + Hooks Integration

✅ **Hooks with API Client** - Tests that hooks properly fetch and cache data

- `useCompanies`, `useCompany`, `useCompanyByTicker`
- `useDocumentsByCompany`, `useDocument`
- `useStatementsByCompany`, `useStatementByCompanyAndType`
- `useTaskStatus` with polling

**Key Test Scenarios:**

- Loading states during data fetching
- Error handling for 404s and API failures
- Query key consistency and caching
- Conditional queries (enabled based on parameters)

**Example Test:**

```typescript
it("useCompanies should fetch and return all companies", async () => {
  mockApiClient.get.mockResolvedValue({ data: mockCompanies });
  const wrapper = createWrapper(queryClient);
  const { result } = renderHook(() => useCompanies(), { wrapper });

  await waitFor(() => expect(result.current.isSuccess).toBe(true));
  expect(result.current.data).toHaveLength(2);
});
```

### Coverage Statistics

```text
Unit Tests:
  - UI Components: 65 tests (100% coverage)
  - API Clients: Full coverage
  - React Query Hooks: Full coverage
  - Utilities: Full coverage

Integration Tests:
  - Component + Hooks: Multiple test scenarios
  - API + Hooks: Comprehensive hook testing

Total: 100+ tests, all passing
```

## Testing Best Practices

### 1. Test User Behavior, Not Implementation

```typescript
// ❌ Bad - testing implementation
expect(component.state.count).toBe(1);

// ✅ Good - testing user-visible behavior
expect(screen.getByText("Count: 1")).toBeInTheDocument();
```

### 2. Use Accessible Queries

```typescript
// ✅ Best - queries by accessible role
screen.getByRole("button", { name: /submit/i });

// ✅ Good - queries by text
screen.getByText("Submit");

// ⚠️ OK - queries by test ID (last resort)
screen.getByTestId("submit-button");
```

### 3. Write Descriptive Test Names

```typescript
// ❌ Bad
it("works", () => { ... });
it("renders button", () => { ... });

// ✅ Good
it("renders a button with default variant", () => { ... });
it("handles click events and calls onClick handler", () => { ... });
it("displays error message when API request fails", () => { ... });
```

### 4. Keep Tests Isolated

Each test should be independent and not rely on state from other tests:

```typescript
it("handles click events", async () => {
  const handleClick = vi.fn(); // Fresh mock for each test
  render(<Button onClick={handleClick}>Click</Button>);
  // ...
});
```

### 5. Use Screen for Queries

Always use `screen` from React Testing Library:

```typescript
// ✅ Good
import { screen } from "@testing-library/react";
const button = screen.getByRole("button");

// ❌ Bad
const { getByRole } = render(<Button />);
const button = getByRole("button");
```

### 6. Clean Up After Tests

Vitest automatically cleans up after each test via the setup file, but be explicit about cleanup when needed:

```typescript
afterEach(() => {
  cleanup(); // Already handled by setup file
});
```

## Common Patterns

### Testing Async Operations

```typescript
it("handles async user interactions", async () => {
  const user = userEvent.setup();

  render(<ComponentWithAsyncAction />);

  const button = screen.getByRole("button");
  await user.click(button);

  // Wait for async update
  const result = await screen.findByText("Loading complete");
  expect(result).toBeInTheDocument();
});
```

### Testing Conditional Rendering

```typescript
it("renders different content based on props", () => {
  const { rerender } = render(<Component isLoading={true} />);
  expect(screen.getByText("Loading...")).toBeInTheDocument();

  rerender(<Component isLoading={false} data="Hello" />);
  expect(screen.queryByText("Loading...")).not.toBeInTheDocument();
  expect(screen.getByText("Hello")).toBeInTheDocument();
});
```

### Testing Error States

```typescript
it("displays error message on failure", () => {
  render(<Component error="Something went wrong" />);

  expect(screen.getByText("Something went wrong")).toBeInTheDocument();
  expect(screen.getByRole("alert")).toHaveClass("text-destructive");
});
```

## Debugging Tests

### Using Vitest UI

Launch the interactive test UI:

```bash
npm run test:ui
```

Features:

- **Live Test Results**: See tests pass/fail in real-time
- **Filter Tests**: Search and filter by test name or file
- **Code Coverage**: View coverage overlays
- **Console Output**: See console.log and errors
- **Snapshot Diff**: Visual snapshot comparisons

### Debugging Tips

1. **Use `screen.debug()`**: Print the current DOM

   ```typescript
   render(<Component />);
   screen.debug(); // Prints entire DOM
   ```

2. **Use `screen.debug(element)`**: Print specific element

   ```typescript
   const button = screen.getByRole("button");
   screen.debug(button); // Prints just the button
   ```

3. **Log Queries**: See what queries are available

   ```typescript
   render(<Component />);
   console.log(screen.getAllByRole("button")); // See all buttons
   ```

4. **Use `--reporter=verbose`**: Get detailed test output
   ```bash
   npm test -- --reporter=verbose
   ```

## Integration Testing Details

### Component + Hooks Integration

Tests verify that React components properly use React Query hooks and handle all states:

**Test Coverage:**

1. **Loading States**: Components show loading skeletons while data is fetched
2. **Success States**: Components render data correctly after successful API calls
3. **Error States**: Components display error messages when API calls fail
4. **Empty States**: Components handle empty data gracefully
5. **Navigation**: Links and routing work correctly with dynamic data

**Test Setup:**

```typescript
// Mock API client
vi.mock("@/lib/api/client", () => ({
  apiClient: { get: vi.fn(), post: vi.fn() },
}));

// Create React Query wrapper
function createWrapper(queryClient: QueryClient) {
  return ({ children }: { children: ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
}
```

### API + Hooks Integration

Tests verify that React Query hooks properly integrate with API clients:

**Test Coverage:**

1. **Query Execution**: Hooks call correct API endpoints with proper parameters
2. **Loading States**: `isLoading` and `isFetching` states are correct
3. **Error Handling**: Hooks handle API errors (404s, network errors) gracefully
4. **Caching**: Query keys are consistent and caching works correctly
5. **Conditional Queries**: Queries are disabled/enabled based on parameters
6. **Retry Logic**: Hooks don't retry on 404 errors (expected failures)

**Key Testing Patterns:**

```typescript
// Test query execution
it("useCompany should fetch company by id", async () => {
  mockApiClient.get.mockResolvedValue({ data: company });
  const { result } = renderHook(() => useCompany(1), { wrapper });

  await waitFor(() => expect(result.current.isSuccess).toBe(true));
  expect(mockApiClient.get).toHaveBeenCalledWith("/companies/1");
});

// Test error handling
it("useCompany should handle 404 errors gracefully", async () => {
  const apiError = new Error("Company not found");
  (apiError as any).status = 404;
  mockApiClient.get.mockRejectedValue(apiError);

  const { result } = renderHook(() => useCompany(999), { wrapper });
  await waitFor(() => expect(result.current.isError).toBe(true));
});
```

### Test Structure

Integration tests are organized in `tests/integration/`:

```
tests/integration/
├── components.test.tsx      # Component + hooks integration
├── api-hooks.test.tsx       # API + hooks integration
├── setup.ts                 # Test utilities and helpers
└── mocks/                   # Shared mock data
```

## End-to-End (E2E) Testing with Playwright

The frontend uses **Playwright** for end-to-end testing, providing comprehensive coverage of complete user workflows across the entire application stack.

### Overview

E2E tests verify the complete user experience, including:

- **Page Navigation**: Routing and navigation between pages
- **Component Rendering**: Full page rendering with real data
- **API Integration**: Real backend API calls and responses
- **User Interactions**: Clicks, form submissions, and keyboard navigation
- **Error Handling**: 404 pages, error states, and edge cases
- **Cross-Component Workflows**: Complete user journeys

### Technology Stack

- **Playwright** - Modern browser automation framework
- **TypeScript** - Type-safe test authoring
- **Auto-Server Management** - Automatic FastAPI and Next.js server startup

### Project Structure

E2E tests are organized in the `tests/e2e/` directory:

```text
frontend/
├── tests/
│   ├── e2e/                      # End-to-end tests
│   │   ├── home.spec.ts          # Home page tests
│   │   ├── navigation.spec.ts    # Navigation flows
│   │   ├── error-pages.spec.ts   # Error page tests
│   │   ├── company-statements.spec.ts  # Statement pages
│   │   ├── extraction.spec.ts    # Extraction page
│   │   ├── README.md             # E2E testing guide
│   │   └── ...
│   └── integration/              # Integration tests (Vitest)
└── playwright.config.ts          # Playwright configuration
```

### Configuration

The Playwright configuration (`playwright.config.ts`) includes:

```typescript
import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "./tests/e2e",

  // Parallel test execution
  fullyParallel: true,

  // CI-specific settings
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,

  // Reporters
  reporter: [
    ["html"],
    ["list"],
    ["json", { outputFile: "test-results/results.json" }],
  ],

  // Shared settings
  use: {
    baseURL: "http://localhost:3000",
    trace: "on-first-retry",
    screenshot: "only-on-failure",
    video: "retain-on-failure",
    actionTimeout: 10000,
  },

  // Browser projects
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
  ],

  // Web servers - automatically starts backend and frontend
  webServer: [
    // FastAPI backend (port 3030)
    {
      command: "cd ../backend && uv run python run.py",
      url: "http://localhost:3030/healthcheck",
      reuseExistingServer: !process.env.CI,
      stdout: "pipe",
      stderr: "pipe",
      timeout: 120 * 1000,
    },
    // Next.js frontend (port 3000)
    {
      command: "npm run dev",
      url: "http://localhost:3000",
      reuseExistingServer: !process.env.CI,
      stdout: "ignore",
      stderr: "pipe",
      timeout: 120 * 1000,
    },
  ],
});
```

**Key Features:**

- **Automatic Server Management**: Starts FastAPI backend and Next.js frontend before tests
- **Health Checks**: Waits for both servers to be ready before running tests
- **Reuse Existing Servers**: Reuses running servers in development (disabled in CI)
- **Artifact Collection**: Screenshots, videos, and traces on test failures
- **CI Optimization**: Adjusts retries, workers, and server management for CI environments

### Running E2E Tests

#### NPM Scripts

```bash
# Run all E2E tests
npm run test:e2e

# Run tests in interactive UI mode
npm run test:e2e:ui

# Run tests with visible browser (headed mode)
npm run test:e2e:headed

# Debug tests (step through with inspector)
npm run test:e2e:debug

# View test report
npm run test:e2e:report
```

#### Command-Line Options

```bash
# Run specific test file
npx playwright test tests/e2e/home.spec.ts

# Run tests matching a pattern
npx playwright test --grep "navigation"

# Run in headed mode
npx playwright test --headed

# Run on specific browser
npx playwright test --project=chromium

# Run with trace
npx playwright test --trace on
```

### Prerequisites

Before running E2E tests, ensure:

1. **Backend Dependencies**: PostgreSQL and Redis must be running

   - The FastAPI backend requires these services to start
   - Tests will fail if the backend cannot connect

2. **Node.js Version**: Node.js 22+ (see `.nvmrc` file)

3. **Browser Installation**: Playwright browsers installed
   ```bash
   npx playwright install chromium
   ```

### Test Structure

E2E tests follow Playwright's best practices:

#### Basic Test Example

```typescript
import { test, expect } from "@playwright/test";

test.describe("Home Page", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/");
  });

  test("should display the home page with correct title", async ({ page }) => {
    await expect(page).toHaveTitle(/Financial Data Extractor/i);
  });

  test("should render the navbar with navigation links", async ({ page }) => {
    const navbar = page.getByRole("navigation");
    await expect(navbar).toBeVisible();

    await expect(page.getByRole("link", { name: /companies/i })).toBeVisible();
    await expect(page.getByRole("link", { name: /extraction/i })).toBeVisible();
  });
});
```

#### Testing Navigation

```typescript
test("should navigate to extraction page from navbar", async ({ page }) => {
  await page.goto("/");

  const extractionLink = page.getByRole("link", { name: /extraction/i });
  await extractionLink.click();

  await expect(page).toHaveURL(/\/extraction/);
  await expect(
    page.getByRole("heading", { name: /data extraction/i })
  ).toBeVisible();
});
```

#### Testing with API Data

```typescript
test("should display companies from API", async ({ page }) => {
  await page.goto("/");

  // Wait for API call to complete
  await page.waitForLoadState("networkidle");

  // Check if companies are displayed (may be empty)
  const companiesCard = page.locator('[data-testid="company-card"]').first();
  const hasCompanies = await companiesCard.isVisible().catch(() => false);

  if (hasCompanies) {
    await expect(companiesCard).toBeVisible();
  } else {
    // Handle empty state gracefully
    const emptyMessage = page.getByText(/no companies found/i);
    await expect(emptyMessage).toBeVisible();
  }
});
```

#### Testing Error Pages

```typescript
test("should display 404 page for invalid company ID", async ({ page }) => {
  await page.goto("/companies/99999/statements/income_statement");

  await expect(page.getByText(/404/i)).toBeVisible();
  await expect(page.getByText(/page not found/i)).toBeVisible();

  // Test navigation back to home
  const homeButton = page.getByRole("link", { name: /back to home/i });
  await homeButton.click();
  await expect(page).toHaveURL("/");
});
```

### Current Test Coverage

**Status:** ✅ **E2E test suite** covering core user workflows

#### Home Page Tests (`home.spec.ts`)

- Page title and metadata
- Navbar rendering and navigation
- Company list display
- Navigation to extraction page
- Logo/home link functionality

#### Navigation Tests (`navigation.spec.ts`)

- Navigation between main pages
- Consistent navbar across pages
- URL routing and page transitions

#### Error Page Tests (`error-pages.spec.ts`)

- 404 page for invalid routes
- 404 page for non-existent companies
- Navigation back from error pages
- Invalid statement type handling

#### Company Statement Tests (`company-statements.spec.ts`)

- Navigation to statement pages from company list
- Loading states for statement pages
- Error handling for non-existent companies
- Support for different statement types (income, balance, cash flow)

#### Extraction Page Tests (`extraction.spec.ts`)

- Extraction page rendering
- Company selection functionality
- Empty state handling
- Navigation flows

### Best Practices

#### 1. Use Semantic Selectors

```typescript
// ✅ Good - accessible and user-focused
page.getByRole("button", { name: /submit/i });
page.getByLabel("Email address");
page.getByText("Welcome");

// ⚠️ OK - test ID when needed
page.getByTestId("submit-button");

// ❌ Bad - fragile CSS selectors
page.locator(".btn-primary");
```

#### 2. Wait for Network Idle

```typescript
// ✅ Good - wait for API calls to complete
await page.goto("/");
await page.waitForLoadState("networkidle");

// ❌ Bad - assume instant loading
await page.goto("/");
// API might not be ready yet
```

#### 3. Handle Conditional Content

```typescript
// ✅ Good - gracefully handle empty states
const viewStatementsButton = page
  .getByRole("button", { name: /view statements/i })
  .first();
const hasCompanies = await viewStatementsButton.isVisible().catch(() => false);

if (hasCompanies) {
  await viewStatementsButton.click();
  // Test navigation...
} else {
  // Skip test or test empty state
  test.info().annotations.push({
    type: "skip",
    description: "No companies found in database",
  });
}
```

#### 4. Use Descriptive Test Names

```typescript
// ✅ Good
test("should navigate to extraction page from navbar when clicking extraction link", async ({
  page,
}) => {
  // ...
});

// ❌ Bad
test("navigation test", async ({ page }) => {
  // ...
});
```

#### 5. Test User Journeys

```typescript
// ✅ Good - complete user workflow
test("should complete company statement viewing workflow", async ({ page }) => {
  // 1. Navigate to home
  await page.goto("/");

  // 2. Find and click company
  await page
    .getByRole("button", { name: /view statements/i })
    .first()
    .click();

  // 3. Verify statement page loaded
  await expect(page).toHaveURL(
    /\/companies\/\d+\/statements\/income_statement/
  );

  // 4. Verify page content
  await expect(page.locator("main")).toBeVisible();
});
```

### Debugging E2E Tests

#### Using Playwright UI

```bash
npm run test:e2e:ui
```

Features:

- **Live Test Execution**: See tests run in real-time
- **Step Through**: Pause and inspect at each step
- **Time Travel**: Replay test execution
- **Trace Viewer**: View detailed execution traces
- **Screenshots/Videos**: Visual debugging of failures

#### Using Debug Mode

```bash
npm run test:e2e:debug
```

Opens Playwright Inspector to step through tests:

- **Breakpoints**: Pause at specific actions
- **DOM Inspection**: Inspect page state at any point
- **Console**: Access browser console
- **Network**: Monitor API requests

#### Viewing Test Reports

```bash
npm run test:e2e:report
```

Opens HTML report with:

- **Test Results**: Pass/fail status for all tests
- **Screenshots**: Visual evidence of failures
- **Videos**: Full test execution videos
- **Traces**: Detailed execution traces with timeline
- **Console Logs**: Browser console output

#### Common Debugging Commands

```typescript
// Print page content
await page.content();

// Take screenshot
await page.screenshot({ path: "debug.png" });

// Wait for specific element
await page.waitForSelector('[data-testid="element"]');

// Log network requests
page.on("request", (request) => console.log("Request:", request.url()));
page.on("response", (response) =>
  console.log("Response:", response.url(), response.status())
);

// Pause execution (opens inspector)
await page.pause();
```

### CI/CD Integration

E2E tests are configured for CI environments:

```yaml
# Example GitHub Actions workflow
- name: Install Playwright browsers
  run: npx playwright install --with-deps chromium

- name: Run E2E tests
  run: npm run test:e2e
  env:
    CI: true

- name: Upload test results
  if: always()
  uses: actions/upload-artifact@v3
  with:
    name: playwright-report
    path: playwright-report/
    retention-days: 30
```

**CI Optimizations:**

- **Retries**: 2 retries on failure
- **Single Worker**: Sequential execution for stability
- **Artifact Collection**: Screenshots, videos, and traces uploaded
- **Browser Installation**: Automatic with dependencies

### Troubleshooting

#### Tests Fail Because Backend Not Available

**Solution:** Ensure PostgreSQL and Redis are running before tests:

```bash
# Check services
docker ps  # If using Docker
# Or check locally running services

# Start services if needed
docker-compose up -d postgres redis
```

#### Tests Are Flaky

**Solutions:**

- Add explicit waits for dynamic content:

  ```typescript
  await page.waitForLoadState("networkidle");
  await page.waitForSelector('[data-testid="element"]');
  ```

- Increase timeouts for slow operations:

  ```typescript
  await expect(element).toBeVisible({ timeout: 10000 });
  ```

- Use `waitFor` instead of immediate checks:
  ```typescript
  await page.waitForResponse((response) =>
    response.url().includes("/api/v1/companies")
  );
  ```

#### Browser Not Found

**Solution:**

```bash
npx playwright install chromium
```

#### Server Startup Timeout

**Solutions:**

- Increase timeout in `playwright.config.ts`:

  ```typescript
  webServer: [
    {
      timeout: 180 * 1000, // 3 minutes
    },
  ];
  ```

- Check backend logs for startup issues
- Verify database connections are working

## Related Documentation

- **[Frontend Architecture](frontend/architecture.html)** - Component structure and patterns
- **[Frontend DevTools](frontend/devtools.html)** - React Query DevTools and ESLint

## Resources

### Unit & Integration Testing

- [Vitest Documentation](https://vitest.dev){:target="\_blank"}
- [React Testing Library](https://testing-library.com/react){:target="\_blank"}
- [Testing Library Queries](https://testing-library.com/docs/queries/about/){:target="\_blank"}
- [Common Mistakes](https://kentcdodds.com/blog/common-mistakes-with-react-testing-library){:target="\_blank"}
- [Vitest UI Documentation](https://vitest.dev/guide/ui){:target="\_blank"}

### End-to-End Testing

- [Playwright Documentation](https://playwright.dev){:target="\_blank"}
- [Playwright Best Practices](https://playwright.dev/docs/best-practices){:target="\_blank"}
- [Playwright Selectors](https://playwright.dev/docs/selectors){:target="\_blank"}
- [Playwright Debugging](https://playwright.dev/docs/debug){:target="\_blank"}
- [Playwright CI/CD Guide](https://playwright.dev/docs/ci){:target="\_blank"}

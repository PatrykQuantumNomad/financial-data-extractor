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
- **100% Coverage**: Target coverage for UI components and utilities
- **Type Safety**: Full TypeScript support with type checking in tests
- **Future-Ready**: Prepared for integration and E2E testing

## Technology Stack

### Testing Framework

- **Vitest** - Fast, Vite-native unit test framework
- **React Testing Library** - Component testing utilities
- **@testing-library/jest-dom** - Custom DOM matchers (toBeInTheDocument, etc.)
- **@testing-library/user-event** - User interaction simulation
- **jsdom** - DOM environment for running tests in Node.js
- **@vitest/ui** - Interactive test UI for better debugging
- **@vitest/coverage-v8** - Code coverage reporting

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

## Future Work

### Additional Integration Tests

- **Form Submissions**: End-to-end form workflows with React Query mutations
- **Cache Invalidation**: Testing cache updates after mutations
- **Optimistic Updates**: Testing optimistic UI updates

### E2E Testing

Future E2E testing will use:

- **Playwright** or **Cypress** for browser automation
- **User Journeys**: Complete workflows from page load to data submission
- **Cross-Browser**: Testing on Chrome, Firefox, Safari
- **Visual Regression**: Snapshot testing for UI changes

## Related Documentation

- **[Frontend Architecture](frontend/architecture.html)** - Component structure and patterns
- **[Frontend DevTools](frontend/devtools.html)** - React Query DevTools and ESLint

## Resources

- [Vitest Documentation](https://vitest.dev){:target="\_blank"}
- [React Testing Library](https://testing-library.com/react){:target="\_blank"}
- [Testing Library Queries](https://testing-library.com/docs/queries/about/){:target="\_blank"}
- [Common Mistakes](https://kentcdodds.com/blog/common-mistakes-with-react-testing-library){:target="\_blank"}
- [Vitest UI Documentation](https://vitest.dev/guide/ui){:target="\_blank"}

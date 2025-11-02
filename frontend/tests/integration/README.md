# Integration Tests

This directory contains Vitest integration tests for the frontend application.

## Overview

Integration tests verify that multiple layers of the application work together correctly:
- **API + Hooks**: Tests that React Query hooks properly integrate with API clients
- **Components + Hooks**: Tests that components correctly use hooks and render data
- **Error Handling**: Tests error propagation through the stack
- **Loading States**: Tests loading state flows
- **Data Flow**: Tests complete data transformation pipelines

## Test Structure

### Setup (`setup.ts`)
- Provides `createTestQueryClient()` for isolated React Query instances
- Provides `renderWithProviders()` helper for rendering components with QueryClient
- Configures test environment for integration testing

### API + Hooks Tests (`api-hooks.test.tsx`)
Tests the integration between API clients and React Query hooks:
- Companies hooks (useCompanies, useCompany, useCompanyByTicker)
- Documents hooks (useDocumentsByCompany, useDocument)
- Statements hooks (useStatementsByCompany, useStatementByCompanyAndType)
- Tasks hooks (useTaskStatus)
- Query key consistency and caching

### Component Tests (`components.test.tsx`)
Tests component rendering with real hooks:
- CompanyList component with useCompanies hook
- StatementPageContent component with useCompany and useStatementByCompanyAndType hooks
- Error states and loading states

## Running Integration Tests

```bash
# Run all integration tests
npm test -- tests/integration

# Run specific integration test file
npm test -- tests/integration/api-hooks.test.tsx

# Run in watch mode
npm test -- tests/integration --watch
```

## Differences from Unit Tests

**Unit Tests:**
- Mock React Query completely
- Test individual functions/components in isolation
- Faster execution

**Integration Tests:**
- Use real React Query with QueryClient
- Test multiple layers working together
- Mock only the API client (axios)
- Test React Query caching, error handling, and state management

## Mocking Strategy

Integration tests mock the `apiClient` (axios instance) rather than React Query hooks. This allows us to:
- Test real React Query behavior (caching, error handling, retries)
- Test hook implementations with real QueryClient
- Test component rendering with real hook data flow
- Verify query keys and cache invalidation work correctly

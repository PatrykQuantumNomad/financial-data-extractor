---
layout: default
title: Frontend DevTools
description: React Query DevTools, ESLint plugin, and frontend development debugging tools configuration
nav_order: 10
---

# Frontend DevTools

This document covers frontend-specific development tools used in the Next.js application to enhance the developer experience, enforce best practices, and enable powerful debugging capabilities.

## React Query DevTools

**Package**: `@tanstack/react-query-devtools`  
**Purpose**: Debug and monitor React Query (TanStack Query) queries, mutations, and cache state.

### Features

- **View Active Queries**: See all active queries and their status (loading, success, error)
- **Inspect Cache**: Browse the query cache and see cached data
- **Monitor Mutations**: Track mutation status and results
- **Query Invalidation**: See when queries are invalidated and refetched
- **Debug Query Keys**: Inspect query key structures and dependencies

### Configuration

The DevTools are configured in `src/lib/providers/query-provider.tsx`:

```typescript
<ReactQueryDevtools
  initialIsOpen={false} // Panel closed by default
  buttonPosition="bottom-left" // Position of toggle button
  position="bottom" // Position of panel when open
/>
```

### Usage

1. **Run the development server**: `npm run dev`
2. **Look for the floating button**: A small React Query logo appears in the bottom-left corner
3. **Click to open**: Opens a panel showing all queries, mutations, and cache state
4. **Inspect queries**: Click on any query to see its data, status, and metadata

### Additional Configuration Options

```typescript
<ReactQueryDevtools
  initialIsOpen={false}
  buttonPosition="bottom-left"
  position="bottom"
  errorTypes={[Error, TypeError]} // Filter error types
  styleNonce="your-nonce" // CSP nonce for security
  shadowDOMTarget={shadowRoot} // Embed in shadow DOM
  closeButtonProps={{ ariaLabel: "Close" }}
/>
```

### Production Builds

The DevTools are automatically excluded from production builds. They only appear when `process.env.NODE_ENV === "development"`.

## React DevTools

**Package**: `@tanstack/react-devtools`  
**Purpose**: General React debugging for concurrent features, components, hooks, and performance profiling.

### Features

- **Component Tree Inspection**: Debug React component hierarchies
- **Hook Debugging**: Inspect hook values and dependencies
- **Performance Profiling**: Analyze render performance
- **Concurrent Features**: Debug React 18+ concurrent rendering features

### Usage

The `@tanstack/react-devtools` package is available as a utility component in `src/lib/providers/react-devtools.tsx` if needed for advanced React debugging. It integrates with the React DevTools browser extension.

**Note**: This is separate from `@tanstack/react-query-devtools`, which is specifically for React Query debugging.

## ESLint Plugin for React Query

**Package**: `@tanstack/eslint-plugin-query`  
**Purpose**: Enforce React Query best practices and catch common mistakes during development.

### Configuration

The plugin is configured in `eslint.config.mjs` with recommended rules:

```javascript
import pluginQuery from "@tanstack/eslint-plugin-query";

export default defineConfig([
  // ... other configs
  ...pluginQuery.configs["flat/recommended"],
  // ... rest of config
]);
```

### Rules Enabled

The recommended configuration includes several important rules:

#### `@tanstack/query/exhaustive-deps`

Ensures all dependencies are included in query hook dependency arrays:

```typescript
// ❌ Bad - missing dependency
const { data } = useQuery({
  queryKey: ["company", companyId],
  queryFn: () => companiesApi.getById(companyId),
});

// ✅ Good - all dependencies included
const { data } = useQuery({
  queryKey: ["company", companyId],
  queryFn: () => companiesApi.getById(companyId),
});
```

#### `@tanstack/query/no-deprecated-options`

Warns about deprecated React Query options to ensure you're using the latest API:

```typescript
// ❌ Deprecated
useQuery({
  cacheTime: 5000, // Should use gcTime
  // ...
});

// ✅ Current API
useQuery({
  gcTime: 5000,
  // ...
});
```

#### `@tanstack/query/prefer-query-object-syntax`

Encourages using object syntax for queries for better readability:

```typescript
// ❌ Less readable
useQuery(["companies"], fetchCompanies);

// ✅ Better
useQuery({
  queryKey: ["companies"],
  queryFn: fetchCompanies,
});
```

#### `@tanstack/query/stable-query-client`

Ensures the query client instance is stable across renders to prevent unnecessary re-renders:

```typescript
// ❌ Creates new instance on every render
function MyComponent() {
  const queryClient = new QueryClient();
  // ...
}

// ✅ Stable instance
const queryClient = new QueryClient();

function MyComponent() {
  // ...
}
```

### Running ESLint

```bash
# Run ESLint
npm run lint

# Auto-fix issues where possible
npm run lint -- --fix
```

## Development Workflow

### 1. Start Development Server

```bash
npm run dev
```

### 2. Open React Query DevTools

- Look for the floating button in the bottom-left corner
- Click to open the DevTools panel
- Inspect queries, mutations, and cache state

### 3. Use ESLint for Code Quality

```bash
# Check for React Query issues
npm run lint

# Fix auto-fixable issues
npm run lint -- --fix
```

### 4. Monitor Query Performance

Use React Query DevTools to:

- Identify slow queries
- Check cache hit rates
- Debug query invalidation issues
- Optimize query key structures

## Common Debugging Scenarios

### Query Not Updating

**Symptoms**: Query shows stale data even after mutation

**Debug Steps**:

1. Check React Query DevTools → Queries tab
2. Verify query key matches what you're invalidating
3. Check if query is cached and not being invalidated
4. Look for query status (stale, fresh, fetching)

**Solution**:

```typescript
// Ensure query keys match exactly
const queryClient = useQueryClient();
queryClient.invalidateQueries({ queryKey: ["companies"] });
```

### Infinite Re-renders

**Symptoms**: Component re-renders continuously

**Debug Steps**:

1. Check React Query DevTools → Queries tab
2. Look for queries that are constantly refetching
3. Check query dependencies

**Solution**:

```typescript
// Use stable query keys and functions
const companyId = useMemo(() => id, [id]);
const { data } = useQuery({
  queryKey: ["company", companyId],
  queryFn: () => companiesApi.getById(companyId),
});
```

### Cache Not Working

**Symptoms**: Same query refetches even with cached data

**Debug Steps**:

1. Check `staleTime` and `gcTime` in QueryClient configuration
2. Verify query keys are consistent
3. Check if queries are being invalidated unnecessarily

**Solution**:

```typescript
// Configure appropriate cache times
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 60 * 1000, // 1 minute
      gcTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});
```

## Resources

- [React Query DevTools Documentation](https://tanstack.com/query/latest/docs/framework/react/devtools)
- [React Query ESLint Plugin Documentation](https://tanstack.com/query/v5/docs/eslint/eslint-plugin-query)
- [React DevTools](https://tanstack.com/router/latest/docs/framework/react/devtools)
- [React Query Best Practices](https://tanstack.com/query/latest/docs/react/guides/best-practices)

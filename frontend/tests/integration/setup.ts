import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, RenderOptions } from "@testing-library/react";
import React, { ReactElement, ReactNode } from "react";
import { afterEach, beforeEach, vi } from "vitest";

/**
 * Creates a new QueryClient for each test to ensure isolation
 */
export function createTestQueryClient() {
  return new QueryClient({
    defaultOptions: {
      queries: {
        // Disable automatic retries in tests for faster failure
        retry: false,
        // Disable cache for deterministic tests
        cacheTime: 0,
        staleTime: 0,
      },
      mutations: {
        retry: false,
      },
    },
  });
}

/**
 * Custom render function that wraps components with QueryClientProvider
 */
export function renderWithProviders(
  ui: ReactElement,
  options?: Omit<RenderOptions, "wrapper"> & {
    queryClient?: QueryClient;
  }
) {
  const queryClient = options?.queryClient ?? createTestQueryClient();

  function Wrapper({ children }: { children: ReactNode }) {
    return React.createElement(
      QueryClientProvider,
      { client: queryClient },
      children
    );
  }

  return {
    ...render(ui, { wrapper: Wrapper, ...options }),
    queryClient,
  };
}

/**
 * Helper to wait for queries to settle
 */
export async function waitForQueriesToSettle(queryClient: QueryClient) {
  // Wait for all queries to finish (success or error)
  await queryClient.getQueryCache().clear();
}

// Cleanup after each test
afterEach(() => {
  // Clear any pending timers
  vi.clearAllTimers();
});

// Setup before each test
beforeEach(() => {
  // Reset mocks if needed
  vi.clearAllMocks();
});

import { QueryClient, DefaultOptions } from "@tanstack/react-query";
import type { ApiError } from "@/lib/api/client";

const queryConfig: DefaultOptions = {
  queries: {
    // Prevent automatic refetching in certain conditions
    refetchOnWindowFocus: false,
    refetchOnReconnect: true,
    refetchOnMount: true,
    
    // Retry configuration
    retry: (failureCount, error) => {
      // Don't retry on 4xx errors except 429 (rate limit)
      const apiError = error as ApiError;
      if (apiError?.status) {
        if (apiError.status >= 400 && apiError.status < 500) {
          return apiError.status === 429 && failureCount < 3;
        }
      }
      // Retry 5xx errors up to 2 times
      return failureCount < 2;
    },
    
    // Default stale time - data is fresh for 1 minute
    staleTime: 60 * 1000,
    
    // Keep unused data in cache for 5 minutes
    gcTime: 5 * 60 * 1000,
  },
  mutations: {
    // Retry mutations only on network errors
    retry: (failureCount, error) => {
      const apiError = error as ApiError;
      return apiError?.code === "NETWORK_ERROR" && failureCount < 1;
    },
  },
};

export const queryClient = new QueryClient({
  defaultOptions: queryConfig,
});

// Type-safe query client hooks
export type { ApiError };

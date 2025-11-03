import type { ApiError } from "@/lib/api/client";
import {
  type UseMutationResult,
  type UseQueryResult,
} from "@tanstack/react-query";

/**
 * Utility type for better error typing in queries
 */
export type QueryError = ApiError;

/**
 * Extract error message from query or mutation error
 */
export function getErrorMessage(
  error: unknown,
  defaultMessage = "An error occurred"
): string {
  if (!error) return defaultMessage;

  const apiError = error as ApiError;
  if (apiError.message) {
    return apiError.message;
  }

  return defaultMessage;
}

/**
 * Check if query is loading (either initial fetch or refetch)
 */
export function isQueryLoading(query: UseQueryResult): boolean {
  return query.isLoading || query.isFetching;
}

/**
 * Check if a 404 error occurred (resource not found)
 */
export function isNotFoundError(error: unknown): boolean {
  return (error as ApiError)?.status === 404;
}

/**
 * Check if a network error occurred
 */
export function isNetworkError(error: unknown): boolean {
  return (error as ApiError)?.code === "NETWORK_ERROR";
}

/**
 * Check if an auth error occurred (401 or 403)
 */
export function isAuthError(error: unknown): boolean {
  const status = (error as ApiError)?.status;
  return status === 401 || status === 403;
}

/**
 * Type guard for checking if mutation is in progress
 */
export function isMutationPending(mutation: UseMutationResult): boolean {
  return mutation.isPending;
}

/**
 * Helper to safely get nested query data
 */
export function getQueryData<T>(query: UseQueryResult<T>): T | undefined {
  return query.data;
}

/**
 * Hook helper to combine multiple queries' loading states
 */
export function areManyQueriesLoading(...queries: UseQueryResult[]): boolean {
  return queries.some((query) => isQueryLoading(query));
}

/**
 * Hook helper to check if any query has an error
 */
export function doAnyQueriesHaveError(...queries: UseQueryResult[]): boolean {
  return queries.some((query) => query.isError);
}

/**
 * Hook helper to get all errors from multiple queries
 */
export function getAllQueryErrors(...queries: UseQueryResult[]): QueryError[] {
  return queries
    .filter((query) => query.isError && query.error)
    .map((query) => query.error as QueryError);
}

/**
 * Format bytes for file size display
 */
export function formatBytes(bytes: number, decimals = 2): string {
  if (bytes === 0) return "0 Bytes";

  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ["Bytes", "KB", "MB", "GB", "TB"];

  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + " " + sizes[i];
}

/**
 * Format date for display
 */
export function formatDate(dateString: string | null): string {
  if (!dateString) return "N/A";

  try {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    }).format(date);
  } catch {
    return dateString;
  }
}

/**
 * Create a debounced function
 */
export function debounce<T extends (...args: unknown[]) => unknown>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout;

  return function executedFunction(...args: Parameters<T>) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };

    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

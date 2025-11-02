import type { Company } from "@/lib/types";
import { vi } from "vitest";

export const mockCompanies: Company[] = [
  {
    id: 1,
    name: "Test Company 1",
    ir_url: "https://example.com/investor-relations",
    primary_ticker: "TEST1",
    tickers: null,
    created_at: "2024-01-01T00:00:00Z",
  },
  {
    id: 2,
    name: "Test Company 2",
    ir_url: "https://example2.com/investor-relations",
    primary_ticker: "TEST2",
    tickers: null,
    created_at: "2024-01-02T00:00:00Z",
  },
];

export const createMockUseCompanies = (overrides?: {
  data?: Company[];
  isLoading?: boolean;
  error?: unknown;
}) => {
  const mockData = overrides?.data ?? mockCompanies;
  const mockIsLoading = overrides?.isLoading ?? false;
  const mockError = overrides?.error ?? null;

  return vi.fn(() => ({
    data: mockData,
    isLoading: mockIsLoading,
    error: mockError,
    isFetching: mockIsLoading,
    isError: !!mockError,
    refetch: vi.fn(),
  }));
};

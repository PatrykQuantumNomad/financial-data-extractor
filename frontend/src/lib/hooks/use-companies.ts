import { companiesApi } from "@/lib/api/companies";
import { useQuery } from "@tanstack/react-query";
import { ApiError } from "../api/client";

// Query keys
export const companyKeys = {
  all: ["companies"] as const,
  lists: () => [...companyKeys.all, "list"] as const,
  list: (filters?: Record<string, unknown>) =>
    [...companyKeys.lists(), filters] as const,
  details: () => [...companyKeys.all, "detail"] as const,
  detail: (id: number) => [...companyKeys.details(), id] as const,
  ticker: (ticker: string) => [...companyKeys.all, "ticker", ticker] as const,
};

// Hooks
export function useCompanies() {
  return useQuery({
    queryKey: companyKeys.lists(),
    queryFn: () => companiesApi.getAll(),
    staleTime: 5 * 60 * 1000, // Consider data fresh for 5 minutes
  });
}

export function useCompany(id: number) {
  return useQuery({
    queryKey: companyKeys.detail(id),
    queryFn: () => companiesApi.getById(id),
    enabled: !!id && !isNaN(id),
    retry: (failureCount, error: any) => {
      // Don't retry on 404 errors (company doesn't exist)
      if ((error as ApiError)?.status === 404) {
        return false;
      }
      return failureCount < 1;
    },
    staleTime: 5 * 60 * 1000,
  });
}

export function useCompanyByTicker(ticker: string) {
  return useQuery({
    queryKey: companyKeys.ticker(ticker),
    queryFn: () => companiesApi.getByTicker(ticker),
    enabled: !!ticker,
    retry: (failureCount, error: any) => {
      if ((error as ApiError)?.status === 404) {
        return false;
      }
      return failureCount < 1;
    },
    staleTime: 5 * 60 * 1000,
  });
}

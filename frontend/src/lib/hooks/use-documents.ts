import { useQuery } from "@tanstack/react-query";
import { documentsApi } from "@/lib/api/documents";
import type { ApiError } from "@/lib/api/client";

// Query keys
export const documentKeys = {
  all: ["documents"] as const,
  lists: () => [...documentKeys.all, "list"] as const,
  byCompany: (companyId: number, filters?: Record<string, unknown>) =>
    [...documentKeys.lists(), "company", companyId, filters] as const,
  byCompanyAndYear: (companyId: number, fiscalYear: number) =>
    [...documentKeys.lists(), "company", companyId, "year", fiscalYear] as const,
  byCompanyAndType: (companyId: number, documentType: string, filters?: Record<string, unknown>) =>
    [
      ...documentKeys.lists(),
      "company",
      companyId,
      "type",
      documentType,
      filters,
    ] as const,
  detail: (id: number) => [...documentKeys.all, "detail", id] as const,
};

// Hooks
export function useDocument(id: number) {
  return useQuery({
    queryKey: documentKeys.detail(id),
    queryFn: () => documentsApi.getById(id),
    enabled: !!id && !isNaN(id),
    retry: (failureCount, error: any) => {
      // Don't retry on 404 errors (document doesn't exist)
      if ((error as ApiError)?.status === 404) {
        return false;
      }
      return failureCount < 1;
    },
    staleTime: 5 * 60 * 1000, // Consider data fresh for 5 minutes
  });
}

export function useDocumentsByCompany(
  companyId: number,
  options?: { skip?: number; limit?: number }
) {
  return useQuery({
    queryKey: documentKeys.byCompany(companyId, options),
    queryFn: () =>
      documentsApi.getByCompany(
        companyId,
        options?.skip ?? 0,
        options?.limit ?? 100
      ),
    enabled: !!companyId && !isNaN(companyId),
    staleTime: 5 * 60 * 1000,
  });
}

export function useDocumentsByCompanyAndYear(
  companyId: number,
  fiscalYear: number
) {
  return useQuery({
    queryKey: documentKeys.byCompanyAndYear(companyId, fiscalYear),
    queryFn: () => documentsApi.getByCompanyAndYear(companyId, fiscalYear),
    enabled: !!companyId && !isNaN(companyId) && !!fiscalYear,
    retry: (failureCount, error: any) => {
      // Don't retry on 404 errors
      if ((error as ApiError)?.status === 404) {
        return false;
      }
      return failureCount < 1;
    },
    staleTime: 5 * 60 * 1000,
  });
}

export function useDocumentsByCompanyAndType(
  companyId: number,
  documentType: string,
  options?: { skip?: number; limit?: number }
) {
  return useQuery({
    queryKey: documentKeys.byCompanyAndType(companyId, documentType, options),
    queryFn: () =>
      documentsApi.getByCompanyAndType(
        companyId,
        documentType,
        options?.skip ?? 0,
        options?.limit ?? 100
      ),
    enabled: !!companyId && !isNaN(companyId) && !!documentType,
    retry: (failureCount, error: any) => {
      // Don't retry on 404 errors
      if ((error as ApiError)?.status === 404) {
        return false;
      }
      return failureCount < 1;
    },
    staleTime: 5 * 60 * 1000,
  });
}

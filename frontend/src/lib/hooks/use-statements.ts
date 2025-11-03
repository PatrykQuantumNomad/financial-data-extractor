import type { ApiError } from "@/lib/api/client";
import { statementsApi } from "@/lib/api/statements";
import type { StatementType } from "@/lib/types";
import { useQuery } from "@tanstack/react-query";

// Query keys
export const statementKeys = {
  all: ["statements"] as const,
  lists: () => [...statementKeys.all, "list"] as const,
  byCompany: (companyId: number) =>
    [...statementKeys.lists(), "company", companyId] as const,
  byCompanyAndType: (companyId: number, statementType: StatementType) =>
    [
      ...statementKeys.lists(),
      "company",
      companyId,
      "type",
      statementType,
    ] as const,
  detail: (id: number) => [...statementKeys.all, "detail", id] as const,
};

// Hooks
export function useStatement(id: number) {
  return useQuery({
    queryKey: statementKeys.detail(id),
    queryFn: () => statementsApi.getById(id),
    enabled: !!id && !isNaN(id),
    retry: (failureCount, error: unknown) => {
      // Don't retry on 404 errors (statement doesn't exist)
      if ((error as ApiError)?.status === 404) {
        return false;
      }
      return failureCount < 1;
    },
    staleTime: 5 * 60 * 1000, // Consider data fresh for 5 minutes
  });
}

export function useStatementsByCompany(companyId: number) {
  return useQuery({
    queryKey: statementKeys.byCompany(companyId),
    queryFn: () => statementsApi.getByCompany(companyId),
    enabled: !!companyId && !isNaN(companyId),
    staleTime: 5 * 60 * 1000,
  });
}

export function useStatementByCompanyAndType(
  companyId: number,
  statementType: StatementType
) {
  return useQuery({
    queryKey: statementKeys.byCompanyAndType(companyId, statementType),
    queryFn: () => statementsApi.getByCompanyAndType(companyId, statementType),
    enabled: !!companyId && !isNaN(companyId) && !!statementType,
    retry: (failureCount, error: unknown) => {
      // Don't retry on 404 errors (statement doesn't exist yet - expected case)
      if ((error as ApiError)?.status === 404) {
        return false;
      }
      return failureCount < 1;
    },
    staleTime: 5 * 60 * 1000,
  });
}

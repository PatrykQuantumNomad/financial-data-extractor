import { documentsApi } from "@/lib/api/documents";
import { useQuery } from "@tanstack/react-query";
import { type ApiError } from "../api/client";

// Query keys
export const storagePdfKeys = {
  all: ["storage-pdfs"] as const,
  lists: () => [...storagePdfKeys.all, "list"] as const,
  list: (companyId: number, fiscalYear?: number) =>
    [...storagePdfKeys.lists(), companyId, fiscalYear] as const,
};

// Hooks
export function useStoragePdfs(companyId: number, fiscalYear?: number) {
  return useQuery({
    queryKey: storagePdfKeys.list(companyId, fiscalYear),
    queryFn: () => documentsApi.listStoragePdfs(companyId, fiscalYear),
    enabled: !!companyId && !isNaN(companyId),
    retry: (failureCount, error: unknown) => {
      // Don't retry on 404 errors
      if ((error as ApiError)?.status === 404) {
        return false;
      }
      return failureCount < 1;
    },
    staleTime: 2 * 60 * 1000, // Consider data fresh for 2 minutes
  });
}

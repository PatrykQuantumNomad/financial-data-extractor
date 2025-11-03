import { tasksApi } from "@/lib/api/tasks";
import type { TaskStatus } from "@/lib/types";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { companyKeys } from "./use-companies";
import { documentKeys } from "./use-documents";
import { statementKeys } from "./use-statements";

// Query keys
export const taskKeys = {
  all: ["tasks"] as const,
  status: (taskId: string) => [...taskKeys.all, "status", taskId] as const,
};

// Helper to check if task is in a terminal state
function isTaskComplete(status: TaskStatus["status"] | undefined): boolean {
  return status === "SUCCESS" || status === "FAILURE" || status === "REVOKED";
}

// Helper to check if task is running
function isTaskRunning(status: TaskStatus["status"] | undefined): boolean {
  return status === "PENDING" || status === "STARTED" || status === "RETRY";
}

// Hooks for task status polling
export function useTaskStatus(
  taskId: string,
  options?: {
    enabled?: boolean;
    refetchInterval?: number;
    onSuccess?: (data: TaskStatus) => void;
    onError?: (error: unknown) => void;
  }
) {
  return useQuery({
    queryKey: taskKeys.status(taskId),
    queryFn: () => tasksApi.getTaskStatus(taskId),
    enabled: options?.enabled !== false && !!taskId,

    refetchInterval: (query) => {
      const status = query.state.data?.status;

      // If task is complete, stop polling
      if (isTaskComplete(status)) {
        return false;
      }

      // If task is still running, continue polling
      if (isTaskRunning(status)) {
        return options?.refetchInterval ?? 2000;
      }

      // If no data yet (initial load), keep polling to get status
      return options?.refetchInterval ?? 2000;
    },
    // Ensure we refetch when component mounts
    refetchOnMount: true,
    // Keep polling even when window loses focus (important for background tasks)
    refetchOnWindowFocus: true,

    // Disable automatic retries for task status (we're polling anyway)
    retry: false,

    // Keep the last successful data while refetching
    placeholderData: (previousData) => previousData,
  });
}

/**
 * Hook for polling multiple tasks at once
 */
export function useTasksStatus(taskIds: string[]) {
  const results = taskIds.map((taskId) =>
    useTaskStatus(taskId, { enabled: !!taskId })
  );

  return {
    tasks: results.map((r) => r.data).filter(Boolean) as TaskStatus[],
    isAnyLoading: results.some((r) => r.isLoading),
    isAnyRunning: results.some((r) => isTaskRunning(r.data?.status)),
    allComplete: results.every((r) => isTaskComplete(r.data?.status)),
    errors: results.map((r) => r.error).filter(Boolean),
  };
}

// Mutation hooks for triggering tasks
export function useTriggerExtractCompany(options?: {
  onSuccess?: (data: unknown, companyId: number) => void;
  onError?: (error: unknown) => void;
}) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (companyId: number) =>
      tasksApi.triggerExtractCompany(companyId),
    onSuccess: (data, companyId) => {
      // Invalidate related queries after extraction
      void queryClient.invalidateQueries({ queryKey: companyKeys.all });
      void queryClient.invalidateQueries({ queryKey: documentKeys.all });
      void queryClient.invalidateQueries({ queryKey: statementKeys.all });

      options?.onSuccess?.(data, companyId);
    },
    onError: options?.onError,
  });
}

export function useTriggerScrapeCompany(options?: {
  onSuccess?: (data: unknown, companyId: number) => void;
  onError?: (error: unknown) => void;
}) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (companyId: number) => tasksApi.triggerScrapeCompany(companyId),
    onSuccess: (data, companyId) => {
      void queryClient.invalidateQueries({ queryKey: documentKeys.all });
      options?.onSuccess?.(data, companyId);
    },
    onError: options?.onError,
  });
}

export function useTriggerProcessAllDocuments(options?: {
  onSuccess?: (data: unknown, companyId: number) => void;
  onError?: (error: unknown) => void;
}) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (companyId: number) =>
      tasksApi.triggerProcessAllDocuments(companyId),
    onSuccess: (data, companyId) => {
      void queryClient.invalidateQueries({ queryKey: documentKeys.all });
      void queryClient.invalidateQueries({ queryKey: statementKeys.all });
      options?.onSuccess?.(data, companyId);
    },
    onError: options?.onError,
  });
}

export function useTriggerRecompileCompany(options?: {
  onSuccess?: (data: unknown, companyId: number) => void;
  onError?: (error: unknown) => void;
}) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (companyId: number) =>
      tasksApi.triggerRecompileCompany(companyId),
    onSuccess: (data, companyId) => {
      void queryClient.invalidateQueries({
        queryKey: statementKeys.byCompany(companyId),
      });
      options?.onSuccess?.(data, companyId);
    },
    onError: options?.onError,
  });
}

export function useTriggerDownloadDocument(options?: {
  onSuccess?: (data: unknown, documentId: number) => void;
  onError?: (error: unknown) => void;
}) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (documentId: number) =>
      tasksApi.triggerDownloadDocument(documentId),
    onSuccess: (data, documentId) => {
      void queryClient.invalidateQueries({ queryKey: documentKeys.all });
      options?.onSuccess?.(data, documentId);
    },
    onError: options?.onError,
  });
}

export function useTriggerClassifyDocument(options?: {
  onSuccess?: (data: unknown, documentId: number) => void;
  onError?: (error: unknown) => void;
}) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (documentId: number) =>
      tasksApi.triggerClassifyDocument(documentId),
    onSuccess: (data, documentId) => {
      void queryClient.invalidateQueries({ queryKey: documentKeys.all });
      options?.onSuccess?.(data, documentId);
    },
    onError: options?.onError,
  });
}

export function useTriggerExtractDocument(options?: {
  onSuccess?: (data: unknown, documentId: number) => void;
  onError?: (error: unknown) => void;
}) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (documentId: number) =>
      tasksApi.triggerExtractDocument(documentId),
    onSuccess: (data, documentId) => {
      void queryClient.invalidateQueries({ queryKey: documentKeys.all });
      void queryClient.invalidateQueries({ queryKey: statementKeys.all });
      options?.onSuccess?.(data, documentId);
    },
    onError: options?.onError,
  });
}

export function useTriggerProcessDocument(options?: {
  onSuccess?: (data: unknown, documentId: number) => void;
  onError?: (error: unknown) => void;
}) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (documentId: number) =>
      tasksApi.triggerProcessDocument(documentId),
    onSuccess: (data, documentId) => {
      void queryClient.invalidateQueries({ queryKey: documentKeys.all });
      void queryClient.invalidateQueries({ queryKey: statementKeys.all });
      options?.onSuccess?.(data, documentId);
    },
    onError: options?.onError,
  });
}

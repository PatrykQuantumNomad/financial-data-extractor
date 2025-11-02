/**
 * Integration tests for API + Hooks
 * Tests that hooks properly integrate with API clients using real React Query
 */

import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";
import { renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { apiClient } from "@/lib/api/client";
import {
  useCompanies,
  useCompany,
  useCompanyByTicker,
} from "@/lib/hooks/use-companies";
import {
  useDocumentsByCompany,
  useDocument,
} from "@/lib/hooks/use-documents";
import {
  useStatementByCompanyAndType,
  useStatementsByCompany,
} from "@/lib/hooks/use-statements";
import { useTaskStatus } from "@/lib/hooks/use-tasks";
import { createTestQueryClient } from "./setup";
import type { ReactNode } from "react";
import type {
  Company,
  Document,
  CompiledStatement,
  TaskStatus,
} from "@/lib/types";

// Mock the API client
vi.mock("@/lib/api/client", () => ({
  apiClient: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
  },
}));

const mockApiClient = vi.mocked(apiClient);

// Mock data
const mockCompanies: Company[] = [
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

const mockDocuments: Document[] = [
  {
    id: 1,
    company_id: 1,
    url: "https://example.com/annual-report-2023.pdf",
    fiscal_year: 2023,
    document_type: "annual_report",
    file_path: "/data/pdfs/company1_2023.pdf",
    created_at: "2024-01-01T00:00:00Z",
  },
];

const mockStatements: CompiledStatement[] = [
  {
    id: 1,
    company_id: 1,
    statement_type: "income_statement",
    data: {
      revenue: { 2023: 1000000, 2022: 900000 },
    },
    updated_at: "2024-01-01T00:00:00Z",
  },
];

const mockTaskStatus: TaskStatus = {
  task_id: "test-task-123",
  status: "SUCCESS",
  result: { extracted: true },
  error: null,
};

// Wrapper for React Query provider
function createWrapper(queryClient: QueryClient) {
  return ({ children }: { children: ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
}

describe("API + Hooks Integration", () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    vi.clearAllMocks();
    queryClient = createTestQueryClient();
  });

  afterEach(() => {
    queryClient.clear();
  });

  describe("Companies Hooks", () => {
    it("useCompanies should fetch and return all companies", async () => {
      mockApiClient.get.mockResolvedValue({ data: mockCompanies });

      const wrapper = createWrapper(queryClient);
      const { result } = renderHook(() => useCompanies(), { wrapper });

      // Initially loading
      expect(result.current.isLoading).toBe(true);
      expect(result.current.data).toBeUndefined();

      // Wait for data to load
      await waitFor(() => expect(result.current.isSuccess).toBe(true));

      expect(result.current.data).toHaveLength(2);
      expect(result.current.data?.[0].name).toBe("Test Company 1");
      expect(result.current.data?.[1].name).toBe("Test Company 2");
      expect(result.current.isLoading).toBe(false);
      expect(result.current.error).toBeNull();
      expect(mockApiClient.get).toHaveBeenCalledWith("/companies");
    });

    it("useCompany should fetch company by id", async () => {
      const company = mockCompanies[0];
      mockApiClient.get.mockResolvedValue({ data: company });

      const wrapper = createWrapper(queryClient);
      const { result } = renderHook(() => useCompany(1), { wrapper });

      await waitFor(() => expect(result.current.isSuccess).toBe(true));

      expect(result.current.data).toBeDefined();
      expect(result.current.data?.id).toBe(1);
      expect(result.current.data?.name).toBe("Test Company 1");
      expect(result.current.isLoading).toBe(false);
      expect(mockApiClient.get).toHaveBeenCalledWith("/companies/1");
    });

    it("useCompany should handle 404 errors gracefully", async () => {
      const apiError = new Error("Company not found");
      (apiError as any).status = 404;
      mockApiClient.get.mockRejectedValue(apiError);

      const wrapper = createWrapper(queryClient);
      const { result } = renderHook(() => useCompany(999), { wrapper });

      await waitFor(() => expect(result.current.isError).toBe(true));

      expect(result.current.data).toBeUndefined();
      expect(result.current.error).toBeDefined();
      // Should not retry on 404 (as per hook configuration)
    });

    it("useCompanyByTicker should fetch company by ticker", async () => {
      const company = mockCompanies[0];
      mockApiClient.get.mockResolvedValue({ data: company });

      const wrapper = createWrapper(queryClient);
      const { result } = renderHook(() => useCompanyByTicker("TEST1"), {
        wrapper,
      });

      await waitFor(() => expect(result.current.isSuccess).toBe(true));

      expect(result.current.data).toBeDefined();
      expect(result.current.data?.primary_ticker).toBe("TEST1");
      expect(result.current.data?.name).toBe("Test Company 1");
      expect(mockApiClient.get).toHaveBeenCalledWith("/companies/ticker/TEST1");
    });

    it("useCompanyByTicker should handle missing ticker", async () => {
      const apiError = new Error("Company not found");
      (apiError as any).status = 404;
      mockApiClient.get.mockRejectedValue(apiError);

      const wrapper = createWrapper(queryClient);
      const { result } = renderHook(() => useCompanyByTicker("MISSING"), {
        wrapper,
      });

      await waitFor(() => expect(result.current.isError).toBe(true));

      expect(result.current.data).toBeUndefined();
      expect(result.current.error).toBeDefined();
    });
  });

  describe("Documents Hooks", () => {
    it("useDocumentsByCompany should fetch documents for a company", async () => {
      mockApiClient.get.mockResolvedValue({ data: mockDocuments });

      const wrapper = createWrapper(queryClient);
      const { result } = renderHook(() => useDocumentsByCompany(1), {
        wrapper,
      });

      await waitFor(() => expect(result.current.isSuccess).toBe(true));

      expect(result.current.data).toBeDefined();
      expect(result.current.data).toHaveLength(1);
      expect(result.current.data?.[0].company_id).toBe(1);
      expect(result.current.isLoading).toBe(false);
      expect(mockApiClient.get).toHaveBeenCalledWith(
        "/documents/companies/1",
        expect.objectContaining({ params: { skip: 0, limit: 100 } })
      );
    });

    it("useDocument should fetch a single document by id", async () => {
      mockApiClient.get.mockResolvedValue({ data: mockDocuments[0] });

      const wrapper = createWrapper(queryClient);
      const { result } = renderHook(() => useDocument(1), { wrapper });

      await waitFor(() => expect(result.current.isSuccess).toBe(true));

      expect(result.current.data).toBeDefined();
      expect(result.current.data?.id).toBe(1);
      expect(result.current.data?.fiscal_year).toBe(2023);
      expect(mockApiClient.get).toHaveBeenCalledWith("/documents/1");
    });

    it("useDocumentsByCompany should return empty array for company with no documents", async () => {
      mockApiClient.get.mockResolvedValue({ data: [] });

      const wrapper = createWrapper(queryClient);
      const { result } = renderHook(() => useDocumentsByCompany(999), {
        wrapper,
      });

      await waitFor(() => expect(result.current.isSuccess).toBe(true));

      expect(result.current.data).toEqual([]);
    });
  });

  describe("Statements Hooks", () => {
    it("useStatementsByCompany should fetch all statements for a company", async () => {
      mockApiClient.get.mockResolvedValue({ data: mockStatements });

      const wrapper = createWrapper(queryClient);
      const { result } = renderHook(() => useStatementsByCompany(1), {
        wrapper,
      });

      await waitFor(() => expect(result.current.isSuccess).toBe(true));

      expect(result.current.data).toBeDefined();
      expect(result.current.data).toHaveLength(1);
      expect(result.current.data?.[0].company_id).toBe(1);
      expect(result.current.data?.[0].statement_type).toBe("income_statement");
      expect(mockApiClient.get).toHaveBeenCalledWith(
        "/compiled-statements/companies/1"
      );
    });

    it("useStatementByCompanyAndType should fetch specific statement type", async () => {
      mockApiClient.get.mockResolvedValue({ data: mockStatements[0] });

      const wrapper = createWrapper(queryClient);
      const { result } = renderHook(
        () => useStatementByCompanyAndType(1, "income_statement"),
        { wrapper }
      );

      await waitFor(() => expect(result.current.isSuccess).toBe(true));

      expect(result.current.data).toBeDefined();
      expect(result.current.data?.statement_type).toBe("income_statement");
      expect(result.current.data?.data).toBeDefined();
      expect(result.current.data?.data.revenue).toBeDefined();
      expect(mockApiClient.get).toHaveBeenCalledWith(
        "/compiled-statements/companies/1/statement-type/income_statement"
      );
    });

    it("useStatementByCompanyAndType should handle 404 for missing statement", async () => {
      const apiError = new Error("Statement not found");
      (apiError as any).status = 404;
      mockApiClient.get.mockRejectedValue(apiError);

      const wrapper = createWrapper(queryClient);
      const { result } = renderHook(
        () => useStatementByCompanyAndType(1, "balance_sheet"),
        { wrapper }
      );

      await waitFor(() => expect(result.current.isError).toBe(true));

      expect(result.current.data).toBeUndefined();
      expect(result.current.error).toBeDefined();
      // Should not retry on 404
    });
  });

  describe("Tasks Hooks", () => {
    it("useTaskStatus should poll and fetch task status", async () => {
      mockApiClient.get.mockResolvedValue({ data: mockTaskStatus });

      const wrapper = createWrapper(queryClient);
      const { result } = renderHook(
        () =>
          useTaskStatus("test-task-123", {
            refetchInterval: false, // Disable polling for tests
          }),
        { wrapper }
      );

      await waitFor(() => expect(result.current.isSuccess).toBe(true));

      expect(result.current.data).toBeDefined();
      expect(result.current.data?.task_id).toBe("test-task-123");
      expect(result.current.data?.status).toBe("SUCCESS");
      expect(mockApiClient.get).toHaveBeenCalledWith("/tasks/test-task-123");
    });

    it("useTaskStatus should handle missing task", async () => {
      const apiError = new Error("Task not found");
      (apiError as any).status = 404;
      mockApiClient.get.mockRejectedValue(apiError);

      const wrapper = createWrapper(queryClient);
      const { result } = renderHook(
        () =>
          useTaskStatus("missing-task", {
            refetchInterval: false,
          }),
        { wrapper }
      );

      await waitFor(() => expect(result.current.isError).toBe(true));

      expect(result.current.data).toBeUndefined();
      expect(result.current.error).toBeDefined();
    });
  });

  describe("Query Key Consistency", () => {
    it("should use consistent query keys across multiple calls", async () => {
      mockApiClient.get.mockResolvedValue({ data: mockCompanies });

      const wrapper = createWrapper(queryClient);
      const { result: result1 } = renderHook(() => useCompanies(), {
        wrapper,
      });

      await waitFor(() => expect(result1.current.isSuccess).toBe(true));

      // Clear mock to verify second call uses cache (won't call API again)
      vi.clearAllMocks();

      // Second call should use cached data
      const { result: result2 } = renderHook(() => useCompanies(), {
        wrapper,
      });

      // Should immediately have data from cache
      expect(result2.current.data).toBeDefined();
      expect(result2.current.data).toEqual(result1.current.data);
      // Should not call API again due to cache
      expect(mockApiClient.get).not.toHaveBeenCalled();
    });
  });
});

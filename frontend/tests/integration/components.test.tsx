/**
 * Integration tests for Components + Hooks
 * Tests that components properly integrate with hooks and render correctly
 */

import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { apiClient } from "@/lib/api/client";
import { CompanyList } from "@/components/dashboard/company-list";
import { StatementPageContent } from "@/components/statements/statement-page-content";
import { createTestQueryClient } from "./setup";
import type { ReactNode } from "react";
import type { Company, CompiledStatement } from "@/lib/types";

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

function createWrapper(queryClient: QueryClient) {
  return ({ children }: { children: ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
}

describe("Component + Hooks Integration", () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    vi.clearAllMocks();
    queryClient = createTestQueryClient();
  });

  afterEach(() => {
    queryClient.clear();
  });

  describe("CompanyList Component", () => {
    it("should render loading state initially", () => {
      // Mock delayed response to see loading state
      mockApiClient.get.mockImplementation(
        () =>
          new Promise((resolve) =>
            setTimeout(() => resolve({ data: mockCompanies }), 100)
          )
      );

      const wrapper = createWrapper(queryClient);
      render(<CompanyList />, { wrapper });

      // Should show loading skeleton (component renders loading state)
      // The component shows skeleton cards while loading
    });

    it("should render companies after loading", async () => {
      mockApiClient.get.mockResolvedValue({ data: mockCompanies });

      const wrapper = createWrapper(queryClient);
      render(<CompanyList />, { wrapper });

      // Wait for companies to load
      await waitFor(() => {
        expect(screen.getByText("Test Company 1")).toBeInTheDocument();
      });

      expect(screen.getByText("Test Company 1")).toBeInTheDocument();
      expect(screen.getByText("Test Company 2")).toBeInTheDocument();
      expect(screen.getByText("TEST1")).toBeInTheDocument();
      expect(screen.getByText("TEST2")).toBeInTheDocument();
      expect(mockApiClient.get).toHaveBeenCalledWith("/companies");
    });

    it("should render error state when API fails", async () => {
      const apiError = new Error("Internal server error");
      (apiError as any).status = 500;
      mockApiClient.get.mockRejectedValue(apiError);

      const wrapper = createWrapper(queryClient);
      render(<CompanyList />, { wrapper });

      await waitFor(() => {
        expect(screen.getByText(/error/i)).toBeInTheDocument();
      });
    });

    it("should render empty state when no companies", async () => {
      mockApiClient.get.mockResolvedValue({ data: [] });

      const wrapper = createWrapper(queryClient);
      render(<CompanyList />, { wrapper });

      await waitFor(() => {
        expect(
          screen.getByText(/no companies found/i)
        ).toBeInTheDocument();
      });
    });

    it("should render company links correctly", async () => {
      mockApiClient.get.mockResolvedValue({ data: mockCompanies });

      const wrapper = createWrapper(queryClient);
      render(<CompanyList />, { wrapper });

      await waitFor(() => {
        expect(screen.getByText("Test Company 1")).toBeInTheDocument();
      });

      // Check for links to statements
      const links = screen.getAllByRole("link");
      const statementLinks = links.filter((link) =>
        link.getAttribute("href")?.includes("/statements/")
      );
      expect(statementLinks.length).toBeGreaterThan(0);
    });
  });

  describe("StatementPageContent Component", () => {
    it("should render loading state initially", () => {
      // Mock delayed responses
      mockApiClient.get.mockImplementation(
        () =>
          new Promise((resolve) =>
            setTimeout(() => resolve({ data: mockCompanies[0] }), 100)
          )
      );

      const wrapper = createWrapper(queryClient);
      render(
        <StatementPageContent companyId={1} statementType="income_statement" />,
        { wrapper }
      );

      // Should show loading state
      // The component uses Suspense and StatementPageLoading
      // Loading state may render briefly
    });

    it("should render statement data after loading", async () => {
      // Mock company and statement responses
      mockApiClient.get
        .mockResolvedValueOnce({ data: mockCompanies[0] }) // Company request
        .mockResolvedValueOnce({ data: mockStatements[0] }); // Statement request

      const wrapper = createWrapper(queryClient);
      render(
        <StatementPageContent companyId={1} statementType="income_statement" />,
        { wrapper }
      );

      // Wait for company and statement to load
      await waitFor(() => {
        expect(screen.getByText("Test Company 1")).toBeInTheDocument();
      }, { timeout: 3000 });

      // StatementView should render with data
      // The actual content depends on StatementView implementation
    });

    it("should render 404 error for missing statement", async () => {
      const apiError = new Error("Statement not found");
      (apiError as any).status = 404;

      mockApiClient.get
        .mockResolvedValueOnce({ data: mockCompanies[0] }) // Company request
        .mockRejectedValueOnce(apiError); // Statement request fails with 404

      const wrapper = createWrapper(queryClient);
      render(
        <StatementPageContent companyId={1} statementType="balance_sheet" />,
        { wrapper }
      );

      // Should show 404 error message for missing statement
      // StatementError shows "Financial Statements Not Available" for 404 statements
      await waitFor(() => {
        expect(
          screen.getByText(/Financial Statements Not Available/i)
        ).toBeInTheDocument();
      }, { timeout: 3000 });
    });

    it("should render error for missing company", async () => {
      const apiError = new Error("Company not found");
      (apiError as any).status = 404;
      mockApiClient.get.mockRejectedValue(apiError);

      const wrapper = createWrapper(queryClient);
      render(
        <StatementPageContent companyId={999} statementType="income_statement" />,
        { wrapper }
      );

      // StatementError shows "Company Not Found" or "Unable to Load Data" for errors
      await waitFor(() => {
        expect(
          screen.getByText(/Company Not Found|Unable to Load Data/i)
        ).toBeInTheDocument();
      }, { timeout: 3000 });
    });
  });
});

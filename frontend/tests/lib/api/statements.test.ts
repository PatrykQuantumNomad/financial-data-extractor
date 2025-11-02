import { describe, it, expect, vi, beforeEach } from "vitest";
import { statementsApi } from "@/lib/api/statements";
import { apiClient } from "@/lib/api/client";
import type { CompiledStatement, StatementType } from "@/lib/types";

// Mock the apiClient
vi.mock("@/lib/api/client", () => ({
  apiClient: {
    get: vi.fn(),
  },
}));

const mockApiClient = vi.mocked(apiClient);

describe("Statements API", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("getById", () => {
    it("fetches statement by id", async () => {
      const mockStatement: CompiledStatement = {
        id: 1,
        company_id: 1,
        statement_type: "income_statement",
        data: {},
        updated_at: "2024-01-01T00:00:00Z",
      };

      mockApiClient.get.mockResolvedValue({ data: mockStatement });

      const result = await statementsApi.getById(1);

      expect(result).toEqual(mockStatement);
      expect(mockApiClient.get).toHaveBeenCalledWith("/compiled-statements/1");
    });
  });

  describe("getByCompany", () => {
    it("fetches all statements by company id", async () => {
      const mockStatements: CompiledStatement[] = [
        {
          id: 1,
          company_id: 1,
          statement_type: "income_statement",
          data: {},
          updated_at: "2024-01-01T00:00:00Z",
        },
        {
          id: 2,
          company_id: 1,
          statement_type: "balance_sheet",
          data: {},
          updated_at: "2024-01-01T00:00:00Z",
        },
      ];

      mockApiClient.get.mockResolvedValue({ data: mockStatements });

      const result = await statementsApi.getByCompany(1);

      expect(result).toEqual(mockStatements);
      expect(mockApiClient.get).toHaveBeenCalledWith(
        "/compiled-statements/companies/1"
      );
    });

    it("returns empty array when no statements found", async () => {
      mockApiClient.get.mockResolvedValue({ data: [] });

      const result = await statementsApi.getByCompany(999);

      expect(result).toEqual([]);
    });
  });

  describe("getByCompanyAndType", () => {
    it("fetches statement by company and type", async () => {
      const statementTypes: StatementType[] = [
        "income_statement",
        "balance_sheet",
        "cash_flow_statement",
      ];

      for (const type of statementTypes) {
        vi.clearAllMocks();
        const mockStatement: CompiledStatement = {
          id: 1,
          company_id: 1,
          statement_type: type,
          data: {},
          updated_at: "2024-01-01T00:00:00Z",
        };

        mockApiClient.get.mockResolvedValue({ data: mockStatement });

        const result = await statementsApi.getByCompanyAndType(1, type);

        expect(result).toEqual(mockStatement);
        expect(mockApiClient.get).toHaveBeenCalledWith(
          `/compiled-statements/companies/1/statement-type/${type}`
        );
      }
    });

    it("handles different company IDs", async () => {
      const mockStatement: CompiledStatement = {
        id: 1,
        company_id: 42,
        statement_type: "income_statement",
        data: {},
        updated_at: "2024-01-01T00:00:00Z",
      };

      mockApiClient.get.mockResolvedValue({ data: mockStatement });

      const result = await statementsApi.getByCompanyAndType(
        42,
        "income_statement"
      );

      expect(result).toEqual(mockStatement);
      expect(mockApiClient.get).toHaveBeenCalledWith(
        "/compiled-statements/companies/42/statement-type/income_statement"
      );
    });
  });
});

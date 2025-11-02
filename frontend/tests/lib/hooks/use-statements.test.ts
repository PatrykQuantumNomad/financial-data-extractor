import { describe, it, expect, vi } from "vitest";
import { statementKeys } from "@/lib/hooks/use-statements";

// Mock the API and React Query
vi.mock("@/lib/api/statements", () => ({
  statementsApi: {
    getById: vi.fn(),
    getByCompany: vi.fn(),
    getByCompanyAndType: vi.fn(),
  },
}));

vi.mock("@tanstack/react-query", () => ({
  useQuery: vi.fn((config) => ({
    data: undefined,
    isLoading: true,
    isError: false,
    error: null,
    ...config,
  })),
}));

describe("Statement Hooks", () => {
  describe("statementKeys", () => {
    it("defines correct query keys", () => {
      expect(statementKeys.all).toEqual(["statements"]);
    });

    it("generates lists key", () => {
      expect(statementKeys.lists()).toEqual(["statements", "list"]);
    });

    it("generates byCompany key", () => {
      expect(statementKeys.byCompany(1)).toEqual([
        "statements",
        "list",
        "company",
        1,
      ]);
      expect(statementKeys.byCompany(99)).toEqual([
        "statements",
        "list",
        "company",
        99,
      ]);
    });

    it("generates byCompanyAndType key", () => {
      expect(
        statementKeys.byCompanyAndType(1, "income_statement")
      ).toEqual(["statements", "list", "company", 1, "type", "income_statement"]);
      expect(
        statementKeys.byCompanyAndType(42, "balance_sheet")
      ).toEqual(["statements", "list", "company", 42, "type", "balance_sheet"]);
      expect(
        statementKeys.byCompanyAndType(99, "cash_flow_statement")
      ).toEqual(["statements", "list", "company", 99, "type", "cash_flow_statement"]);
    });

    it("generates detail key with id", () => {
      expect(statementKeys.detail(1)).toEqual(["statements", "detail", 1]);
      expect(statementKeys.detail(100)).toEqual(["statements", "detail", 100]);
    });
  });
});

import { describe, it, expect, vi } from "vitest";
import { companyKeys } from "@/lib/hooks/use-companies";

// Mock the API and React Query
vi.mock("@/lib/api/companies", () => ({
  companiesApi: {
    getAll: vi.fn(),
    getById: vi.fn(),
    getByTicker: vi.fn(),
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

describe("Company Hooks", () => {
  describe("companyKeys", () => {
    it("defines correct query keys", () => {
      expect(companyKeys.all).toEqual(["companies"]);
    });

    it("generates lists key", () => {
      expect(companyKeys.lists()).toEqual(["companies", "list"]);
    });

    it("generates list key with filters", () => {
      const filters = { search: "test" };
      expect(companyKeys.list(filters)).toEqual([
        "companies",
        "list",
        filters,
      ]);
    });

    it("generates details key", () => {
      expect(companyKeys.details()).toEqual(["companies", "detail"]);
    });

    it("generates detail key with id", () => {
      expect(companyKeys.detail(1)).toEqual(["companies", "detail", 1]);
      expect(companyKeys.detail(42)).toEqual(["companies", "detail", 42]);
    });

    it("generates ticker key", () => {
      expect(companyKeys.ticker("TEST")).toEqual(["companies", "ticker", "TEST"]);
      expect(companyKeys.ticker("AAPL")).toEqual(["companies", "ticker", "AAPL"]);
    });
  });
});

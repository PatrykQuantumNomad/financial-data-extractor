import { describe, it, expect, vi } from "vitest";
import { documentKeys } from "@/lib/hooks/use-documents";

// Mock the API and React Query
vi.mock("@/lib/api/documents", () => ({
  documentsApi: {
    getById: vi.fn(),
    getByCompany: vi.fn(),
    getByCompanyAndYear: vi.fn(),
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

describe("Document Hooks", () => {
  describe("documentKeys", () => {
    it("defines correct query keys", () => {
      expect(documentKeys.all).toEqual(["documents"]);
    });

    it("generates lists key", () => {
      expect(documentKeys.lists()).toEqual(["documents", "list"]);
    });

    it("generates byCompany key without filters", () => {
      expect(documentKeys.byCompany(1)).toEqual([
        "documents",
        "list",
        "company",
        1,
        undefined,
      ]);
    });

    it("generates byCompany key with filters", () => {
      const filters = { skip: 10, limit: 20 };
      expect(documentKeys.byCompany(1, filters)).toEqual([
        "documents",
        "list",
        "company",
        1,
        filters,
      ]);
    });

    it("generates byCompanyAndYear key", () => {
      expect(documentKeys.byCompanyAndYear(1, 2024)).toEqual([
        "documents",
        "list",
        "company",
        1,
        "year",
        2024,
      ]);
      expect(documentKeys.byCompanyAndYear(42, 2023)).toEqual([
        "documents",
        "list",
        "company",
        42,
        "year",
        2023,
      ]);
    });

    it("generates byCompanyAndType key without filters", () => {
      expect(documentKeys.byCompanyAndType(1, "annual_report")).toEqual([
        "documents",
        "list",
        "company",
        1,
        "type",
        "annual_report",
        undefined,
      ]);
    });

    it("generates byCompanyAndType key with filters", () => {
      const filters = { skip: 5, limit: 15 };
      expect(documentKeys.byCompanyAndType(1, "quarterly_report", filters)).toEqual([
        "documents",
        "list",
        "company",
        1,
        "type",
        "quarterly_report",
        filters,
      ]);
    });

    it("generates detail key with id", () => {
      expect(documentKeys.detail(1)).toEqual(["documents", "detail", 1]);
      expect(documentKeys.detail(999)).toEqual(["documents", "detail", 999]);
    });
  });
});

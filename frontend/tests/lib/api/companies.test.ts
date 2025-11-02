import { describe, it, expect, vi, beforeEach } from "vitest";
import { companiesApi } from "@/lib/api/companies";
import { apiClient } from "@/lib/api/client";
import type { Company, CompanyCreate } from "@/lib/types";

// Mock the apiClient
vi.mock("@/lib/api/client", () => ({
  apiClient: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
  },
}));

const mockApiClient = vi.mocked(apiClient);

describe("Companies API", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("getAll", () => {
    it("fetches all companies", async () => {
      const mockCompanies: Company[] = [
        {
          id: 1,
          name: "Test Company",
          ir_url: "https://example.com",
          primary_ticker: "TEST",
          tickers: null,
          created_at: "2024-01-01T00:00:00Z",
        },
      ];

      mockApiClient.get.mockResolvedValue({ data: mockCompanies });

      const result = await companiesApi.getAll();

      expect(result).toEqual(mockCompanies);
      expect(mockApiClient.get).toHaveBeenCalledWith("/companies");
    });

    it("returns empty array when no companies found", async () => {
      mockApiClient.get.mockResolvedValue({ data: [] });

      const result = await companiesApi.getAll();

      expect(result).toEqual([]);
    });
  });

  describe("getById", () => {
    it("fetches company by id", async () => {
      const mockCompany: Company = {
        id: 1,
        name: "Test Company",
        ir_url: "https://example.com",
        primary_ticker: "TEST",
        tickers: null,
        created_at: "2024-01-01T00:00:00Z",
      };

      mockApiClient.get.mockResolvedValue({ data: mockCompany });

      const result = await companiesApi.getById(1);

      expect(result).toEqual(mockCompany);
      expect(mockApiClient.get).toHaveBeenCalledWith("/companies/1");
    });

    it("handles different company IDs", async () => {
      const mockCompany: Company = {
        id: 42,
        name: "Another Company",
        ir_url: "https://example2.com",
        primary_ticker: "AC",
        tickers: null,
        created_at: "2024-01-01T00:00:00Z",
      };

      mockApiClient.get.mockResolvedValue({ data: mockCompany });

      const result = await companiesApi.getById(42);

      expect(result).toEqual(mockCompany);
      expect(mockApiClient.get).toHaveBeenCalledWith("/companies/42");
    });
  });

  describe("getByTicker", () => {
    it("fetches company by ticker", async () => {
      const mockCompany: Company = {
        id: 1,
        name: "Test Company",
        ir_url: "https://example.com",
        primary_ticker: "TEST",
        tickers: null,
        created_at: "2024-01-01T00:00:00Z",
      };

      mockApiClient.get.mockResolvedValue({ data: mockCompany });

      const result = await companiesApi.getByTicker("TEST");

      expect(result).toEqual(mockCompany);
      expect(mockApiClient.get).toHaveBeenCalledWith("/companies/ticker/TEST");
    });

    it("handles different tickers", async () => {
      const mockCompany: Company = {
        id: 2,
        name: "Another Company",
        ir_url: "https://example2.com",
        primary_ticker: "TWO",
        tickers: null,
        created_at: "2024-01-01T00:00:00Z",
      };

      mockApiClient.get.mockResolvedValue({ data: mockCompany });

      const result = await companiesApi.getByTicker("TWO");

      expect(result).toEqual(mockCompany);
      expect(mockApiClient.get).toHaveBeenCalledWith("/companies/ticker/TWO");
    });
  });

  describe("create", () => {
    it("creates a new company", async () => {
      const newCompany: CompanyCreate = {
        name: "New Company",
        ir_url: "https://newcompany.com",
        primary_ticker: "NEW",
      };

      const createdCompany: Company = {
        id: 1,
        ...newCompany,
        tickers: null,
        created_at: "2024-01-01T00:00:00Z",
      };

      mockApiClient.post.mockResolvedValue({ data: createdCompany });

      const result = await companiesApi.create(newCompany);

      expect(result).toEqual(createdCompany);
      expect(mockApiClient.post).toHaveBeenCalledWith("/companies", newCompany);
    });

    it("creates company without ticker", async () => {
      const newCompany: CompanyCreate = {
        name: "Company Without Ticker",
        ir_url: "https://example.com",
      };

      const createdCompany: Company = {
        id: 1,
        ...newCompany,
        primary_ticker: null,
        tickers: null,
        created_at: "2024-01-01T00:00:00Z",
      };

      mockApiClient.post.mockResolvedValue({ data: createdCompany });

      const result = await companiesApi.create(newCompany);

      expect(result).toEqual(createdCompany);
    });
  });

  describe("update", () => {
    it("updates company by id", async () => {
      const updates: Partial<CompanyCreate> = {
        name: "Updated Company Name",
      };

      const updatedCompany: Company = {
        id: 1,
        name: "Updated Company Name",
        ir_url: "https://example.com",
        primary_ticker: "TEST",
        tickers: null,
        created_at: "2024-01-01T00:00:00Z",
      };

      mockApiClient.put.mockResolvedValue({ data: updatedCompany });

      const result = await companiesApi.update(1, updates);

      expect(result).toEqual(updatedCompany);
      expect(mockApiClient.put).toHaveBeenCalledWith("/companies/1", updates);
    });

    it("updates with partial data", async () => {
      const updates: Partial<CompanyCreate> = {
        primary_ticker: "UPD",
      };

      const updatedCompany: Company = {
        id: 1,
        name: "Test Company",
        ir_url: "https://example.com",
        primary_ticker: "UPD",
        tickers: null,
        created_at: "2024-01-01T00:00:00Z",
      };

      mockApiClient.put.mockResolvedValue({ data: updatedCompany });

      const result = await companiesApi.update(1, updates);

      expect(result).toEqual(updatedCompany);
    });
  });

  describe("delete", () => {
    it("deletes company by id", async () => {
      mockApiClient.delete.mockResolvedValue(undefined);

      await companiesApi.delete(1);

      expect(mockApiClient.delete).toHaveBeenCalledWith("/companies/1");
    });

    it("handles delete for different ids", async () => {
      mockApiClient.delete.mockResolvedValue(undefined);

      await companiesApi.delete(999);

      expect(mockApiClient.delete).toHaveBeenCalledWith("/companies/999");
    });
  });
});

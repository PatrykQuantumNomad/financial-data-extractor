import { describe, it, expect, vi, beforeEach } from "vitest";
import { documentsApi } from "@/lib/api/documents";
import { apiClient } from "@/lib/api/client";
import type { Document } from "@/lib/types";

// Mock the apiClient
vi.mock("@/lib/api/client", () => ({
  apiClient: {
    get: vi.fn(),
  },
}));

const mockApiClient = vi.mocked(apiClient);

describe("Documents API", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("getById", () => {
    it("fetches document by id", async () => {
      const mockDocument: Document = {
        id: 1,
        company_id: 1,
        url: "https://example.com/doc.pdf",
        fiscal_year: 2024,
        document_type: "annual_report",
        file_path: "/path/to/doc.pdf",
        created_at: "2024-01-01T00:00:00Z",
      };

      mockApiClient.get.mockResolvedValue({ data: mockDocument });

      const result = await documentsApi.getById(1);

      expect(result).toEqual(mockDocument);
      expect(mockApiClient.get).toHaveBeenCalledWith("/documents/1");
    });
  });

  describe("getByCompany", () => {
    it("fetches documents by company id", async () => {
      const mockDocuments: Document[] = [
        {
          id: 1,
          company_id: 1,
          url: "https://example.com/doc1.pdf",
          fiscal_year: 2024,
          document_type: "annual_report",
          file_path: "/path/to/doc1.pdf",
          created_at: "2024-01-01T00:00:00Z",
        },
      ];

      mockApiClient.get.mockResolvedValue({ data: mockDocuments });

      const result = await documentsApi.getByCompany(1);

      expect(result).toEqual(mockDocuments);
      expect(mockApiClient.get).toHaveBeenCalledWith(
        "/documents/companies/1",
        { params: { skip: 0, limit: 100 } }
      );
    });

    it("uses custom skip and limit parameters", async () => {
      const mockDocuments: Document[] = [];
      mockApiClient.get.mockResolvedValue({ data: mockDocuments });

      await documentsApi.getByCompany(1, 10, 20);

      expect(mockApiClient.get).toHaveBeenCalledWith(
        "/documents/companies/1",
        { params: { skip: 10, limit: 20 } }
      );
    });
  });

  describe("getByCompanyAndYear", () => {
    it("fetches documents by company and fiscal year", async () => {
      const mockDocuments: Document[] = [
        {
          id: 1,
          company_id: 1,
          url: "https://example.com/doc.pdf",
          fiscal_year: 2024,
          document_type: "annual_report",
          file_path: "/path/to/doc.pdf",
          created_at: "2024-01-01T00:00:00Z",
        },
      ];

      mockApiClient.get.mockResolvedValue({ data: mockDocuments });

      const result = await documentsApi.getByCompanyAndYear(1, 2024);

      expect(result).toEqual(mockDocuments);
      expect(mockApiClient.get).toHaveBeenCalledWith(
        "/documents/companies/1/fiscal-year/2024"
      );
    });

    it("handles different fiscal years", async () => {
      const mockDocuments: Document[] = [];
      mockApiClient.get.mockResolvedValue({ data: mockDocuments });

      await documentsApi.getByCompanyAndYear(1, 2023);

      expect(mockApiClient.get).toHaveBeenCalledWith(
        "/documents/companies/1/fiscal-year/2023"
      );
    });
  });

  describe("getByCompanyAndType", () => {
    it("fetches documents by company and type", async () => {
      const mockDocuments: Document[] = [
        {
          id: 1,
          company_id: 1,
          url: "https://example.com/doc.pdf",
          fiscal_year: 2024,
          document_type: "annual_report",
          file_path: "/path/to/doc.pdf",
          created_at: "2024-01-01T00:00:00Z",
        },
      ];

      mockApiClient.get.mockResolvedValue({ data: mockDocuments });

      const result = await documentsApi.getByCompanyAndType(1, "annual_report");

      expect(result).toEqual(mockDocuments);
      expect(mockApiClient.get).toHaveBeenCalledWith(
        "/documents/companies/1/type/annual_report",
        { params: { skip: 0, limit: 100 } }
      );
    });

    it("uses custom skip and limit parameters", async () => {
      const mockDocuments: Document[] = [];
      mockApiClient.get.mockResolvedValue({ data: mockDocuments });

      await documentsApi.getByCompanyAndType(1, "quarterly_report", 5, 15);

      expect(mockApiClient.get).toHaveBeenCalledWith(
        "/documents/companies/1/type/quarterly_report",
        { params: { skip: 5, limit: 15 } }
      );
    });

    it("handles different document types", async () => {
      const mockDocuments: Document[] = [];
      mockApiClient.get.mockResolvedValue({ data: mockDocuments });

      await documentsApi.getByCompanyAndType(1, "presentation");

      expect(mockApiClient.get).toHaveBeenCalledWith(
        "/documents/companies/1/type/presentation",
        { params: { skip: 0, limit: 100 } }
      );
    });
  });
});

import { apiClient } from "./client";
import type { Document } from "../types";

export interface StoragePdfFile {
  object_key: string;
  size: number;
  last_modified: string | null;
  content_type: string;
}

export interface StoragePdfListResponse {
  company_id: number;
  fiscal_year: number | null;
  prefix: string;
  count: number;
  files: StoragePdfFile[];
}

export const documentsApi = {
  getById: async (id: number): Promise<Document> => {
    const response = await apiClient.get<Document>(`/documents/${id}`);
    return response.data;
  },

  getByCompany: async (
    companyId: number,
    skip: number = 0,
    limit: number = 100
  ): Promise<Document[]> => {
    const response = await apiClient.get<Document[]>(
      `/documents/companies/${companyId}`,
      {
        params: { skip, limit },
      }
    );
    return response.data;
  },

  getByCompanyAndYear: async (
    companyId: number,
    fiscalYear: number
  ): Promise<Document[]> => {
    const response = await apiClient.get<Document[]>(
      `/documents/companies/${companyId}/fiscal-year/${fiscalYear}`
    );
    return response.data;
  },

  getByCompanyAndType: async (
    companyId: number,
    documentType: string,
    skip: number = 0,
    limit: number = 100
  ): Promise<Document[]> => {
    const response = await apiClient.get<Document[]>(
      `/documents/companies/${companyId}/type/${documentType}`,
      {
        params: { skip, limit },
      }
    );
    return response.data;
  },

  listStoragePdfs: async (
    companyId: number,
    fiscalYear?: number
  ): Promise<StoragePdfListResponse> => {
    const response = await apiClient.get<StoragePdfListResponse>(
      `/documents/storage/companies/${companyId}`,
      {
        params: fiscalYear ? { fiscal_year: fiscalYear } : {},
      }
    );
    return response.data;
  },
};

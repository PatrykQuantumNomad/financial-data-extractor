import { apiClient } from "./client";
import type { Company, CompanyCreate } from "../types";

export const companiesApi = {
  getAll: async (): Promise<Company[]> => {
    const response = await apiClient.get<Company[]>("/companies");
    return response.data;
  },

  getById: async (id: number): Promise<Company> => {
    const response = await apiClient.get<Company>(`/companies/${id}`);
    return response.data;
  },

  getByTicker: async (ticker: string): Promise<Company> => {
    const response = await apiClient.get<Company>(`/companies/ticker/${ticker}`);
    return response.data;
  },

  create: async (data: CompanyCreate): Promise<Company> => {
    const response = await apiClient.post<Company>("/companies", data);
    return response.data;
  },

  update: async (id: number, data: Partial<CompanyCreate>): Promise<Company> => {
    const response = await apiClient.put<Company>(`/companies/${id}`, data);
    return response.data;
  },

  delete: async (id: number): Promise<void> => {
    await apiClient.delete(`/companies/${id}`);
  },
};

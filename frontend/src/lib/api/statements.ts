import { apiClient } from "./client";
import type { CompiledStatement, StatementType } from "../types";

export const statementsApi = {
  getById: async (id: number): Promise<CompiledStatement> => {
    const response = await apiClient.get<CompiledStatement>(
      `/compiled-statements/${id}`
    );
    return response.data;
  },

  getByCompany: async (companyId: number): Promise<CompiledStatement[]> => {
    const response = await apiClient.get<CompiledStatement[]>(
      `/compiled-statements/companies/${companyId}`
    );
    return response.data;
  },

  getByCompanyAndType: async (
    companyId: number,
    statementType: StatementType
  ): Promise<CompiledStatement> => {
    const response = await apiClient.get<CompiledStatement>(
      `/compiled-statements/companies/${companyId}/statement-type/${statementType}`
    );
    return response.data;
  },
};

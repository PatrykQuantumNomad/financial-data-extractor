import { apiClient } from "./client";
import type { TaskResponse, TaskStatus } from "../types";

export const tasksApi = {
  triggerExtractCompany: async (companyId: number): Promise<TaskResponse> => {
    const response = await apiClient.post<TaskResponse>(
      `/tasks/companies/${companyId}/extract`
    );
    return response.data;
  },

  triggerScrapeCompany: async (companyId: number): Promise<TaskResponse> => {
    const response = await apiClient.post<TaskResponse>(
      `/tasks/companies/${companyId}/scrape`
    );
    return response.data;
  },

  triggerRecompileCompany: async (
    companyId: number
  ): Promise<TaskResponse> => {
    const response = await apiClient.post<TaskResponse>(
      `/tasks/companies/${companyId}/recompile`
    );
    return response.data;
  },

  triggerDownloadDocument: async (
    documentId: number
  ): Promise<TaskResponse> => {
    const response = await apiClient.post<TaskResponse>(
      `/tasks/documents/${documentId}/download`
    );
    return response.data;
  },

  triggerClassifyDocument: async (
    documentId: number
  ): Promise<TaskResponse> => {
    const response = await apiClient.post<TaskResponse>(
      `/tasks/documents/${documentId}/classify`
    );
    return response.data;
  },

  triggerExtractDocument: async (
    documentId: number
  ): Promise<TaskResponse> => {
    const response = await apiClient.post<TaskResponse>(
      `/tasks/documents/${documentId}/extract`
    );
    return response.data;
  },

  triggerProcessDocument: async (
    documentId: number
  ): Promise<TaskResponse> => {
    const response = await apiClient.post<TaskResponse>(
      `/tasks/documents/${documentId}/process`
    );
    return response.data;
  },

  getTaskStatus: async (taskId: string): Promise<TaskStatus> => {
    const response = await apiClient.get<TaskStatus>(`/tasks/${taskId}`);
    return response.data;
  },
};

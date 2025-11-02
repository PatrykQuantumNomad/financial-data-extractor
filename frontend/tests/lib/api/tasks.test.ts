import { describe, it, expect, vi, beforeEach } from "vitest";
import { tasksApi } from "@/lib/api/tasks";
import { apiClient } from "@/lib/api/client";
import type { TaskResponse, TaskStatus } from "@/lib/types";

// Mock the apiClient
vi.mock("@/lib/api/client", () => ({
  apiClient: {
    get: vi.fn(),
    post: vi.fn(),
  },
}));

const mockApiClient = vi.mocked(apiClient);

describe("Tasks API", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("triggerExtractCompany", () => {
    it("triggers extract company task", async () => {
      const mockResponse: TaskResponse = {
        task_id: "task-123",
        status: "PENDING",
        message: "Extraction started",
      };

      mockApiClient.post.mockResolvedValue({ data: mockResponse });

      const result = await tasksApi.triggerExtractCompany(1);

      expect(result).toEqual(mockResponse);
      expect(mockApiClient.post).toHaveBeenCalledWith(
        "/tasks/companies/1/extract"
      );
    });
  });

  describe("triggerScrapeCompany", () => {
    it("triggers scrape company task", async () => {
      const mockResponse: TaskResponse = {
        task_id: "task-456",
        status: "PENDING",
        message: "Scraping started",
      };

      mockApiClient.post.mockResolvedValue({ data: mockResponse });

      const result = await tasksApi.triggerScrapeCompany(1);

      expect(result).toEqual(mockResponse);
      expect(mockApiClient.post).toHaveBeenCalledWith(
        "/tasks/companies/1/scrape"
      );
    });
  });

  describe("triggerRecompileCompany", () => {
    it("triggers recompile company task", async () => {
      const mockResponse: TaskResponse = {
        task_id: "task-789",
        status: "PENDING",
        message: "Recompilation started",
      };

      mockApiClient.post.mockResolvedValue({ data: mockResponse });

      const result = await tasksApi.triggerRecompileCompany(1);

      expect(result).toEqual(mockResponse);
      expect(mockApiClient.post).toHaveBeenCalledWith(
        "/tasks/companies/1/recompile"
      );
    });
  });

  describe("triggerDownloadDocument", () => {
    it("triggers download document task", async () => {
      const mockResponse: TaskResponse = {
        task_id: "task-download-123",
        status: "PENDING",
        message: "Download started",
      };

      mockApiClient.post.mockResolvedValue({ data: mockResponse });

      const result = await tasksApi.triggerDownloadDocument(42);

      expect(result).toEqual(mockResponse);
      expect(mockApiClient.post).toHaveBeenCalledWith("/tasks/documents/42/download");
    });
  });

  describe("triggerClassifyDocument", () => {
    it("triggers classify document task", async () => {
      const mockResponse: TaskResponse = {
        task_id: "task-classify-123",
        status: "PENDING",
        message: "Classification started",
      };

      mockApiClient.post.mockResolvedValue({ data: mockResponse });

      const result = await tasksApi.triggerClassifyDocument(42);

      expect(result).toEqual(mockResponse);
      expect(mockApiClient.post).toHaveBeenCalledWith("/tasks/documents/42/classify");
    });
  });

  describe("triggerExtractDocument", () => {
    it("triggers extract document task", async () => {
      const mockResponse: TaskResponse = {
        task_id: "task-extract-123",
        status: "PENDING",
        message: "Extraction started",
      };

      mockApiClient.post.mockResolvedValue({ data: mockResponse });

      const result = await tasksApi.triggerExtractDocument(42);

      expect(result).toEqual(mockResponse);
      expect(mockApiClient.post).toHaveBeenCalledWith("/tasks/documents/42/extract");
    });
  });

  describe("triggerProcessDocument", () => {
    it("triggers process document task", async () => {
      const mockResponse: TaskResponse = {
        task_id: "task-process-123",
        status: "PENDING",
        message: "Processing started",
      };

      mockApiClient.post.mockResolvedValue({ data: mockResponse });

      const result = await tasksApi.triggerProcessDocument(42);

      expect(result).toEqual(mockResponse);
      expect(mockApiClient.post).toHaveBeenCalledWith("/tasks/documents/42/process");
    });
  });

  describe("getTaskStatus", () => {
    it("fetches task status", async () => {
      const mockStatus: TaskStatus = {
        task_id: "task-123",
        status: "SUCCESS",
        result: { completed: true },
        error: null,
      };

      mockApiClient.get.mockResolvedValue({ data: mockStatus });

      const result = await tasksApi.getTaskStatus("task-123");

      expect(result).toEqual(mockStatus);
      expect(mockApiClient.get).toHaveBeenCalledWith("/tasks/task-123");
    });

    it("handles pending status", async () => {
      const mockStatus: TaskStatus = {
        task_id: "task-456",
        status: "PENDING",
        result: null,
        error: null,
      };

      mockApiClient.get.mockResolvedValue({ data: mockStatus });

      const result = await tasksApi.getTaskStatus("task-456");

      expect(result.status).toBe("PENDING");
    });

    it("handles failure status", async () => {
      const mockStatus: TaskStatus = {
        task_id: "task-789",
        status: "FAILURE",
        result: null,
        error: "Task failed with error",
      };

      mockApiClient.get.mockResolvedValue({ data: mockStatus });

      const result = await tasksApi.getTaskStatus("task-789");

      expect(result.status).toBe("FAILURE");
      expect(result.error).toBe("Task failed with error");
    });
  });
});

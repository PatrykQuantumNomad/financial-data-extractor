import { describe, it, expect, vi } from "vitest";
import { taskKeys } from "@/lib/hooks/use-tasks";

// Mock the API and React Query
vi.mock("@/lib/api/tasks", () => ({
  tasksApi: {
    triggerExtractCompany: vi.fn(),
    triggerScrapeCompany: vi.fn(),
    triggerRecompileCompany: vi.fn(),
    triggerDownloadDocument: vi.fn(),
    triggerClassifyDocument: vi.fn(),
    triggerExtractDocument: vi.fn(),
    triggerProcessDocument: vi.fn(),
    getTaskStatus: vi.fn(),
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
  useMutation: vi.fn((config) => ({
    mutate: vi.fn(),
    mutateAsync: vi.fn(),
    ...config,
  })),
  useQueryClient: vi.fn(() => ({
    invalidateQueries: vi.fn(),
  })),
}));

describe("Task Hooks", () => {
  describe("taskKeys", () => {
    it("defines correct query keys", () => {
      expect(taskKeys.all).toEqual(["tasks"]);
    });

    it("generates status key", () => {
      expect(taskKeys.status("task-123")).toEqual(["tasks", "status", "task-123"]);
      expect(taskKeys.status("task-abc-456")).toEqual(["tasks", "status", "task-abc-456"]);
    });
  });

  describe("task status helper functions", () => {
    // These are internal functions, but we can test their behavior through the hooks
    it("correctly identifies task status keys", () => {
      expect(taskKeys.status("pending-task")).toEqual([
        "tasks",
        "status",
        "pending-task",
      ]);
    });
  });
});

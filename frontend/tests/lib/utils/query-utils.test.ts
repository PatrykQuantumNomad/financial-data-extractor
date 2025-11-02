import { describe, it, expect, vi } from "vitest";
import {
  getErrorMessage,
  isQueryLoading,
  isNotFoundError,
  isNetworkError,
  isAuthError,
  isMutationPending,
  getQueryData,
  areManyQueriesLoading,
  doAnyQueriesHaveError,
  getAllQueryErrors,
  formatBytes,
  formatDate,
  debounce,
  type QueryError,
} from "@/lib/utils/query-utils";

describe("Query Utils", () => {
  describe("getErrorMessage", () => {
    it("returns default message when error is null", () => {
      expect(getErrorMessage(null)).toBe("An error occurred");
    });

    it("returns default message when error is undefined", () => {
      expect(getErrorMessage(undefined)).toBe("An error occurred");
    });

    it("returns custom default message", () => {
      expect(getErrorMessage(null, "Custom message")).toBe("Custom message");
    });

    it("returns error message from ApiError", () => {
      const error: QueryError = { message: "Test error", status: 500 };
      expect(getErrorMessage(error)).toBe("Test error");
    });

    it("returns default when error has no message", () => {
      const error: QueryError = { status: 500 };
      expect(getErrorMessage(error)).toBe("An error occurred");
    });
  });

  describe("isQueryLoading", () => {
    it("returns true when isLoading is true", () => {
      const query = {
        isLoading: true,
        isFetching: false,
      } as any;
      expect(isQueryLoading(query)).toBe(true);
    });

    it("returns true when isFetching is true", () => {
      const query = {
        isLoading: false,
        isFetching: true,
      } as any;
      expect(isQueryLoading(query)).toBe(true);
    });

    it("returns true when both are true", () => {
      const query = {
        isLoading: true,
        isFetching: true,
      } as any;
      expect(isQueryLoading(query)).toBe(true);
    });

    it("returns false when neither is true", () => {
      const query = {
        isLoading: false,
        isFetching: false,
      } as any;
      expect(isQueryLoading(query)).toBe(false);
    });
  });

  describe("isNotFoundError", () => {
    it("returns true for 404 error", () => {
      const error: QueryError = { status: 404 };
      expect(isNotFoundError(error)).toBe(true);
    });

    it("returns false for non-404 error", () => {
      const error: QueryError = { status: 500 };
      expect(isNotFoundError(error)).toBe(false);
    });

    it("returns false for error without status", () => {
      const error: QueryError = {};
      expect(isNotFoundError(error)).toBe(false);
    });
  });

  describe("isNetworkError", () => {
    it("returns true for network error", () => {
      const error: QueryError = { code: "NETWORK_ERROR" };
      expect(isNetworkError(error)).toBe(true);
    });

    it("returns false for non-network error", () => {
      const error: QueryError = { code: "OTHER_ERROR" };
      expect(isNetworkError(error)).toBe(false);
    });

    it("returns false for error without code", () => {
      const error: QueryError = {};
      expect(isNetworkError(error)).toBe(false);
    });
  });

  describe("isAuthError", () => {
    it("returns true for 401 error", () => {
      const error: QueryError = { status: 401 };
      expect(isAuthError(error)).toBe(true);
    });

    it("returns true for 403 error", () => {
      const error: QueryError = { status: 403 };
      expect(isAuthError(error)).toBe(true);
    });

    it("returns false for non-auth error", () => {
      const error: QueryError = { status: 500 };
      expect(isAuthError(error)).toBe(false);
    });

    it("returns false for error without status", () => {
      const error: QueryError = {};
      expect(isAuthError(error)).toBe(false);
    });
  });

  describe("isMutationPending", () => {
    it("returns true when mutation is pending", () => {
      const mutation = { isPending: true } as any;
      expect(isMutationPending(mutation)).toBe(true);
    });

    it("returns false when mutation is not pending", () => {
      const mutation = { isPending: false } as any;
      expect(isMutationPending(mutation)).toBe(false);
    });
  });

  describe("getQueryData", () => {
    it("returns query data", () => {
      const data = { id: 1, name: "Test" };
      const query = { data } as any;
      expect(getQueryData(query)).toBe(data);
    });

    it("returns undefined when no data", () => {
      const query = { data: undefined } as any;
      expect(getQueryData(query)).toBeUndefined();
    });
  });

  describe("areManyQueriesLoading", () => {
    it("returns true when any query is loading", () => {
      const queries = [
        { isLoading: false, isFetching: false },
        { isLoading: true, isFetching: false },
        { isLoading: false, isFetching: false },
      ] as any[];
      expect(areManyQueriesLoading(...queries)).toBe(true);
    });

    it("returns true when any query is fetching", () => {
      const queries = [
        { isLoading: false, isFetching: false },
        { isLoading: false, isFetching: true },
        { isLoading: false, isFetching: false },
      ] as any[];
      expect(areManyQueriesLoading(...queries)).toBe(true);
    });

    it("returns false when no queries are loading", () => {
      const queries = [
        { isLoading: false, isFetching: false },
        { isLoading: false, isFetching: false },
      ] as any[];
      expect(areManyQueriesLoading(...queries)).toBe(false);
    });

    it("returns false for empty array", () => {
      expect(areManyQueriesLoading()).toBe(false);
    });
  });

  describe("doAnyQueriesHaveError", () => {
    it("returns true when any query has error", () => {
      const queries = [
        { isError: false },
        { isError: true },
        { isError: false },
      ] as any[];
      expect(doAnyQueriesHaveError(...queries)).toBe(true);
    });

    it("returns false when no queries have error", () => {
      const queries = [
        { isError: false },
        { isError: false },
      ] as any[];
      expect(doAnyQueriesHaveError(...queries)).toBe(false);
    });

    it("returns false for empty array", () => {
      expect(doAnyQueriesHaveError()).toBe(false);
    });
  });

  describe("getAllQueryErrors", () => {
    it("returns all errors from queries", () => {
      const error1: QueryError = { status: 404, message: "Not found" };
      const error2: QueryError = { status: 500, message: "Server error" };
      const queries = [
        { isError: false, error: null },
        { isError: true, error: error1 },
        { isError: false, error: null },
        { isError: true, error: error2 },
      ] as any[];

      const errors = getAllQueryErrors(...queries);
      expect(errors).toHaveLength(2);
      expect(errors).toContain(error1);
      expect(errors).toContain(error2);
    });

    it("returns empty array when no errors", () => {
      const queries = [
        { isError: false, error: null },
        { isError: false, error: null },
      ] as any[];
      expect(getAllQueryErrors(...queries)).toEqual([]);
    });

    it("returns empty array for empty input", () => {
      expect(getAllQueryErrors()).toEqual([]);
    });
  });

  describe("formatBytes", () => {
    it("returns '0 Bytes' for zero", () => {
      expect(formatBytes(0)).toBe("0 Bytes");
    });

    it("formats bytes correctly", () => {
      expect(formatBytes(500)).toBe("500 Bytes");
    });

    it("formats KB correctly", () => {
      expect(formatBytes(1024)).toBe("1 KB");
      expect(formatBytes(2048)).toBe("2 KB");
      expect(formatBytes(1536)).toBe("1.5 KB");
    });

    it("formats MB correctly", () => {
      expect(formatBytes(1048576)).toBe("1 MB");
      expect(formatBytes(2097152)).toBe("2 MB");
    });

    it("formats GB correctly", () => {
      expect(formatBytes(1073741824)).toBe("1 GB");
    });

    it("handles custom decimals", () => {
      expect(formatBytes(1536, 0)).toBe("2 KB");
      expect(formatBytes(1536, 4)).toBe("1.5 KB");
    });

    it("handles negative decimals correctly", () => {
      expect(formatBytes(1536, -1)).toBe("2 KB");
    });
  });

  describe("formatDate", () => {
    it("returns 'N/A' for null", () => {
      expect(formatDate(null)).toBe("N/A");
    });

    it("formats valid date string", () => {
      const dateStr = "2024-01-15T10:30:00Z";
      const formatted = formatDate(dateStr);
      expect(formatted).toContain("Jan");
      expect(formatted).toContain("2024");
    });

    it("handles invalid date string", () => {
      const dateStr = "invalid";
      expect(formatDate(dateStr)).toBe("invalid");
    });
  });

  describe("debounce", () => {
    it("delays function execution", async () => {
      const fn = vi.fn();
      const debounced = debounce(fn, 100);

      debounced();
      expect(fn).not.toHaveBeenCalled();

      await new Promise((resolve) => setTimeout(resolve, 150));
      expect(fn).toHaveBeenCalledTimes(1);
    });

    it("cancels previous call on new call", async () => {
      const fn = vi.fn();
      const debounced = debounce(fn, 100);

      debounced();
      debounced();
      debounced();

      await new Promise((resolve) => setTimeout(resolve, 150));
      expect(fn).toHaveBeenCalledTimes(1);
    });

    it("passes arguments correctly", async () => {
      const fn = vi.fn();
      const debounced = debounce(fn, 100);

      debounced("arg1", "arg2");

      await new Promise((resolve) => setTimeout(resolve, 150));
      expect(fn).toHaveBeenCalledWith("arg1", "arg2");
    });
  });
});

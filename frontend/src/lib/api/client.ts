import axios, {
  type AxiosError,
  type AxiosInstance,
  type AxiosResponse,
  type InternalAxiosRequestConfig,
} from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:3030";

// Custom error type for better type safety
export interface ApiError extends Error {
  status?: number;
  response?: unknown;
  code?: string;
}

// Type guard for Axios errors
function isAxiosError(error: unknown): error is AxiosError {
  return (
    typeof error === "object" &&
    error !== null &&
    "isAxiosError" in error &&
    (error as { isAxiosError?: unknown }).isAxiosError === true
  );
}

// Type guard for error response data
function isErrorResponseData(
  data: unknown
): data is { detail?: string; message?: string; error?: string } {
  return typeof data === "object" && data !== null;
}

export const apiClient: AxiosInstance = axios.create({
  baseURL: `${API_URL}/api/v1`,
  timeout: 30000, // 30 second timeout
  headers: {
    "Content-Type": "application/json",
  },
});

// Request interceptor for auth tokens and request tracking
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // Add auth token if available (example for future use)
    // const token = getAuthToken(); // Implement this based on your auth strategy
    // if (token) {
    //   config.headers.Authorization = `Bearer ${token}`;
    // }

    // Add request timestamp for debugging
    (config as unknown as Record<string, unknown>).metadata = {
      startTime: new Date(),
    };

    return config;
  },
  (error: unknown) => {
    // Ensure we always reject with an Error
    const rejectionError =
      error instanceof Error ? error : new Error(String(error));
    return Promise.reject(rejectionError);
  }
);

// Add response interceptor for error handling
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    // Log response time in development
    if (process.env.NODE_ENV === "development") {
      const configWithMetadata = response.config as unknown as Record<
        string,
        unknown
      >;
      const metadata = configWithMetadata.metadata as
        | { startTime: Date }
        | undefined;
      const startTime = metadata?.startTime;
      if (startTime) {
        const duration = new Date().getTime() - startTime.getTime();
        if (duration > 1000) {
          console.log(
            `[API] Slow request (${duration}ms): ${response.config?.url}`
          );
        }
      }
    }
    return response;
  },
  (error: unknown) => {
    if (isAxiosError(error) && error.response) {
      // Server responded with error
      const response = error.response;
      const status = response.status;
      const data = response.data;

      // Build a meaningful error message first
      let errorMessage = "API request failed";

      if (status === 404) {
        errorMessage = "Resource not found";
        // 404s are expected for missing resources, log at debug level
        if (process.env.NODE_ENV === "development") {
          const configUrl = error.config?.url;
          if (configUrl) {
            console.log(`[API] Resource not found: ${configUrl}`);
          }
        }
      } else if (status === 401) {
        errorMessage = "Unauthorized access";
      } else if (status === 403) {
        errorMessage = "Access forbidden";
      } else if (status === 500) {
        errorMessage = "Internal server error";
      } else if (data) {
        // Try to extract error message from response
        if (isErrorResponseData(data)) {
          errorMessage =
            data.detail ??
            data.message ??
            data.error ??
            (typeof data === "string" ? data : errorMessage) ??
            errorMessage;
        } else if (typeof data === "string") {
          errorMessage = data;
        }
      } else if (response.statusText) {
        errorMessage = `${status} ${response.statusText}`;
      }

      // Only log non-404 errors as errors (404s are expected for missing resources)
      if (status !== 404) {
        const configUrl = error.config?.url;
        const logData: Record<string, unknown> = {
          status,
          statusText: response.statusText,
          url: configUrl,
        };

        // Only include data if it's not empty and has meaningful content
        if (data && typeof data === "object" && Object.keys(data).length > 0) {
          logData.data = data;
        } else if (typeof data === "string" && data.trim().length > 0) {
          logData.data = data;
        }

        console.error(`[API Error ${status}]`, logData);
      }

      const apiError: ApiError = new Error(errorMessage);
      apiError.status = status;
      apiError.response = response;
      throw apiError;
    } else if (isAxiosError(error) && error.request) {
      // Request made but no response
      const configUrl = error.config?.url;
      const configMethod = error.config?.method;
      console.error("Network Error: No response received", {
        url: configUrl,
        method: configMethod?.toUpperCase(),
      });

      const networkError: ApiError = new Error(
        "Network error. Please check your connection and ensure the backend server is running."
      );
      networkError.code = "NETWORK_ERROR";
      throw networkError;
    } else if (
      isAxiosError(error) &&
      "code" in error &&
      error.code === "ECONNABORTED"
    ) {
      // Request timeout
      const timeoutError: ApiError = new Error(
        "Request timeout. The server took too long to respond."
      );
      timeoutError.code = "TIMEOUT";
      throw timeoutError;
    } else {
      // Something else happened
      const errorMessage =
        error instanceof Error ? error.message : String(error);
      console.error("Error:", errorMessage);
      const finalError =
        error instanceof Error ? error : new Error(errorMessage);
      throw finalError;
    }
  }
);

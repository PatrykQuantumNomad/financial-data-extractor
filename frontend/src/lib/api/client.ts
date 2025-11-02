import axios, { AxiosInstance, InternalAxiosRequestConfig } from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:3030";

// Custom error type for better type safety
export interface ApiError extends Error {
  status?: number;
  response?: any;
  code?: string;
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
    (config as any).metadata = { startTime: new Date() };

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => {
    // Log response time in development
    if (process.env.NODE_ENV === "development") {
      const startTime = (response.config as any).metadata?.startTime;
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
  (error) => {
    if (error.response) {
      // Server responded with error
      const status = error.response.status;
      const data = error.response.data;

      // Build a meaningful error message first
      let errorMessage = "API request failed";

      if (status === 404) {
        errorMessage = "Resource not found";
        // 404s are expected for missing resources, log at debug level
        if (process.env.NODE_ENV === "development") {
          console.log(`[API] Resource not found: ${error.config?.url}`);
        }
      } else if (status === 401) {
        errorMessage = "Unauthorized access";
      } else if (status === 403) {
        errorMessage = "Access forbidden";
      } else if (status === 500) {
        errorMessage = "Internal server error";
      } else if (data) {
        // Try to extract error message from response
        errorMessage =
          data.detail ||
          data.message ||
          data.error ||
          (typeof data === "string" ? data : errorMessage);
      } else if (error.response.statusText) {
        errorMessage = `${status} ${error.response.statusText}`;
      }

      // Only log non-404 errors as errors (404s are expected for missing resources)
      if (status !== 404) {
        const logData: Record<string, unknown> = {
          status,
          statusText: error.response.statusText,
          url: error.config?.url,
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
      apiError.response = error.response;
      throw apiError;
    } else if (error.request) {
      // Request made but no response
      console.error("Network Error: No response received", {
        url: error.config?.url,
        method: error.config?.method?.toUpperCase(),
      });

      const networkError: ApiError = new Error(
        "Network error. Please check your connection and ensure the backend server is running."
      );
      networkError.code = "NETWORK_ERROR";
      throw networkError;
    } else if (error.code === "ECONNABORTED") {
      // Request timeout
      const timeoutError: ApiError = new Error(
        "Request timeout. The server took too long to respond."
      );
      timeoutError.code = "TIMEOUT";
      throw timeoutError;
    } else {
      // Something else happened
      console.error("Error:", error.message);
      throw error;
    }
  }
);

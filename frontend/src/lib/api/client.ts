import axios, { AxiosInstance } from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:3030";

export const apiClient: AxiosInstance = axios.create({
  baseURL: `${API_URL}/api/v1`,
  headers: {
    "Content-Type": "application/json",
  },
});

// Add response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
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

      const apiError = new Error(errorMessage);
      (apiError as any).status = status;
      (apiError as any).response = error.response;
      throw apiError;
    } else if (error.request) {
      // Request made but no response
      console.error("Network Error: No response received", {
        url: error.config?.url,
      });
      throw new Error(
        "Network error. Please check your connection and ensure the backend server is running."
      );
    } else {
      // Something else happened
      console.error("Error:", error.message);
      throw error;
    }
  }
);

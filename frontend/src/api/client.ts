import axios, { AxiosError } from "axios";

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "/api/v1",
  timeout: 15000,
  headers: {
    Accept: "application/json",
  },
});

apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError<{ detail?: string }>) => {
    let message = "Network error. Please check your connection.";
    if (error.response?.data?.detail) {
      message = error.response.data.detail;
    } else if (error.response?.status) {
      message = `Server returned error (${error.response.status})`;
    } else if (error.code === "ECONNABORTED") {
      message = "Request timed out. Please try again.";
    } else if (error.message) {
      message = error.message;
    }
    return Promise.reject(new Error(message));
  },
);

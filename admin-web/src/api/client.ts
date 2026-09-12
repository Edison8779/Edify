/**
 * Edify Admin — API Client.
 *
 * Axios instance pre-configured with base URL, auth headers,
 * and error interceptors.
 */

import axios from "axios";
import { config } from "../app/config";

export const apiClient = axios.create({
  baseURL: `${config.apiBaseUrl}${config.apiPrefix}`,
  headers: {
    "Content-Type": "application/json",
  },
  withCredentials: true,
});

// Request interceptor — attach auth token
apiClient.interceptors.request.use(
  (requestConfig) => {
    const token = localStorage.getItem("access_token");
    if (token) {
      requestConfig.headers.Authorization = `Bearer ${token}`;
    }
    return requestConfig;
  },
  (error) => Promise.reject(error),
);

// Response interceptor — handle errors consistently
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid — redirect to login
      localStorage.removeItem("access_token");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  },
);

/**
 * Edify Admin — Application configuration.
 */

export const config = {
  /** Base URL of the Edify API */
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL || "http://localhost:8000",

  /** API version prefix */
  apiPrefix: "/api/v1",

  /** Application name */
  appName: "Edify Admin",
} as const;

export type Config = typeof config;

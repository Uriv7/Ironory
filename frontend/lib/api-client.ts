/**
 * Centralized API client abstraction for Ironory Industrial Quality Inspection SaaS.
 * Handles environment-based configuration, structured error formatting,
 * and automatic injection of JWT bearer authentication and tenant headers.
 */

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export interface ApiError {
  code: string;
  message: string;
  details?: Record<string, unknown>;
}

export class ApiException extends Error {
  status: number;
  code: string;
  details?: Record<string, unknown>;

  constructor(status: number, error: ApiError) {
    super(error.message);
    this.name = "ApiException";
    this.status = status;
    this.code = error.code;
    this.details = error.details;
  }
}

/**
 * Token and Tenant Session Management Helpers
 */
export const sessionStore = {
  getAccessToken: (): string | null => {
    if (typeof window === "undefined") return null;
    return localStorage.getItem("ironory_access_token");
  },
  getRefreshToken: (): string | null => {
    if (typeof window === "undefined") return null;
    return localStorage.getItem("ironory_refresh_token");
  },
  getOrganizationId: (): string | null => {
    if (typeof window === "undefined") return null;
    return localStorage.getItem("ironory_org_id");
  },
  setSession: (accessToken: string, refreshToken: string, orgId: string) => {
    if (typeof window === "undefined") return;
    localStorage.setItem("ironory_access_token", accessToken);
    localStorage.setItem("ironory_refresh_token", refreshToken);
    localStorage.setItem("ironory_org_id", orgId);
  },
  clearSession: () => {
    if (typeof window === "undefined") return;
    localStorage.removeItem("ironory_access_token");
    localStorage.removeItem("ironory_refresh_token");
    localStorage.removeItem("ironory_org_id");
  },
};

async function request<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint.startsWith("/") ? endpoint : `/${endpoint}`}`;

  const headers = new Headers(options.headers);

  // Set default JSON Content-Type if not sending FormData
  if (!headers.has("Content-Type") && !(options.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }

  // Automatically inject Bearer authentication if present in storage
  if (!headers.has("Authorization")) {
    const token = sessionStore.getAccessToken();
    if (token) {
      headers.set("Authorization", `Bearer ${token}`);
    }
  }

  // Automatically inject active tenant header if present in storage
  if (!headers.has("X-Organization-ID")) {
    const orgId = sessionStore.getOrganizationId();
    if (orgId) {
      headers.set("X-Organization-ID", orgId);
    }
  }

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let errorData: ApiError = {
      code: "HTTP_ERROR",
      message: `Request failed with status ${response.status}`,
    };

    try {
      const json = await response.json();
      if (json.error) {
        errorData = json.error;
      } else if (json.detail) {
        errorData = {
          code: "API_ERROR",
          message:
            typeof json.detail === "string"
              ? json.detail
              : JSON.stringify(json.detail),
        };
      }
    } catch {
      // response wasn't json, use default errorData
    }

    throw new ApiException(response.status, errorData);
  }

  return response.json() as Promise<T>;
}

export const apiClient = {
  get: <T>(endpoint: string, options?: RequestInit) =>
    request<T>(endpoint, { ...options, method: "GET" }),

  post: <T>(endpoint: string, body?: unknown, options?: RequestInit) =>
    request<T>(endpoint, {
      ...options,
      method: "POST",
      body: body instanceof FormData ? body : JSON.stringify(body),
    }),

  patch: <T>(endpoint: string, body?: unknown, options?: RequestInit) =>
    request<T>(endpoint, {
      ...options,
      method: "PATCH",
      body: JSON.stringify(body),
    }),

  put: <T>(endpoint: string, body?: unknown, options?: RequestInit) =>
    request<T>(endpoint, {
      ...options,
      method: "PUT",
      body: JSON.stringify(body),
    }),

  delete: <T>(endpoint: string, options?: RequestInit) =>
    request<T>(endpoint, { ...options, method: "DELETE" }),
};

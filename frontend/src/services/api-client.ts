import axios, { AxiosError, type InternalAxiosRequestConfig } from "axios";

/**
 * In-memory access-token holder.
 *
 * The access token is deliberately kept out of localStorage/sessionStorage
 * (XSS-exposed) and out of Zustand persistence. It lives only in memory for
 * the life of the tab. The refresh token never touches JS at all — it's an
 * httpOnly cookie set by the backend (see SRS §1.6 / Security Architecture
 * §12) and is sent automatically because `withCredentials: true` below.
 *
 * The auth feature module owns calling `setAccessToken` after login/refresh
 * and `clearAccessToken` on logout; this module only exposes the mechanism.
 */
let accessToken: string | null = null;

export function setAccessToken(token: string | null): void {
  accessToken = token;
}

export function getAccessToken(): string | null {
  return accessToken;
}

export interface ApiErrorPayload {
  type: string;
  title: string;
  status: number;
  detail: string;
  instance?: string;
}

export class ApiError extends Error {
  readonly status: number;
  readonly type: string;
  readonly instance?: string;

  constructor(payload: ApiErrorPayload) {
    super(payload.detail || payload.title);
    this.name = "ApiError";
    this.status = payload.status;
    this.type = payload.type;
    this.instance = payload.instance;
  }
}

function generateRequestId(): string {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return crypto.randomUUID();
  }
  return `${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  withCredentials: true,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 30_000,
});

apiClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  config.headers.set("X-Request-ID", generateRequestId());
  if (accessToken) {
    config.headers.set("Authorization", `Bearer ${accessToken}`);
  }
  return config;
});

/**
 * Refresh coordination: if multiple requests fail with 401 concurrently, we
 * only want a single in-flight refresh call. Subsequent 401s await the same
 * promise instead of each triggering their own refresh.
 */
let refreshPromise: Promise<string | null> | null = null;

async function refreshAccessToken(): Promise<string | null> {
  if (!refreshPromise) {
    refreshPromise = axios
      .post<{ access_token: string }>(
        `${import.meta.env.VITE_API_BASE_URL}/auth/refresh`,
        {},
        { withCredentials: true },
      )
      .then((response) => {
        const token = response.data.access_token;
        setAccessToken(token);
        return token;
      })
      .catch(() => {
        setAccessToken(null);
        return null;
      })
      .finally(() => {
        refreshPromise = null;
      });
  }
  return refreshPromise;
}

apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError<ApiErrorPayload>) => {
    const originalRequest = error.config as
      | (InternalAxiosRequestConfig & { _retried?: boolean })
      | undefined;

    const isAuthEndpoint = originalRequest?.url?.includes("/auth/");

    if (error.response?.status === 401 && originalRequest && !originalRequest._retried && !isAuthEndpoint) {
      originalRequest._retried = true;
      const newToken = await refreshAccessToken();
      if (newToken) {
        originalRequest.headers.set("Authorization", `Bearer ${newToken}`);
        return apiClient(originalRequest);
      }
    }

    if (error.response?.data) {
      return Promise.reject(new ApiError(error.response.data));
    }

    return Promise.reject(
      new ApiError({
        type: "about:blank",
        title: "Network Error",
        status: error.response?.status ?? 0,
        detail: error.message || "Unable to reach the server. Check your connection and try again.",
      }),
    );
  },
);

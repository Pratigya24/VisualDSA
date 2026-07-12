import { apiClient, setAccessToken } from "@/services/api-client";
import type {
  AuthenticatedResult,
  ForgotPasswordPayload,
  LoginPayload,
  RegisterPayload,
  ResetPasswordPayload,
  User,
} from "@/features/auth/types";

/* ---- Backend wire shapes (snake_case, as returned by FastAPI) ---- */

interface UserResponseDTO {
  id: string;
  email: string;
  display_name: string;
  avatar_url: string | null;
  role: "student" | "admin";
  email_verified: boolean;
  streak_count: number;
  created_at: string;
}

interface AuthenticatedResponseDTO {
  user: UserResponseDTO;
  access_token: string;
  token_type: string;
  expires_in: number;
}

interface AccessTokenResponseDTO {
  access_token: string;
  token_type: string;
  expires_in: number;
}

function toUser(dto: UserResponseDTO): User {
  return {
    id: dto.id,
    email: dto.email,
    displayName: dto.display_name,
    avatarUrl: dto.avatar_url,
    role: dto.role,
    emailVerified: dto.email_verified,
    streakCount: dto.streak_count,
    createdAt: dto.created_at,
  };
}

function toAuthenticatedResult(dto: AuthenticatedResponseDTO): AuthenticatedResult {
  return {
    user: toUser(dto.user),
    accessToken: dto.access_token,
    expiresIn: dto.expires_in,
  };
}

export async function registerUser(payload: RegisterPayload): Promise<AuthenticatedResult> {
  const response = await apiClient.post<AuthenticatedResponseDTO>("/auth/register", {
    email: payload.email,
    password: payload.password,
    display_name: payload.displayName,
  });
  const result = toAuthenticatedResult(response.data);
  setAccessToken(result.accessToken);
  return result;
}

export async function loginUser(payload: LoginPayload): Promise<AuthenticatedResult> {
  const response = await apiClient.post<AuthenticatedResponseDTO>("/auth/login", payload);
  const result = toAuthenticatedResult(response.data);
  setAccessToken(result.accessToken);
  return result;
}

export async function logoutUser(): Promise<void> {
  await apiClient.post("/auth/logout");
  setAccessToken(null);
}

export async function fetchCurrentUser(): Promise<User> {
  const response = await apiClient.get<UserResponseDTO>("/auth/me");
  return toUser(response.data);
}

export async function refreshSession(): Promise<string> {
  const response = await apiClient.post<AccessTokenResponseDTO>("/auth/refresh");
  setAccessToken(response.data.access_token);
  return response.data.access_token;
}

export async function requestPasswordReset(payload: ForgotPasswordPayload): Promise<void> {
  await apiClient.post("/auth/forgot-password", payload);
}

export async function resetPassword(payload: ResetPasswordPayload): Promise<void> {
  await apiClient.post("/auth/reset-password", {
    token: payload.token,
    new_password: payload.newPassword,
  });
}

export async function verifyEmail(token: string): Promise<User> {
  const response = await apiClient.post<UserResponseDTO>("/auth/verify-email", { token });
  return toUser(response.data);
}

export function googleLoginUrl(): string {
  return `${import.meta.env.VITE_API_BASE_URL}/auth/google`;
}

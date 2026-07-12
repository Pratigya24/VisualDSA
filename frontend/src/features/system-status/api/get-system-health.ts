import { apiClient } from "@/services/api-client";

export interface DependencyStatus {
  mongodb: boolean;
  redis: boolean;
}

export interface SystemHealth {
  status: "ok" | "degraded";
  dependencies: DependencyStatus;
}

export async function getSystemHealth(): Promise<SystemHealth> {
  const response = await apiClient.get<SystemHealth>("/health");
  return response.data;
}

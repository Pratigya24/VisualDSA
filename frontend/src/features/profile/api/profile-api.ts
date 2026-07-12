import { apiClient } from "@/services/api-client";

export async function updateProfile(payload: { displayName?: string; avatarUrl?: string }): Promise<void> {
  await apiClient.patch("/users/me", {
    display_name: payload.displayName,
    avatar_url: payload.avatarUrl,
  });
}

export async function changePassword(payload: {
  currentPassword: string;
  newPassword: string;
}): Promise<void> {
  await apiClient.post("/users/me/change-password", {
    current_password: payload.currentPassword,
    new_password: payload.newPassword,
  });
}

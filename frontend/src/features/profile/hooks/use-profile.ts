import { useMutation, useQueryClient } from "@tanstack/react-query";

import { currentUserQueryKey } from "@/features/auth/hooks/use-current-user";
import { changePassword, updateProfile } from "@/features/profile/api/profile-api";

export function useUpdateProfile() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: updateProfile,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: currentUserQueryKey }),
  });
}

export function useChangePassword() {
  return useMutation({
    mutationFn: changePassword,
  });
}

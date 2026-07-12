import { useMutation, useQueryClient } from "@tanstack/react-query";

import { logoutUser } from "@/features/auth/api/auth-api";
import { useAuthSessionStore } from "@/features/auth/store/auth-session-store";

export function useLogout() {
  const queryClient = useQueryClient();
  const setStatus = useAuthSessionStore((state) => state.setStatus);

  return useMutation({
    mutationFn: logoutUser,
    onSuccess: () => {
      setStatus("unauthenticated");
      queryClient.clear();
    },
  });
}

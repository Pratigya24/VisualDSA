import { useMutation, useQueryClient } from "@tanstack/react-query";

import { loginUser } from "@/features/auth/api/auth-api";
import { currentUserQueryKey } from "@/features/auth/hooks/use-current-user";
import { useAuthSessionStore } from "@/features/auth/store/auth-session-store";
import type { LoginPayload } from "@/features/auth/types";

export function useLogin() {
  const queryClient = useQueryClient();
  const setStatus = useAuthSessionStore((state) => state.setStatus);

  return useMutation({
    mutationFn: (payload: LoginPayload) => loginUser(payload),
    onSuccess: (result) => {
      setStatus("authenticated");
      queryClient.setQueryData(currentUserQueryKey, result.user);
    },
  });
}

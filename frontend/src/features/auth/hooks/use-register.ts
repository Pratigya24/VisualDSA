import { useMutation, useQueryClient } from "@tanstack/react-query";

import { registerUser } from "@/features/auth/api/auth-api";
import { currentUserQueryKey } from "@/features/auth/hooks/use-current-user";
import { useAuthSessionStore } from "@/features/auth/store/auth-session-store";
import type { RegisterPayload } from "@/features/auth/types";

export function useRegister() {
  const queryClient = useQueryClient();
  const setStatus = useAuthSessionStore((state) => state.setStatus);

  return useMutation({
    mutationFn: (payload: RegisterPayload) => registerUser(payload),
    onSuccess: (result) => {
      setStatus("authenticated");
      queryClient.setQueryData(currentUserQueryKey, result.user);
    },
  });
}

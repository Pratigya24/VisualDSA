import { useQuery } from "@tanstack/react-query";

import { fetchCurrentUser } from "@/features/auth/api/auth-api";
import { useAuthSessionStore } from "@/features/auth/store/auth-session-store";

export const currentUserQueryKey = ["auth", "me"] as const;

export function useCurrentUser() {
  const status = useAuthSessionStore((state) => state.status);

  return useQuery({
    queryKey: currentUserQueryKey,
    queryFn: fetchCurrentUser,
    enabled: status === "authenticated",
    staleTime: 60_000,
    retry: false,
  });
}

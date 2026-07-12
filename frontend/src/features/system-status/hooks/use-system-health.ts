import { useQuery } from "@tanstack/react-query";

import { getSystemHealth } from "@/features/system-status/api/get-system-health";

export const systemHealthQueryKey = ["system-health"] as const;

export function useSystemHealth() {
  return useQuery({
    queryKey: systemHealthQueryKey,
    queryFn: getSystemHealth,
    refetchInterval: 15_000,
    retry: 1,
  });
}

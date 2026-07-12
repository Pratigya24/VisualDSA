import { useQuery } from "@tanstack/react-query";

import { getAlgorithm, listAlgorithms } from "@/features/algorithms/api/algorithms-api";
import type { AlgorithmListFilters } from "@/features/algorithms/types";

export function useAlgorithms(filters: AlgorithmListFilters, options?: { enabled?: boolean }) {
  return useQuery({
    queryKey: ["algorithms", filters],
    queryFn: () => listAlgorithms(filters),
    placeholderData: (previous) => previous,
    enabled: options?.enabled ?? true,
  });
}

export function useAlgorithm(slug: string | undefined) {
  return useQuery({
    queryKey: ["algorithms", "detail", slug],
    queryFn: () => getAlgorithm(slug as string),
    enabled: Boolean(slug),
  });
}

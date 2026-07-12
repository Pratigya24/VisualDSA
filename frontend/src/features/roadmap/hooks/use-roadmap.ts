import { useQuery } from "@tanstack/react-query";

import { listRoadmapTopics } from "@/features/roadmap/api/roadmap-api";

export function useRoadmap() {
  return useQuery({
    queryKey: ["roadmap"],
    queryFn: listRoadmapTopics,
    staleTime: 60_000,
  });
}

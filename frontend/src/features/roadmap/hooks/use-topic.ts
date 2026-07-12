import { useQuery } from "@tanstack/react-query";

import { getTopic } from "@/features/roadmap/api/topic-detail-api";

export function useTopic(slug: string | undefined) {
  return useQuery({
    queryKey: ["roadmap", "topic", slug],
    queryFn: () => getTopic(slug as string),
    enabled: Boolean(slug),
  });
}

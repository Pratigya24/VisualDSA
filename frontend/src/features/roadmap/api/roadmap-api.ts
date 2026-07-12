import { apiClient } from "@/services/api-client";
import type { RoadmapTopic } from "@/features/roadmap/types";

interface TopicDTO {
  id: string;
  name: string;
  slug: string;
  description: string;
  order: number;
  prerequisite_ids: string[];
  icon: string | null;
  is_unlocked: boolean;
  algorithm_count: number;
  solved_count: number;
}

interface TopicListDTO {
  topics: TopicDTO[];
}

export async function listRoadmapTopics(): Promise<RoadmapTopic[]> {
  const response = await apiClient.get<TopicListDTO>("/topics");
  return response.data.topics
    .map((dto) => ({
      id: dto.id,
      name: dto.name,
      slug: dto.slug,
      description: dto.description,
      order: dto.order,
      prerequisiteIds: dto.prerequisite_ids,
      icon: dto.icon,
      isUnlocked: dto.is_unlocked,
      algorithmCount: dto.algorithm_count,
      solvedCount: dto.solved_count,
    }))
    .sort((a, b) => a.order - b.order);
}

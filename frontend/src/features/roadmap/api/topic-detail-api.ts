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

export async function getTopic(slug: string): Promise<RoadmapTopic> {
  const response = await apiClient.get<TopicDTO>(`/topics/${slug}`);
  const dto = response.data;
  return {
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
  };
}

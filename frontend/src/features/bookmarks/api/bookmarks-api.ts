import { apiClient } from "@/services/api-client";
import type { Difficulty, ProgressStatus } from "@/features/algorithms/types";
import type { Bookmark } from "@/features/bookmarks/types";

interface AlgorithmSummaryDTO {
  id: string;
  slug: string;
  title: string;
  difficulty: Difficulty;
  topic_id: string;
  pattern_tags: string[];
  companies: string[];
  estimated_minutes: number;
  status: ProgressStatus;
  is_bookmarked: boolean;
}

interface BookmarkDTO {
  algorithm: AlgorithmSummaryDTO;
  created_at: string;
}

export async function listBookmarks(): Promise<Bookmark[]> {
  const response = await apiClient.get<BookmarkDTO[]>("/bookmarks");
  return response.data.map((dto) => ({
    algorithm: {
      id: dto.algorithm.id,
      slug: dto.algorithm.slug,
      title: dto.algorithm.title,
      difficulty: dto.algorithm.difficulty,
      topicId: dto.algorithm.topic_id,
      patternTags: dto.algorithm.pattern_tags,
      companies: dto.algorithm.companies,
      estimatedMinutes: dto.algorithm.estimated_minutes,
      status: dto.algorithm.status,
      isBookmarked: true,
    },
    createdAt: dto.created_at,
  }));
}

export async function addBookmark(algorithmId: string): Promise<void> {
  await apiClient.post("/bookmarks", { algorithm_id: algorithmId });
}

export async function removeBookmark(algorithmId: string): Promise<void> {
  await apiClient.delete(`/bookmarks/${algorithmId}`);
}

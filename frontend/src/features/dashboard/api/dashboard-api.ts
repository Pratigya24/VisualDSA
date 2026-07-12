import { apiClient } from "@/services/api-client";
import type { Difficulty, ProgressStatus } from "@/features/algorithms/types";
import type { DashboardData } from "@/features/dashboard/types";

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

interface DashboardDTO {
  streak_count: number;
  total_solved: number;
  total_attempted: number;
  difficulty_breakdown: { easy: number; medium: number; hard: number };
  weekly_activity: { date: string; count: number }[];
  recommended_algorithm: AlgorithmSummaryDTO | null;
}

export async function getDashboard(): Promise<DashboardData> {
  const response = await apiClient.get<DashboardDTO>("/dashboard");
  const dto = response.data;
  return {
    streakCount: dto.streak_count,
    totalSolved: dto.total_solved,
    totalAttempted: dto.total_attempted,
    difficultyBreakdown: dto.difficulty_breakdown,
    weeklyActivity: dto.weekly_activity,
    recommendedAlgorithm: dto.recommended_algorithm
      ? {
          id: dto.recommended_algorithm.id,
          slug: dto.recommended_algorithm.slug,
          title: dto.recommended_algorithm.title,
          difficulty: dto.recommended_algorithm.difficulty,
          topicId: dto.recommended_algorithm.topic_id,
          patternTags: dto.recommended_algorithm.pattern_tags,
          companies: dto.recommended_algorithm.companies,
          estimatedMinutes: dto.recommended_algorithm.estimated_minutes,
          status: dto.recommended_algorithm.status,
          isBookmarked: dto.recommended_algorithm.is_bookmarked,
        }
      : null,
  };
}

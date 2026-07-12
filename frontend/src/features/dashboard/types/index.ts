import type { AlgorithmSummary } from "@/features/algorithms/types";

export interface DailyActivity {
  date: string;
  count: number;
}

export interface DifficultyBreakdown {
  easy: number;
  medium: number;
  hard: number;
}

export interface DashboardData {
  streakCount: number;
  totalSolved: number;
  totalAttempted: number;
  difficultyBreakdown: DifficultyBreakdown;
  weeklyActivity: DailyActivity[];
  recommendedAlgorithm: AlgorithmSummary | null;
}

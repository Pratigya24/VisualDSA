export type Difficulty = "easy" | "medium" | "hard";
export type ProgressStatus = "not_started" | "in_progress" | "solved" | "needs_review";

export interface AlgorithmSummary {
  id: string;
  slug: string;
  title: string;
  difficulty: Difficulty;
  topicId: string;
  patternTags: string[];
  companies: string[];
  estimatedMinutes: number;
  status: ProgressStatus;
  isBookmarked: boolean;
}

export interface AlgorithmDetail extends AlgorithmSummary {
  statementMd: string;
  timeComplexity: string;
  spaceComplexity: string;
  pluginKey: string;
}

export interface AlgorithmListResult {
  items: AlgorithmSummary[];
  page: number;
  limit: number;
  total: number;
  totalPages: number;
}

export interface AlgorithmListFilters {
  page?: number;
  limit?: number;
  topicId?: string;
  difficulty?: Difficulty;
  company?: string;
  pattern?: string;
  search?: string;
}

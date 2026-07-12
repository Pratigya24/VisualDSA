import { apiClient } from "@/services/api-client";
import type {
  AlgorithmDetail,
  AlgorithmListFilters,
  AlgorithmListResult,
  AlgorithmSummary,
  Difficulty,
  ProgressStatus,
} from "@/features/algorithms/types";

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

interface AlgorithmDetailDTO extends AlgorithmSummaryDTO {
  statement_md: string;
  time_complexity: string;
  space_complexity: string;
  plugin_key: string;
}

interface AlgorithmListDTO {
  items: AlgorithmSummaryDTO[];
  page: number;
  limit: number;
  total: number;
  total_pages: number;
}

function toSummary(dto: AlgorithmSummaryDTO): AlgorithmSummary {
  return {
    id: dto.id,
    slug: dto.slug,
    title: dto.title,
    difficulty: dto.difficulty,
    topicId: dto.topic_id,
    patternTags: dto.pattern_tags,
    companies: dto.companies,
    estimatedMinutes: dto.estimated_minutes,
    status: dto.status,
    isBookmarked: dto.is_bookmarked,
  };
}

export async function listAlgorithms(filters: AlgorithmListFilters): Promise<AlgorithmListResult> {
  const response = await apiClient.get<AlgorithmListDTO>("/algorithms", {
    params: {
      page: filters.page,
      limit: filters.limit,
      topic_id: filters.topicId,
      difficulty: filters.difficulty,
      company: filters.company,
      pattern: filters.pattern,
      search: filters.search,
    },
  });
  return {
    items: response.data.items.map(toSummary),
    page: response.data.page,
    limit: response.data.limit,
    total: response.data.total,
    totalPages: response.data.total_pages,
  };
}

export async function getAlgorithm(slug: string): Promise<AlgorithmDetail> {
  const response = await apiClient.get<AlgorithmDetailDTO>(`/algorithms/${slug}`);
  const dto = response.data;
  return {
    ...toSummary(dto),
    statementMd: dto.statement_md,
    timeComplexity: dto.time_complexity,
    spaceComplexity: dto.space_complexity,
    pluginKey: dto.plugin_key,
  };
}

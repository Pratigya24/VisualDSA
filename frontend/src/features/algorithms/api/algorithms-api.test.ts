import { describe, expect, it, vi, beforeEach } from "vitest";

import { apiClient } from "@/services/api-client";
import { getAlgorithm, listAlgorithms } from "@/features/algorithms/api/algorithms-api";

describe("algorithms-api mapping", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("maps a paginated list DTO from snake_case to camelCase", async () => {
    vi.spyOn(apiClient, "get").mockResolvedValueOnce({
      data: {
        items: [
          {
            id: "1",
            slug: "two-sum",
            title: "Two Sum",
            difficulty: "easy",
            topic_id: "t1",
            pattern_tags: ["hash-map"],
            companies: ["Amazon"],
            estimated_minutes: 15,
            status: "not_started",
            is_bookmarked: false,
          },
        ],
        page: 1,
        limit: 20,
        total: 1,
        total_pages: 1,
      },
    } as never);

    const result = await listAlgorithms({});

    expect(result.totalPages).toBe(1);
    expect(result.items[0]).toEqual({
      id: "1",
      slug: "two-sum",
      title: "Two Sum",
      difficulty: "easy",
      topicId: "t1",
      patternTags: ["hash-map"],
      companies: ["Amazon"],
      estimatedMinutes: 15,
      status: "not_started",
      isBookmarked: false,
    });
  });

  it("maps a detail DTO including the extra detail-only fields", async () => {
    vi.spyOn(apiClient, "get").mockResolvedValueOnce({
      data: {
        id: "1",
        slug: "two-sum",
        title: "Two Sum",
        difficulty: "easy",
        topic_id: "t1",
        pattern_tags: [],
        companies: [],
        estimated_minutes: 15,
        status: "solved",
        is_bookmarked: true,
        statement_md: "Given an array...",
        time_complexity: "O(n)",
        space_complexity: "O(n)",
        plugin_key: "two-sum",
      },
    } as never);

    const result = await getAlgorithm("two-sum");

    expect(result.timeComplexity).toBe("O(n)");
    expect(result.pluginKey).toBe("two-sum");
    expect(result.status).toBe("solved");
    expect(result.isBookmarked).toBe(true);
  });
});

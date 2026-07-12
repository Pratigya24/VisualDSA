import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { addBookmark, listBookmarks, removeBookmark } from "@/features/bookmarks/api/bookmarks-api";

export const bookmarksQueryKey = ["bookmarks"] as const;

export function useBookmarks() {
  return useQuery({
    queryKey: bookmarksQueryKey,
    queryFn: listBookmarks,
  });
}

/**
 * Toggles a single algorithm's bookmark state. Optimistically flips
 * `isBookmarked` on every cached algorithm list/detail entry so the UI
 * responds instantly, and rolls back on failure — per the State Management
 * Strategy (architecture §13), optimistic updates are reserved for exactly
 * this kind of low-risk, easily-reversible action.
 */
export function useToggleBookmark() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ algorithmId, isBookmarked }: { algorithmId: string; isBookmarked: boolean }) =>
      isBookmarked ? removeBookmark(algorithmId) : addBookmark(algorithmId),
    onMutate: async ({ algorithmId, isBookmarked }) => {
      await queryClient.cancelQueries({ queryKey: ["algorithms"] });
      const previous = queryClient.getQueriesData({ queryKey: ["algorithms"] });

      queryClient.setQueriesData({ queryKey: ["algorithms"] }, (data: unknown) => {
        if (!data || typeof data !== "object") return data;
        if ("items" in data) {
          const list = data as { items: { id: string; isBookmarked: boolean }[] };
          return {
            ...list,
            items: list.items.map((item) =>
              item.id === algorithmId ? { ...item, isBookmarked: !isBookmarked } : item,
            ),
          };
        }
        if ("id" in data) {
          const detail = data as { id: string; isBookmarked: boolean };
          return detail.id === algorithmId ? { ...detail, isBookmarked: !isBookmarked } : detail;
        }
        return data;
      });

      return { previous };
    },
    onError: (_err, _vars, context) => {
      context?.previous.forEach(([key, data]) => {
        queryClient.setQueryData(key, data);
      });
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["algorithms"] });
      queryClient.invalidateQueries({ queryKey: bookmarksQueryKey });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });
}

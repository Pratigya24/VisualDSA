import { useMemo, useState } from "react";

import { ProblemListItem } from "@/features/algorithms/components/problem-list-item";
import { useBookmarks } from "@/features/bookmarks/hooks/use-bookmarks";
import { Input } from "@/shared/components/input";

export function BookmarksPage() {
  const { data: bookmarks, isLoading, isError, refetch } = useBookmarks();
  const [search, setSearch] = useState("");

  const filtered = useMemo(() => {
    if (!bookmarks) return [];
    const query = search.trim().toLowerCase();
    if (!query) return bookmarks;
    return bookmarks.filter((bookmark) => bookmark.algorithm.title.toLowerCase().includes(query));
  }, [bookmarks, search]);

  return (
    <main className="mx-auto max-w-3xl px-6 py-8">
      <h1 className="mb-1 font-display text-2xl font-semibold">Bookmarks</h1>
      <p className="mb-6 text-sm text-ink-muted">Problems you've saved to come back to.</p>

      {bookmarks && bookmarks.length > 0 && (
        <Input
          placeholder="Search bookmarks…"
          value={search}
          onChange={(event) => setSearch(event.target.value)}
          className="mb-4"
          aria-label="Search bookmarks"
        />
      )}

      {isLoading && (
        <div className="space-y-2" aria-hidden>
          {[0, 1, 2].map((i) => (
            <div key={i} className="h-16 animate-pulse-trace rounded-lg bg-canvas-overlay" />
          ))}
        </div>
      )}

      {isError && (
        <div className="glass-surface rounded-lg p-6 text-center">
          <p className="mb-3 text-sm text-signal-danger">Couldn&apos;t load your bookmarks.</p>
          <button type="button" onClick={() => refetch()} className="text-sm font-medium text-trace hover:underline">
            Try again
          </button>
        </div>
      )}

      {bookmarks && bookmarks.length === 0 && (
        <p className="text-sm text-ink-muted">
          You haven&apos;t bookmarked anything yet. Tap the bookmark icon on any problem to save it here.
        </p>
      )}

      {bookmarks && bookmarks.length > 0 && filtered.length === 0 && (
        <p className="text-sm text-ink-muted">No bookmarks match "{search}".</p>
      )}

      <div className="space-y-2">
        {filtered.map((bookmark) => (
          <ProblemListItem key={bookmark.algorithm.id} algorithm={bookmark.algorithm} />
        ))}
      </div>
    </main>
  );
}

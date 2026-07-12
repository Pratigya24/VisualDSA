import { Bookmark as BookmarkIcon } from "lucide-react";

import { useToggleBookmark } from "@/features/bookmarks/hooks/use-bookmarks";
import { cn } from "@/shared/utils/cn";

export function BookmarkButton({
  algorithmId,
  isBookmarked,
}: {
  algorithmId: string;
  isBookmarked: boolean;
}) {
  const toggle = useToggleBookmark();

  return (
    <button
      type="button"
      onClick={(event) => {
        event.preventDefault();
        event.stopPropagation();
        toggle.mutate({ algorithmId, isBookmarked });
      }}
      disabled={toggle.isPending}
      aria-pressed={isBookmarked}
      aria-label={isBookmarked ? "Remove bookmark" : "Add bookmark"}
      className="rounded-md p-1.5 text-ink-faint transition-colors hover:bg-canvas-overlay hover:text-trace disabled:opacity-50"
    >
      <BookmarkIcon
        className={cn("h-4 w-4", isBookmarked && "fill-trace text-trace")}
        aria-hidden
      />
    </button>
  );
}

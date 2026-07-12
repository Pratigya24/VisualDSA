import { CheckCircle2, Circle, CircleDot, RotateCcw } from "lucide-react";
import { Link } from "react-router-dom";

import type { AlgorithmSummary } from "@/features/algorithms/types";
import { BookmarkButton } from "@/features/bookmarks/components/bookmark-button";
import { DifficultyBadge } from "@/shared/components/difficulty-badge";

const STATUS_ICON = {
  not_started: <Circle className="h-4 w-4 text-ink-faint" aria-hidden />,
  in_progress: <CircleDot className="h-4 w-4 text-signal-warning" aria-hidden />,
  solved: <CheckCircle2 className="h-4 w-4 text-signal-success" aria-hidden />,
  needs_review: <RotateCcw className="h-4 w-4 text-trace" aria-hidden />,
};

const STATUS_LABEL = {
  not_started: "Not started",
  in_progress: "In progress",
  solved: "Solved",
  needs_review: "Needs review",
};

export function ProblemListItem({ algorithm }: { algorithm: AlgorithmSummary }) {
  return (
    <Link
      to={`/app/problems/${algorithm.slug}`}
      className="glass-surface flex items-center justify-between rounded-lg p-3 transition-colors hover:border-trace/50"
    >
      <div className="flex items-center gap-3">
        <span aria-label={STATUS_LABEL[algorithm.status]}>{STATUS_ICON[algorithm.status]}</span>
        <div>
          <p className="text-sm font-medium text-ink">{algorithm.title}</p>
          <p className="font-mono text-xs text-ink-faint">{algorithm.estimatedMinutes} min</p>
        </div>
      </div>
      <div className="flex items-center gap-2">
        <DifficultyBadge difficulty={algorithm.difficulty} />
        <BookmarkButton algorithmId={algorithm.id} isBookmarked={algorithm.isBookmarked} />
      </div>
    </Link>
  );
}

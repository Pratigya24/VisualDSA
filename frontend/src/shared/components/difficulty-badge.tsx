import type { Difficulty } from "@/features/algorithms/types";
import { cn } from "@/shared/utils/cn";

const STYLES: Record<Difficulty, string> = {
  easy: "bg-signal-success/15 text-signal-success",
  medium: "bg-signal-warning/15 text-signal-warning",
  hard: "bg-signal-danger/15 text-signal-danger",
};

export function DifficultyBadge({ difficulty }: { difficulty: Difficulty }) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium capitalize",
        STYLES[difficulty],
      )}
    >
      {difficulty}
    </span>
  );
}

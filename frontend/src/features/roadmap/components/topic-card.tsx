import { Lock } from "lucide-react";
import { Link } from "react-router-dom";

import type { RoadmapTopic } from "@/features/roadmap/types";
import { ProgressRing } from "@/shared/components/progress-ring";
import { cn } from "@/shared/utils/cn";

export function TopicCard({ topic }: { topic: RoadmapTopic }) {
  const progress = topic.algorithmCount > 0 ? topic.solvedCount / topic.algorithmCount : 0;

  const content = (
    <div
      className={cn(
        "glass-surface flex items-center justify-between rounded-lg p-4 transition-colors",
        topic.isUnlocked ? "hover:border-trace/50" : "opacity-60",
      )}
    >
      <div>
        <h3 className="flex items-center gap-2 font-medium text-ink">
          {topic.name}
          {!topic.isUnlocked && <Lock className="h-3.5 w-3.5 text-ink-faint" aria-hidden />}
        </h3>
        <p className="mt-1 line-clamp-2 max-w-sm text-sm text-ink-muted">{topic.description}</p>
        <p className="mt-2 font-mono text-xs text-ink-faint">
          {topic.solvedCount} / {topic.algorithmCount} solved
        </p>
      </div>
      <ProgressRing progress={progress} />
    </div>
  );

  if (!topic.isUnlocked) {
    return (
      <div role="group" aria-label={`${topic.name} (locked)`}>
        {content}
      </div>
    );
  }

  return (
    <Link to={`/app/roadmap/${topic.slug}`} aria-label={topic.name}>
      {content}
    </Link>
  );
}

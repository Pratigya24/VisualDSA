import { ArrowRight, Sparkles } from "lucide-react";
import { Link } from "react-router-dom";

import type { AlgorithmSummary } from "@/features/algorithms/types";
import { Button } from "@/shared/components/button";
import { DifficultyBadge } from "@/shared/components/difficulty-badge";

export function RecommendedProblemCard({ algorithm }: { algorithm: AlgorithmSummary | null }) {
  if (!algorithm) {
    return (
      <div className="glass-surface rounded-lg p-4">
        <p className="text-sm text-ink-muted">
          You&apos;ve attempted every problem in the catalog so far — nice work. More are on the way.
        </p>
      </div>
    );
  }

  return (
    <div className="glass-surface rounded-lg p-4">
      <div className="mb-2 flex items-center gap-1.5 text-xs font-medium text-trace-strong">
        <Sparkles className="h-3.5 w-3.5" aria-hidden />
        Recommended next
      </div>
      <div className="mb-3 flex items-center justify-between">
        <h3 className="font-medium text-ink">{algorithm.title}</h3>
        <DifficultyBadge difficulty={algorithm.difficulty} />
      </div>
      <Button asChild size="sm" variant="secondary">
        <Link to={`/app/problems/${algorithm.slug}`}>
          Start problem
          <ArrowRight className="h-3.5 w-3.5" aria-hidden />
        </Link>
      </Button>
    </div>
  );
}

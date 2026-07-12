import { Lock } from "lucide-react";
import { Link, useParams } from "react-router-dom";

import { ProblemListItem } from "@/features/algorithms/components/problem-list-item";
import { useAlgorithms } from "@/features/algorithms/hooks/use-algorithms";
import { useTopic } from "@/features/roadmap/hooks/use-topic";

export function TopicDetailPage() {
  const { slug } = useParams<{ slug: string }>();
  const { data: topic, isLoading: isTopicLoading, isError: isTopicError } = useTopic(slug);
  const { data: algorithmsResult, isLoading: isAlgorithmsLoading } = useAlgorithms(
    { topicId: topic?.id, limit: 50 },
    { enabled: Boolean(topic?.id) },
  );

  if (isTopicLoading) {
    return (
      <main className="mx-auto max-w-3xl px-6 py-8" aria-hidden>
        <div className="h-8 w-64 animate-pulse-trace rounded bg-canvas-overlay" />
      </main>
    );
  }

  if (isTopicError || !topic) {
    return (
      <main className="mx-auto max-w-3xl px-6 py-8">
        <p className="text-sm text-signal-danger">Couldn&apos;t find that topic.</p>
        <Link to="/app/roadmap" className="text-sm text-trace hover:underline">
          Back to roadmap
        </Link>
      </main>
    );
  }

  if (!topic.isUnlocked) {
    return (
      <main className="mx-auto max-w-3xl px-6 py-8">
        <div className="glass-surface flex flex-col items-center gap-3 rounded-lg p-10 text-center">
          <Lock className="h-6 w-6 text-ink-faint" aria-hidden />
          <p className="text-sm text-ink-muted">
            {topic.name} is still locked. Solve more problems in its prerequisite topics to unlock it.
          </p>
          <Link to="/app/roadmap" className="text-sm font-medium text-trace hover:underline">
            Back to roadmap
          </Link>
        </div>
      </main>
    );
  }

  return (
    <main className="mx-auto max-w-3xl px-6 py-8">
      <Link to="/app/roadmap" className="mb-4 inline-block text-xs text-ink-muted hover:text-trace">
        ← Roadmap
      </Link>
      <h1 className="mb-1 font-display text-2xl font-semibold">{topic.name}</h1>
      <p className="mb-6 max-w-2xl text-sm text-ink-muted">{topic.description}</p>
      <p className="mb-4 font-mono text-xs text-ink-faint">
        {topic.solvedCount} / {topic.algorithmCount} solved
      </p>

      {isAlgorithmsLoading && (
        <div className="space-y-2" aria-hidden>
          {[0, 1, 2].map((i) => (
            <div key={i} className="h-16 animate-pulse-trace rounded-lg bg-canvas-overlay" />
          ))}
        </div>
      )}

      {algorithmsResult && algorithmsResult.items.length === 0 && (
        <p className="text-sm text-ink-muted">No problems in this topic yet.</p>
      )}

      {algorithmsResult && algorithmsResult.items.length > 0 && (
        <div className="space-y-2">
          {algorithmsResult.items.map((algorithm) => (
            <ProblemListItem key={algorithm.id} algorithm={algorithm} />
          ))}
        </div>
      )}
    </main>
  );
}

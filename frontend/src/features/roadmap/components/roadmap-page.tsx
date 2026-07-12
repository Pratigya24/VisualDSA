import { TopicCard } from "@/features/roadmap/components/topic-card";
import { useRoadmap } from "@/features/roadmap/hooks/use-roadmap";

export function RoadmapPage() {
  const { data: topics, isLoading, isError, refetch } = useRoadmap();

  return (
    <main className="mx-auto max-w-3xl px-6 py-8">
      <h1 className="mb-1 font-display text-2xl font-semibold">Roadmap</h1>
      <p className="mb-6 text-sm text-ink-muted">
        Work through topics in order — each one unlocks once you've solved about half of what
        comes before it.
      </p>

      {isLoading && (
        <div className="space-y-3" aria-hidden>
          {[0, 1, 2, 3].map((i) => (
            <div key={i} className="h-20 animate-pulse-trace rounded-lg bg-canvas-overlay" />
          ))}
        </div>
      )}

      {isError && (
        <div className="glass-surface rounded-lg p-6 text-center">
          <p className="mb-3 text-sm text-signal-danger">Couldn&apos;t load the roadmap.</p>
          <button type="button" onClick={() => refetch()} className="text-sm font-medium text-trace hover:underline">
            Try again
          </button>
        </div>
      )}

      {topics && topics.length === 0 && (
        <p className="text-sm text-ink-muted">No topics are available yet — check back soon.</p>
      )}

      {topics && topics.length > 0 && (
        <div className="space-y-3">
          {topics.map((topic) => (
            <TopicCard key={topic.id} topic={topic} />
          ))}
        </div>
      )}
    </main>
  );
}

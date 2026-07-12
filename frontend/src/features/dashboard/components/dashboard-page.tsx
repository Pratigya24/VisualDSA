import { Flame, ListChecks, Target } from "lucide-react";

import { useCurrentUser } from "@/features/auth/hooks/use-current-user";
import { DifficultyBreakdownChart } from "@/features/dashboard/components/difficulty-breakdown-chart";
import { RecommendedProblemCard } from "@/features/dashboard/components/recommended-problem-card";
import { StatCard } from "@/features/dashboard/components/stat-card";
import { WeeklyActivityChart } from "@/features/dashboard/components/weekly-activity-chart";
import { useDashboard } from "@/features/dashboard/hooks/use-dashboard";

function DashboardSkeleton() {
  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-3" aria-hidden>
      {[0, 1, 2].map((i) => (
        <div key={i} className="h-20 animate-pulse-trace rounded-lg bg-canvas-overlay" />
      ))}
    </div>
  );
}

export function DashboardPage() {
  const { data: user } = useCurrentUser();
  const { data, isLoading, isError, refetch } = useDashboard();

  return (
    <main className="mx-auto max-w-5xl px-6 py-8">
      <h1 className="mb-1 font-display text-2xl font-semibold">
        {user ? `Welcome back, ${user.displayName.split(" ")[0]}` : "Dashboard"}
      </h1>
      <p className="mb-6 text-sm text-ink-muted">Here&apos;s where you left off.</p>

      {isLoading && <DashboardSkeleton />}

      {isError && (
        <div className="glass-surface rounded-lg p-6 text-center">
          <p className="mb-3 text-sm text-signal-danger">Couldn&apos;t load your dashboard.</p>
          <button
            type="button"
            onClick={() => refetch()}
            className="text-sm font-medium text-trace hover:underline"
          >
            Try again
          </button>
        </div>
      )}

      {data && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            <StatCard label="Day streak" value={data.streakCount} icon={Flame} accent="trace" />
            <StatCard label="Problems solved" value={data.totalSolved} icon={ListChecks} accent="success" />
            <StatCard label="Problems attempted" value={data.totalAttempted} icon={Target} accent="visited" />
          </div>

          <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
            <WeeklyActivityChart data={data.weeklyActivity} />
            <DifficultyBreakdownChart breakdown={data.difficultyBreakdown} />
          </div>

          <RecommendedProblemCard algorithm={data.recommendedAlgorithm} />
        </div>
      )}
    </main>
  );
}

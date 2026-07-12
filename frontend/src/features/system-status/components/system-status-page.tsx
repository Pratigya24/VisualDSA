import { CheckCircle2, Loader2, XCircle } from "lucide-react";

import { useSystemHealth } from "@/features/system-status/hooks/use-system-health";
import { cn } from "@/shared/utils/cn";

function StatusRow({ label, ok }: { label: string; ok: boolean }) {
  return (
    <div className="flex items-center justify-between border-b border-canvas-border py-3 last:border-b-0">
      <span className="font-mono text-sm text-ink-muted">{label}</span>
      <span
        className={cn(
          "flex items-center gap-1.5 text-sm font-medium",
          ok ? "text-signal-success" : "text-signal-danger",
        )}
      >
        {ok ? <CheckCircle2 className="h-4 w-4" aria-hidden /> : <XCircle className="h-4 w-4" aria-hidden />}
        {ok ? "connected" : "unreachable"}
      </span>
    </div>
  );
}

export function SystemStatusPage() {
  const { data, isLoading, isError, error } = useSystemHealth();

  return (
    <main className="mx-auto flex min-h-screen max-w-md flex-col items-center justify-center px-6">
      <div className="glass-surface w-full rounded-lg p-6" role="status" aria-live="polite">
        <div className="mb-4 flex items-center gap-2">
          <span
            className={cn(
              "h-2.5 w-2.5 rounded-full",
              isLoading && "animate-pulse-trace bg-trace",
              !isLoading && data?.status === "ok" && "bg-signal-success",
              !isLoading && data?.status === "degraded" && "bg-signal-warning",
              isError && "bg-signal-danger",
            )}
            aria-hidden
          />
          <h1 className="font-display text-lg font-semibold">VisualDSA AI — Platform Status</h1>
        </div>

        {isLoading && (
          <p className="flex items-center gap-2 text-sm text-ink-muted">
            <Loader2 className="h-4 w-4 animate-spin" aria-hidden />
            Checking backend connectivity…
          </p>
        )}

        {isError && (
          <p className="text-sm text-signal-danger">
            Could not reach the API{error instanceof Error ? `: ${error.message}` : "."} Confirm the
            backend is running and <code className="font-mono">VITE_API_BASE_URL</code> is set correctly.
          </p>
        )}

        {data && (
          <div>
            <StatusRow label="mongodb" ok={data.dependencies.mongodb} />
            <StatusRow label="redis" ok={data.dependencies.redis} />
          </div>
        )}
      </div>
    </main>
  );
}

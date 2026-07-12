import type { LucideIcon } from "lucide-react";

interface StatCardProps {
  label: string;
  value: string | number;
  icon: LucideIcon;
  accent?: "trace" | "visited" | "success";
}

const ACCENT_STYLES = {
  trace: "text-trace bg-trace/10",
  visited: "text-visited bg-visited/10",
  success: "text-signal-success bg-signal-success/10",
};

export function StatCard({ label, value, icon: Icon, accent = "trace" }: StatCardProps) {
  return (
    <div className="glass-surface rounded-lg p-4">
      <div className="flex items-center gap-3">
        <span className={`flex h-9 w-9 items-center justify-center rounded-md ${ACCENT_STYLES[accent]}`}>
          <Icon className="h-4 w-4" aria-hidden />
        </span>
        <div>
          <p className="text-2xl font-semibold text-ink">{value}</p>
          <p className="text-xs text-ink-muted">{label}</p>
        </div>
      </div>
    </div>
  );
}

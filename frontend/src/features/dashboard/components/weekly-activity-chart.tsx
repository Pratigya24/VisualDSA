import { Bar, BarChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import type { DailyActivity } from "@/features/dashboard/types";

function formatDayLabel(isoDate: string): string {
  const date = new Date(`${isoDate}T00:00:00`);
  return date.toLocaleDateString(undefined, { weekday: "short" });
}

export function WeeklyActivityChart({ data }: { data: DailyActivity[] }) {
  const chartData = data.map((day) => ({ ...day, label: formatDayLabel(day.date) }));
  const hasActivity = data.some((day) => day.count > 0);

  return (
    <div className="glass-surface rounded-lg p-4">
      <h2 className="mb-3 text-sm font-medium text-ink-muted">Weekly activity</h2>
      {hasActivity ? (
        <ResponsiveContainer width="100%" height={160}>
          <BarChart data={chartData} margin={{ top: 4, right: 4, left: -24, bottom: 0 }}>
            <XAxis
              dataKey="label"
              tick={{ fill: "#9AA1B2", fontSize: 12 }}
              axisLine={false}
              tickLine={false}
            />
            <YAxis tick={{ fill: "#9AA1B2", fontSize: 12 }} axisLine={false} tickLine={false} allowDecimals={false} />
            <Tooltip
              cursor={{ fill: "rgba(110,91,255,0.08)" }}
              contentStyle={{
                background: "#111319",
                border: "1px solid #262A35",
                borderRadius: 8,
                fontSize: 12,
              }}
              labelStyle={{ color: "#E7E9EE" }}
            />
            <Bar dataKey="count" fill="#6E5BFF" radius={[4, 4, 0, 0]} maxBarSize={28} />
          </BarChart>
        </ResponsiveContainer>
      ) : (
        <p className="flex h-40 items-center justify-center text-sm text-ink-faint">
          No activity yet this week — solve a problem to get started.
        </p>
      )}
    </div>
  );
}

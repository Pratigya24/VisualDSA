import { Cell, Pie, PieChart, ResponsiveContainer } from "recharts";

import type { DifficultyBreakdown } from "@/features/dashboard/types";

const COLORS = {
  easy: "#3DD68C",
  medium: "#F5A623",
  hard: "#F0556B",
};

export function DifficultyBreakdownChart({ breakdown }: { breakdown: DifficultyBreakdown }) {
  const total = breakdown.easy + breakdown.medium + breakdown.hard;
  const data = [
    { name: "Easy", value: breakdown.easy, color: COLORS.easy },
    { name: "Medium", value: breakdown.medium, color: COLORS.medium },
    { name: "Hard", value: breakdown.hard, color: COLORS.hard },
  ];

  return (
    <div className="glass-surface rounded-lg p-4">
      <h2 className="mb-3 text-sm font-medium text-ink-muted">Solved by difficulty</h2>
      {total === 0 ? (
        <p className="flex h-40 items-center justify-center text-sm text-ink-faint">
          Solve your first problem to see a breakdown here.
        </p>
      ) : (
        <div className="flex items-center gap-6">
          <ResponsiveContainer width={140} height={140}>
            <PieChart>
              <Pie data={data} dataKey="value" innerRadius={40} outerRadius={62} paddingAngle={2}>
                {data.map((entry) => (
                  <Cell key={entry.name} fill={entry.color} stroke="none" />
                ))}
              </Pie>
            </PieChart>
          </ResponsiveContainer>
          <ul className="space-y-2 text-sm">
            {data.map((entry) => (
              <li key={entry.name} className="flex items-center gap-2">
                <span
                  className="h-2.5 w-2.5 rounded-full"
                  style={{ backgroundColor: entry.color }}
                  aria-hidden
                />
                <span className="text-ink-muted">{entry.name}</span>
                <span className="font-mono text-ink">{entry.value}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

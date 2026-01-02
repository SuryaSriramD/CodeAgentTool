"use client";

import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Legend,
  Tooltip,
} from "recharts";
import { type SeveritySummary } from "@/lib/api-client";

interface SeverityDistributionChartProps {
  data?: SeveritySummary;
}

const COLORS = {
  critical: "#ef4444",
  high: "#f59e0b",
  medium: "#6366f1",
  low: "#10b981",
};

export function SeverityDistributionChart({
  data,
}: SeverityDistributionChartProps) {
  if (!data) {
    return (
      <div className="bg-card border border-border rounded-lg p-6">
        <h3 className="font-semibold mb-4">Severity Distribution</h3>
        <div className="flex items-center justify-center h-64 text-muted">
          No data available
        </div>
      </div>
    );
  }

  const chartData = [
    { name: "Critical", value: data.critical, color: COLORS.critical },
    { name: "High", value: data.high, color: COLORS.high },
    { name: "Medium", value: data.medium, color: COLORS.medium },
    { name: "Low", value: data.low, color: COLORS.low },
  ].filter((item) => item.value > 0); // Only show non-zero values

  const totalIssues = data.critical + data.high + data.medium + data.low;

  if (totalIssues === 0) {
    return (
      <div className="bg-card border border-border rounded-lg p-6">
        <h3 className="font-semibold mb-4">Severity Distribution</h3>
        <div className="flex flex-col items-center justify-center h-64 text-muted">
          <p className="text-lg">🎉 No issues found!</p>
          <p className="text-sm mt-2">All scans are clean</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-card border border-border rounded-lg p-6">
      <h3 className="font-semibold mb-4">Severity Distribution</h3>
      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={(entry: any) =>
              `${entry.name}: ${((entry.percent || 0) * 100).toFixed(0)}%`
            }
            outerRadius={80}
            fill="#8884d8"
            dataKey="value"
          >
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{
              backgroundColor: "#1a1f3a",
              border: "1px solid #2d3748",
              borderRadius: "0.5rem",
            }}
          />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
      <div className="mt-4 grid grid-cols-2 gap-4">
        {chartData.map((item) => (
          <div key={item.name} className="flex items-center gap-2">
            <div
              className="w-3 h-3 rounded-full"
              style={{ backgroundColor: item.color }}
            />
            <span className="text-sm text-muted">
              {item.name}:{" "}
              <span className="font-semibold text-foreground">
                {item.value}
              </span>
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

"use client";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

interface SeverityData {
  critical: number;
  high: number;
  medium: number;
  low: number;
}

interface SeverityChartProps {
  data?: SeverityData;
}

export function SeverityChart({ data }: SeverityChartProps) {
  // Transform the summary data into chart format
  const chartData = data
    ? [
        {
          name: "Total",
          critical: data.critical,
          high: data.high,
          medium: data.medium,
          low: data.low,
        },
      ]
    : [
        { name: "Bandit", critical: 1, high: 2, medium: 3, low: 2 },
        { name: "Semgrep", critical: 1, high: 2, medium: 2, low: 1 },
        { name: "Dep Check", critical: 0, high: 0, medium: 1, low: 0 },
      ];
  return (
    <div className="bg-card border border-border rounded-lg p-6">
      <h3 className="font-semibold mb-4">Severity Distribution</h3>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#2d3748" />
          <XAxis dataKey="name" stroke="#71717a" />
          <YAxis stroke="#71717a" />
          <Tooltip
            contentStyle={{
              backgroundColor: "#1a1f3a",
              border: "1px solid #2d3748",
              borderRadius: "0.5rem",
            }}
          />
          <Legend />
          <Bar dataKey="critical" stackId="a" fill="#ef4444" />
          <Bar dataKey="high" stackId="a" fill="#f59e0b" />
          <Bar dataKey="medium" stackId="a" fill="#6366f1" />
          <Bar dataKey="low" stackId="a" fill="#10b981" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

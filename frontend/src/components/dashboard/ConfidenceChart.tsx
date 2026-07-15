import { memo, useMemo } from "react";
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from "recharts";
import { Card } from "@/components/ui/Card";
import { SectionHeader } from "@/components/ui/SectionHeader";
import { Skeleton } from "@/components/ui/skeleton";
import { EmptyState } from "@/components/ui/EmptyState";
import { CONFIDENCE_STATUS_COLORS } from "@/lib/chartColors";
import type { StatusCount } from "@/lib/types";

const STATUS_LABELS: Record<string, string> = {
  HIGH: "High Confidence",
  MEDIUM: "Medium Confidence",
  LOW: "Low Confidence",
  NEEDS_REVIEW: "Needs Review",
};

interface ConfidenceChartProps {
  data: StatusCount[] | undefined;
  isLoading: boolean;
}

/** Directly visualizes DashboardSummary.screenings_by_confidence_status —
 * no client-side computation beyond reshaping for Recharts' prop shape. */
export const ConfidenceChart = memo(function ConfidenceChart({ data, isLoading }: ConfidenceChartProps) {
  const chartData = useMemo(
    () =>
      (data ?? []).map((d) => ({
        name: STATUS_LABELS[d.status] ?? d.status,
        value: d.count,
        color: CONFIDENCE_STATUS_COLORS[d.status] ?? "#94A3B8",
      })),
    [data]
  );

  const total = useMemo(() => chartData.reduce((sum, d) => sum + d.value, 0), [chartData]);

  return (
    <Card>
      <SectionHeader title="Confidence Distribution" description="Screening Confidence Score across all screenings" />
      {isLoading ? (
        <Skeleton className="h-64 w-full" />
      ) : total === 0 ? (
        <EmptyState title="No screenings yet" description="Confidence distribution will appear once screenings are submitted." />
      ) : (
        <ResponsiveContainer width="100%" height={260}>
          <PieChart>
            <Pie data={chartData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={90} label={(entry) => entry.name}>
              {chartData.map((entry) => (
                <Cell key={entry.name} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      )}
    </Card>
  );
});

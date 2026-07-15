import { memo, useMemo } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from "recharts";
import { Card } from "@/components/ui/Card";
import { SectionHeader } from "@/components/ui/SectionHeader";
import { Skeleton } from "@/components/ui/skeleton";
import { EmptyState } from "@/components/ui/EmptyState";
import { RISK_LEVEL_COLORS } from "@/lib/chartColors";
import type { StatusCount } from "@/lib/types";

const LEVEL_LABELS: Record<string, string> = { LOW: "Low", MODERATE: "Moderate", HIGH: "High" };

interface RiskDistributionChartProps {
  data: StatusCount[] | undefined;
  isLoading: boolean;
}

/** Directly visualizes DashboardSummary.screenings_by_risk_level. Worth
 * noting in the UI (not just this comment): risk_level is only ever set
 * for HIGH-confidence screenings — Arogent Risk never runs otherwise — so
 * this reflects risk among screenings that passed the confidence gate,
 * not all screenings submitted. */
export const RiskDistributionChart = memo(function RiskDistributionChart({ data, isLoading }: RiskDistributionChartProps) {
  const chartData = useMemo(
    () =>
      (data ?? []).map((d) => ({
        name: LEVEL_LABELS[d.status] ?? d.status,
        count: d.count,
        color: RISK_LEVEL_COLORS[d.status] ?? "#94A3B8",
      })),
    [data]
  );

  const total = useMemo(() => chartData.reduce((sum, d) => sum + d.count, 0), [chartData]);

  return (
    <Card>
      <SectionHeader
        title="Diabetes Risk Distribution"
        description="Among HIGH-confidence screenings only — Arogent Risk never runs on lower-confidence data"
      />
      {isLoading ? (
        <Skeleton className="h-64 w-full" />
      ) : total === 0 ? (
        <EmptyState title="No risk predictions yet" description="This fills in once a HIGH-confidence screening has been submitted." />
      ) : (
        <ResponsiveContainer width="100%" height={260}>
          <BarChart data={chartData}>
            <XAxis dataKey="name" tick={{ fontSize: 12 }} />
            <YAxis allowDecimals={false} tick={{ fontSize: 12 }} />
            <Tooltip />
            <Bar dataKey="count" radius={[4, 4, 0, 0]}>
              {chartData.map((entry) => (
                <Cell key={entry.name} fill={entry.color} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      )}
    </Card>
  );
});

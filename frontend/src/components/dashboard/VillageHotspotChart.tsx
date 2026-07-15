import { memo, useMemo } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer } from "recharts";
import { Card } from "@/components/ui/Card";
import { SectionHeader } from "@/components/ui/SectionHeader";
import { Skeleton } from "@/components/ui/skeleton";
import { EmptyState } from "@/components/ui/EmptyState";
import { CHART_COLORS } from "@/lib/chartColors";
import type { VillageSummary } from "@/lib/types";

interface VillageHotspotChartProps {
  data: VillageSummary[] | undefined;
  isLoading: boolean;
}

/** Directly visualizes DashboardSummary.village_summaries — total
 * screenings vs. high-risk count per village, both fields already
 * computed server-side (app/services/dashboard_service.py). */
export const VillageHotspotChart = memo(function VillageHotspotChart({ data, isLoading }: VillageHotspotChartProps) {
  const chartData = useMemo(
    () =>
      (data ?? [])
        .map((v) => ({
          village: v.village,
          totalScreenings: v.total_screenings,
          highRisk: v.high_risk_count,
          needsReview: v.needs_review_count,
        }))
        .sort((a, b) => b.totalScreenings - a.totalScreenings),
    [data]
  );

  return (
    <Card>
      <SectionHeader title="Village Hotspots" description="Screening coverage and high-risk counts by village" />
      {isLoading ? (
        <Skeleton className="h-72 w-full" />
      ) : chartData.length === 0 ? (
        <EmptyState title="No village data yet" description="This fills in once screenings have been submitted across villages." />
      ) : (
        <ResponsiveContainer width="100%" height={Math.max(280, chartData.length * 50)}>
          <BarChart data={chartData} layout="vertical" margin={{ left: 24 }}>
            <XAxis type="number" allowDecimals={false} tick={{ fontSize: 12 }} />
            <YAxis dataKey="village" type="category" tick={{ fontSize: 12 }} width={110} />
            <Tooltip />
            <Legend />
            <Bar dataKey="totalScreenings" name="Total Screenings" fill={CHART_COLORS.primary} radius={[0, 4, 4, 0]} />
            <Bar dataKey="highRisk" name="High Risk" fill={CHART_COLORS.danger} radius={[0, 4, 4, 0]} />
            <Bar dataKey="needsReview" name="Needs Review" fill={CHART_COLORS.warning} radius={[0, 4, 4, 0]} />
          </BarChart>
        </ResponsiveContainer>
      )}
    </Card>
  );
});

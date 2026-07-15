import { memo, useMemo } from "react";
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from "recharts";
import { Card } from "@/components/ui/Card";
import { SectionHeader } from "@/components/ui/SectionHeader";
import { Skeleton } from "@/components/ui/skeleton";
import { EmptyState } from "@/components/ui/EmptyState";
import { REFERRAL_STATUS_COLORS } from "@/lib/chartColors";
import type { Referral } from "@/lib/types";

const STATUS_LABELS: Record<string, string> = { PENDING: "Pending", REFERRED: "Referred", COMPLETED: "Completed" };

interface ReferralChartProps {
  referrals: Referral[] | undefined;
  isLoading: boolean;
}

/**
 * The one chart in Module 9 built from a client-side tally rather than an
 * aggregate field the backend already computed: DashboardSummary doesn't
 * expose a referral-status breakdown, only `pending_referrals_count`. Each
 * referral's `status` is still 100% backend-decided — this only counts
 * how many fall into each already-assigned bucket for the chart. No
 * status is inferred, predicted, or decided here.
 */
export const ReferralChart = memo(function ReferralChart({ referrals, isLoading }: ReferralChartProps) {
  const chartData = useMemo(() => {
    const counts: Record<string, number> = {};
    for (const referral of referrals ?? []) {
      counts[referral.status] = (counts[referral.status] ?? 0) + 1;
    }
    return Object.entries(counts).map(([status, count]) => ({
      name: STATUS_LABELS[status] ?? status,
      value: count,
      color: REFERRAL_STATUS_COLORS[status] ?? "#94A3B8",
    }));
  }, [referrals]);

  const total = useMemo(() => chartData.reduce((sum, d) => sum + d.value, 0), [chartData]);

  return (
    <Card>
      <SectionHeader title="Referral Status" description="Referrals generated from HIGH-risk screenings, by current status" />
      {isLoading ? (
        <Skeleton className="h-64 w-full" />
      ) : total === 0 ? (
        <EmptyState title="No referrals yet" description="Referrals generated from high-risk screenings will appear here." />
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

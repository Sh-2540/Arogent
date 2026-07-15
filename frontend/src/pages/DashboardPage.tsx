import { useMemo } from "react";
import { Users, ShieldCheck, AlertTriangle, ClipboardList, RefreshCw } from "lucide-react";
import { AppShell } from "@/components/layout/AppShell";
import { MetricCard } from "@/components/ui/MetricCard";
import { Skeleton } from "@/components/ui/skeleton";
import { ErrorBanner } from "@/components/ui/ErrorBanner";
import { Button } from "@/components/ui/button";
import { ConfidenceChart } from "@/components/dashboard/ConfidenceChart";
import { RiskDistributionChart } from "@/components/dashboard/RiskDistributionChart";
import { ReferralChart } from "@/components/dashboard/ReferralChart";
import { VillageHotspotChart } from "@/components/dashboard/VillageHotspotChart";
import { RecentScreeningsTable } from "@/components/dashboard/RecentScreeningsTable";
import { useDashboard } from "@/hooks/useDashboard";
import { ApiError } from "@/api/axios";

export function DashboardPage() {
  const { summary, referrals, isLoading, isError, error, refetch } = useDashboard();

  // Formatting only — dividing two numbers the backend already computed
  // is display arithmetic, not a new business metric (no thresholds, no
  // scoring, nothing decided). See Module 9's architecture notes.
  const highConfidencePercent = useMemo(() => {
    if (!summary || summary.total_screenings === 0) return null;
    const highCount = summary.screenings_by_confidence_status.find((s) => s.status === "HIGH")?.count ?? 0;
    return Math.round((highCount / summary.total_screenings) * 100);
  }, [summary]);

  const highRiskScreeningsCount = useMemo(
    () => summary?.screenings_by_risk_level.find((s) => s.status === "HIGH")?.count ?? 0,
    [summary]
  );

  if (isError) {
    const message = error instanceof ApiError ? error.message : "Unable to reach the server. Check your connection.";
    return (
      <AppShell pageTitle="District Dashboard">
        <ErrorBanner message={message} />
        <Button variant="secondary" className="mt-4" onClick={() => refetch()}>
          <RefreshCw className="h-4 w-4" aria-hidden="true" />
          Retry
        </Button>
      </AppShell>
    );
  }

  return (
    <AppShell pageTitle="District Dashboard">
      <div className="space-y-6">
        {/* --- Top Metrics --- */}
        <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
          {isLoading ? (
            <>
              <Skeleton className="h-28" />
              <Skeleton className="h-28" />
              <Skeleton className="h-28" />
              <Skeleton className="h-28" />
            </>
          ) : (
            <>
              <MetricCard
                label="Total Screenings"
                value={summary?.total_screenings ?? 0}
                tone="primary"
                icon={<Users className="h-4 w-4" aria-hidden="true" />}
              />
              <MetricCard
                label="High Confidence"
                value={highConfidencePercent !== null ? `${highConfidencePercent}%` : "—"}
                tone="success"
                icon={<ShieldCheck className="h-4 w-4" aria-hidden="true" />}
              />
              <MetricCard
                label="High Risk Screenings"
                value={highRiskScreeningsCount}
                tone="danger"
                icon={<AlertTriangle className="h-4 w-4" aria-hidden="true" />}
                helperText="Among HIGH-confidence screenings"
              />
              <MetricCard
                label="Pending Referrals"
                value={summary?.pending_referrals_count ?? 0}
                tone="warning"
                icon={<ClipboardList className="h-4 w-4" aria-hidden="true" />}
              />
            </>
          )}
        </div>

        {/* --- Charts --- */}
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <ConfidenceChart data={summary?.screenings_by_confidence_status} isLoading={isLoading} />
          <RiskDistributionChart data={summary?.screenings_by_risk_level} isLoading={isLoading} />
          <ReferralChart referrals={referrals} isLoading={isLoading} />
          <VillageHotspotChart data={summary?.village_summaries} isLoading={isLoading} />
        </div>

        {/* --- Recent Activity (honestly labeled placeholder — see component docstring) --- */}
        <RecentScreeningsTable />
      </div>
    </AppShell>
  );
}

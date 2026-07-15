import { useQuery } from "@tanstack/react-query";
import { getDashboardSummary, getAllReferrals } from "@/api/dashboard";

const REFETCH_INTERVAL_MS = 30_000; // background refetch — dashboard should feel live without a manual reload

/**
 * Combines both queries the Dashboard needs into one hook so
 * DashboardPage doesn't juggle two separate loading/error states itself.
 * No aggregation happens here beyond what useQuery itself does — the
 * summary is echoed as-is; referrals are handed back as a raw list for
 * chart components to tally (see api/dashboard.ts's note on why that's
 * still just visualization).
 */
export function useDashboard() {
  const summaryQuery = useQuery({
    queryKey: ["dashboard", "summary"],
    queryFn: getDashboardSummary,
    refetchInterval: REFETCH_INTERVAL_MS,
  });

  const referralsQuery = useQuery({
    queryKey: ["dashboard", "referrals"],
    queryFn: getAllReferrals,
    refetchInterval: REFETCH_INTERVAL_MS,
  });

  return {
    summary: summaryQuery.data,
    referrals: referralsQuery.data,
    isLoading: summaryQuery.isLoading || referralsQuery.isLoading,
    isError: summaryQuery.isError || referralsQuery.isError,
    error: summaryQuery.error ?? referralsQuery.error,
    refetch: () => {
      summaryQuery.refetch();
      referralsQuery.refetch();
    },
  };
}

import { axiosInstance } from "./axios";
import type { DashboardSummary, Referral } from "@/lib/types";

export async function getDashboardSummary(): Promise<DashboardSummary> {
  const response = await axiosInstance.get<DashboardSummary>("/dashboard");
  return response.data;
}

/**
 * Unfiltered — fetches every referral so useDashboard can tally counts per
 * status for the Referral chart. This is the one place a chart is built
 * from a raw list rather than an aggregate field the backend already
 * computed; see Module 9's architecture notes for why that's still just
 * visualization, not new business logic (no status is decided here, only
 * counted).
 */
export async function getAllReferrals(): Promise<Referral[]> {
  const response = await axiosInstance.get<Referral[]>("/referrals");
  return response.data;
}

/**
 * Raw hex values for Recharts (which needs literal color strings, not
 * Tailwind classes) — copied from index.css's @theme tokens so charts
 * never visually diverge from the badges that use the same status values
 * (ConfidenceBadge, RiskBadge, ReferralBadge). If a token changes in
 * index.css, update here too.
 */
export const CHART_COLORS = {
  primary: "#1D5FA3",
  success: "#1F8556",
  warning: "#B7791F",
  danger: "#C1293B",
  neutral: "#94A3B8",
} as const;

export const CONFIDENCE_STATUS_COLORS: Record<string, string> = {
  HIGH: CHART_COLORS.success,
  MEDIUM: CHART_COLORS.warning,
  LOW: CHART_COLORS.warning,
  NEEDS_REVIEW: CHART_COLORS.danger,
};

export const RISK_LEVEL_COLORS: Record<string, string> = {
  LOW: CHART_COLORS.success,
  MODERATE: CHART_COLORS.warning,
  HIGH: CHART_COLORS.danger,
};

export const REFERRAL_STATUS_COLORS: Record<string, string> = {
  PENDING: CHART_COLORS.warning,
  REFERRED: CHART_COLORS.primary,
  COMPLETED: CHART_COLORS.success,
};

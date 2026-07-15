import type { ReactNode } from "react";
import { cn } from "@/lib/utils";
import { Card } from "./Card";
import type { BadgeTone } from "./StatusBadge";

const ACCENT_COLOR: Record<BadgeTone, string> = {
  primary: "text-primary-600",
  success: "text-success-600",
  warning: "text-warning-600",
  danger: "text-danger-600",
  neutral: "text-neutral-700",
};

interface MetricCardProps {
  label: string;
  value: string | number;
  tone?: BadgeTone;
  icon?: ReactNode;
  helperText?: string;
}

/** A single dashboard number with a label — the district dashboard's
 * building block for "high-confidence screenings," "referrals pending," etc. */
export function MetricCard({ label, value, tone = "neutral", icon, helperText }: MetricCardProps) {
  return (
    <Card className="flex flex-col gap-1">
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium text-neutral-500">{label}</span>
        {icon && <span className={ACCENT_COLOR[tone]}>{icon}</span>}
      </div>
      <span className={cn("font-data text-3xl font-semibold", ACCENT_COLOR[tone])}>{value}</span>
      {helperText && <span className="text-xs text-neutral-500">{helperText}</span>}
    </Card>
  );
}

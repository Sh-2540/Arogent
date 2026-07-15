import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

export type BadgeTone = "primary" | "success" | "warning" | "danger" | "neutral";

const TONE_STYLES: Record<BadgeTone, string> = {
  primary: "bg-primary-50 text-primary-700 ring-primary-200",
  success: "bg-success-50 text-success-700 ring-success-100",
  warning: "bg-warning-50 text-warning-700 ring-warning-100",
  danger: "bg-danger-50 text-danger-700 ring-danger-100",
  neutral: "bg-neutral-100 text-neutral-600 ring-neutral-200",
};

interface StatusBadgeProps {
  tone: BadgeTone;
  icon?: ReactNode;
  children: ReactNode;
  className?: string;
}

/**
 * Generic pill badge — ConfidenceBadge, RiskBadge, and ReferralBadge are
 * all thin wrappers around this that map a domain enum to a tone + label,
 * so the visual language (shape, weight, ring) never has to be redefined
 * per-badge-type.
 */
export function StatusBadge({ tone, icon, children, className }: StatusBadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold ring-1 ring-inset",
        TONE_STYLES[tone],
        className
      )}
    >
      {icon}
      {children}
    </span>
  );
}

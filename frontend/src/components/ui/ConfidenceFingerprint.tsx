import { cn } from "@/lib/utils";
import type { ConfidenceBreakdown } from "@/lib/types";

interface Signal {
  label: string;
  value: number;
}

function scoreTone(score: number): "success" | "warning" | "danger" {
  if (score >= 80) return "success";
  if (score >= 50) return "warning";
  return "danger";
}

const BAR_COLOR: Record<"success" | "warning" | "danger", string> = {
  success: "bg-success-600",
  warning: "bg-warning-600",
  danger: "bg-danger-600",
};

const TRACK_COLOR: Record<"success" | "warning" | "danger", string> = {
  success: "bg-success-50",
  warning: "bg-warning-50",
  danger: "bg-danger-50",
};

/**
 * The Confidence Fingerprint — Arogent's signature visual element.
 *
 * This isn't decoration: it's the actual mechanism behind the Screening
 * Confidence Score made visible. Instead of a single number, a viewer can
 * see in ~2 seconds *why* the score is what it is — which signal is
 * pulling it down. Used compact (in list rows) and expanded (Result
 * screen) via the `size` prop, but the visual language never changes.
 */
export function ConfidenceFingerprint({
  breakdown,
  size = "default",
  className,
}: {
  breakdown: ConfidenceBreakdown;
  size?: "compact" | "default";
  className?: string;
}) {
  const signals: Signal[] = [
    { label: "Clinical", value: breakdown.clinical_consistency_score },
    { label: "Historical", value: breakdown.historical_consistency_score },
    { label: "Behaviour", value: breakdown.behaviour_consistency_score },
    { label: "Geographic", value: breakdown.geographic_consistency_score },
  ];

  const barHeight = size === "compact" ? "h-1.5" : "h-2.5";
  const labelWidth = size === "compact" ? "w-16" : "w-24";
  const gap = size === "compact" ? "gap-1" : "gap-2";

  return (
    <div className={cn("flex flex-col", gap, className)}>
      {signals.map((signal) => {
        const tone = scoreTone(signal.value);
        return (
          <div key={signal.label} className="flex items-center gap-3">
            <span
              className={cn(
                labelWidth,
                "shrink-0 text-right text-xs font-medium text-neutral-500",
                size === "compact" && "text-[11px]"
              )}
            >
              {signal.label}
            </span>
            <div className={cn("flex-1 overflow-hidden rounded-full", barHeight, TRACK_COLOR[tone])}>
              <div
                className={cn("h-full rounded-full transition-all", BAR_COLOR[tone])}
                style={{ width: `${Math.max(signal.value, 4)}%` }}
              />
            </div>
            {size !== "compact" && (
              <span className="font-data w-10 shrink-0 text-right text-xs font-semibold text-neutral-700">
                {Math.round(signal.value)}
              </span>
            )}
          </div>
        );
      })}
    </div>
  );
}

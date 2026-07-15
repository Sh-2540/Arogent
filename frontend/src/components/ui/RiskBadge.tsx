import { StatusBadge, type BadgeTone } from "./StatusBadge";
import { RiskLevel } from "@/lib/constants";

const CONFIG: Record<RiskLevel, { label: string; tone: BadgeTone }> = {
  LOW: { label: "Low Risk", tone: "success" },
  MODERATE: { label: "Moderate Risk", tone: "warning" },
  HIGH: { label: "High Risk", tone: "danger" },
};

export function RiskBadge({ level }: { level: RiskLevel }) {
  const config = CONFIG[level];
  return <StatusBadge tone={config.tone}>{config.label}</StatusBadge>;
}

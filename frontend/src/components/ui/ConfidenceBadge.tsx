import { CheckCircle2, AlertTriangle, HelpCircle, ShieldAlert } from "lucide-react";
import { StatusBadge, type BadgeTone } from "./StatusBadge";
import { ConfidenceStatus } from "@/lib/constants";

const CONFIG: Record<ConfidenceStatus, { label: string; tone: BadgeTone; icon: React.ReactNode }> = {
  HIGH: { label: "High Confidence", tone: "success", icon: <CheckCircle2 className="h-3.5 w-3.5" /> },
  MEDIUM: { label: "Medium Confidence", tone: "warning", icon: <HelpCircle className="h-3.5 w-3.5" /> },
  LOW: { label: "Low Confidence", tone: "warning", icon: <AlertTriangle className="h-3.5 w-3.5" /> },
  NEEDS_REVIEW: { label: "Needs Review", tone: "danger", icon: <ShieldAlert className="h-3.5 w-3.5" /> },
};

export function ConfidenceBadge({ status }: { status: ConfidenceStatus }) {
  const config = CONFIG[status];
  return (
    <StatusBadge tone={config.tone} icon={config.icon}>
      {config.label}
    </StatusBadge>
  );
}

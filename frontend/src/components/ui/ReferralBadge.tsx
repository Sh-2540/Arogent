import { StatusBadge, type BadgeTone } from "./StatusBadge";
import { ReferralStatus } from "@/lib/constants";

const CONFIG: Record<ReferralStatus, { label: string; tone: BadgeTone }> = {
  PENDING: { label: "Pending", tone: "warning" },
  REFERRED: { label: "Referred", tone: "primary" },
  COMPLETED: { label: "Completed", tone: "success" },
};

export function ReferralBadge({ status }: { status: ReferralStatus }) {
  const config = CONFIG[status];
  return <StatusBadge tone={config.tone}>{config.label}</StatusBadge>;
}

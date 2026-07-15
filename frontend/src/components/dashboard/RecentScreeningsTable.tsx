import { Construction } from "lucide-react";
import { Card } from "@/components/ui/Card";
import { SectionHeader } from "@/components/ui/SectionHeader";
import { EmptyState } from "@/components/ui/EmptyState";

/**
 * Explicitly labeled placeholder — per the project's "never invent
 * functionality" rule. DashboardSummary (Module 5) is aggregate-only and
 * has no per-screening listing; there is no backend endpoint today that
 * returns "recent screenings across the district" (GET /screenings/patient/{id}
 * requires already knowing a patient, which isn't the district-wide view
 * this table needs). Building this for real requires a backend addition —
 * e.g. GET /api/v1/screenings/recent — which is out of Module 9's stated
 * scope (visualize existing data only, no new backend logic).
 */
export function RecentScreeningsTable() {
  return (
    <Card>
      <SectionHeader title="Recent Screenings" description="Patient, village, confidence, risk, and referral status for the latest screenings" />
      <EmptyState
        icon={<Construction className="h-8 w-8" />}
        title="Not available yet"
        description="This table requires a district-wide 'recent screenings' endpoint that doesn't exist in the backend yet — GET /api/v1/dashboard is aggregate-only. Flagged as a backend fast-follow rather than built with fabricated data."
      />
    </Card>
  );
}

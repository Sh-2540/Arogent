import { User as UserIcon, MapPin } from "lucide-react";
import { Card } from "./Card";
import type { Patient, PatientSummary } from "@/lib/types";

export function PatientInfoCard({ patient }: { patient: Patient | PatientSummary }) {
  return (
    <Card className="flex items-center gap-4">
      <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-primary-50 text-primary-600">
        <UserIcon className="h-5 w-5" />
      </div>
      <div className="min-w-0">
        <p className="font-display truncate font-semibold text-neutral-900">{patient.full_name}</p>
        <div className="mt-0.5 flex items-center gap-3 text-sm text-neutral-500">
          <span>{patient.age} years</span>
          <span className="flex items-center gap-1">
            <MapPin className="h-3.5 w-3.5" />
            {patient.village}
          </span>
        </div>
      </div>
    </Card>
  );
}

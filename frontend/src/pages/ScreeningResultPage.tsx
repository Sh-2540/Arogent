import { useParams, Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { CheckCircle2, AlertTriangle } from "lucide-react";
import { AppShell } from "@/components/layout/AppShell";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/button";
import { ConfidenceBadge } from "@/components/ui/ConfidenceBadge";
import { RiskBadge } from "@/components/ui/RiskBadge";
import { ReferralBadge } from "@/components/ui/ReferralBadge";
import { ConfidenceFingerprint } from "@/components/ui/ConfidenceFingerprint";
import { PatientInfoCard } from "@/components/ui/PatientInfoCard";
import { LoadingState } from "@/components/ui/LoadingState";
import { ErrorBanner } from "@/components/ui/ErrorBanner";
import { getScreeningResult } from "@/api/screenings";
import { getPatient } from "@/api/patients";
import { ApiError } from "@/api/axios";
import { ConfidenceStatus } from "@/lib/constants";

/** Background/border tone for the recommendation banner — mirrors the tone
 * a judge should read the outcome as, at a glance, before reading any text. */
function recommendationTone(status: ConfidenceStatus | null): "success" | "warning" | "danger" {
  if (status === ConfidenceStatus.HIGH) return "success";
  if (status === ConfidenceStatus.NEEDS_REVIEW) return "danger";
  return "warning";
}

const TONE_CLASSES = {
  success: "bg-success-50 border-success-100 text-success-700",
  warning: "bg-warning-50 border-warning-100 text-warning-700",
  danger: "bg-danger-50 border-danger-100 text-danger-700",
};

export function ScreeningResultPage() {
  const { screeningId } = useParams<{ screeningId: string }>();
  const id = Number(screeningId);

  const {
    data: screening,
    isLoading: screeningLoading,
    error: screeningError,
  } = useQuery({
    queryKey: ["screenings", id],
    queryFn: () => getScreeningResult(id),
    enabled: Number.isFinite(id),
  });

  const { data: patient } = useQuery({
    queryKey: ["patients", screening?.patient_id],
    queryFn: () => getPatient(screening!.patient_id),
    enabled: !!screening,
  });

  if (screeningLoading) {
    return (
      <AppShell pageTitle="Screening Result">
        <LoadingState label="Loading screening result…" />
      </AppShell>
    );
  }

  if (screeningError || !screening) {
    const message = screeningError instanceof ApiError ? screeningError.message : "Unable to load this screening.";
    return (
      <AppShell pageTitle="Screening Result">
        <ErrorBanner message={message} />
      </AppShell>
    );
  }

  const tone = recommendationTone(screening.confidence_status);
  const showRisk = screening.confidence_status === ConfidenceStatus.HIGH && screening.risk_score !== null;

  return (
    <AppShell pageTitle="Screening Result">
      <div className="max-w-2xl space-y-5">
        {patient && <PatientInfoCard patient={patient} />}

        {/* --- The 10-second read: status + recommendation, impossible to miss --- */}
        <Card className={`border ${TONE_CLASSES[tone]}`}>
          <div className="flex items-start gap-3">
            {tone === "success" ? (
              <CheckCircle2 className="mt-0.5 h-6 w-6 shrink-0" aria-hidden="true" />
            ) : (
              <AlertTriangle className="mt-0.5 h-6 w-6 shrink-0" aria-hidden="true" />
            )}
            <div>
              <p className="text-base font-semibold">{screening.recommendation}</p>
              {screening.referral_status && (
                <div className="mt-2">
                  <ReferralBadge status={screening.referral_status} />
                </div>
              )}
            </div>
          </div>
        </Card>

        {/* --- Screening Confidence --- */}
        <Card>
          <div className="mb-4 flex items-center justify-between">
            <h2 className="font-display text-base font-semibold text-neutral-900">Screening Confidence</h2>
            {screening.confidence_status && <ConfidenceBadge status={screening.confidence_status} />}
          </div>

          {screening.confidence_score !== null && (
            <p className="font-data mb-4 text-3xl font-semibold text-neutral-900">
              {screening.confidence_score.toFixed(1)}%
            </p>
          )}

          {screening.confidence_breakdown && (
            <ConfidenceFingerprint breakdown={screening.confidence_breakdown} className="mb-4" />
          )}

          {screening.confidence_reasons.length > 0 && (
            <ul className="space-y-1.5 border-t border-neutral-100 pt-4">
              {screening.confidence_reasons.map((reason, i) => (
                <li key={i} className="text-sm text-neutral-600">
                  {reason}
                </li>
              ))}
            </ul>
          )}
        </Card>

        {/* --- Diabetes Risk (only ever shown for HIGH confidence — the gate, visible in the UI too) --- */}
        {showRisk && (
          <Card>
            <div className="mb-4 flex items-center justify-between">
              <h2 className="font-display text-base font-semibold text-neutral-900">Diabetes Risk</h2>
              {screening.risk_level && <RiskBadge level={screening.risk_level} />}
            </div>
            <p className="font-data text-3xl font-semibold text-neutral-900">{screening.risk_score?.toFixed(1)}%</p>
          </Card>
        )}

        {!showRisk && screening.confidence_status !== ConfidenceStatus.NEEDS_REVIEW && (
          <p className="text-center text-sm text-neutral-400">
            Diabetes risk is only predicted for HIGH-confidence screenings — Arogent Risk did not run for this
            screening.
          </p>
        )}

        <Link to="/screening/new">
          <Button variant="secondary" className="w-full">
            Start another screening
          </Button>
        </Link>
      </div>
    </AppShell>
  );
}

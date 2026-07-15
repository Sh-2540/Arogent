/**
 * Types mirroring backend Pydantic schemas exactly (field names and enum
 * values match app/schemas/*.py and app/core/enums.py 1:1). Keep these in
 * sync manually if the backend schemas change — there's no codegen step
 * in this hackathon build.
 */
import type { ConfidenceStatus, RiskLevel, ReferralStatus, UserRole } from "./constants";

export interface User {
  id: number;
  full_name: string;
  username: string;
  role: UserRole;
  assigned_village: string | null;
  created_at: string;
}

export interface AuthToken {
  access_token: string;
  token_type: string;
  user: User;
}

export interface Patient {
  id: number;
  full_name: string;
  age: number;
  gender: string;
  village: string;
  phone_number: string | null;
  date_of_birth: string | null;
  registered_by_id: number;
  registered_at: string;
}

export interface PatientSummary {
  id: number;
  full_name: string;
  age: number;
  village: string;
}

export interface ScreeningCreate {
  patient_id: number;
  blood_glucose_mg_dl: number;
  bmi: number;
  family_history_diabetes: boolean;
  physical_activity_level: "LOW" | "MODERATE" | "HIGH";
  symptoms: string[];
  village_at_screening: string;
  latitude?: number | null;
  longitude?: number | null;
}

export interface ConfidenceBreakdown {
  clinical_consistency_score: number;
  historical_consistency_score: number;
  behaviour_consistency_score: number;
  geographic_consistency_score: number;
}

export interface ScreeningResult {
  id: number;
  patient_id: number;
  screened_at: string;
  blood_glucose_mg_dl: number;
  bmi: number;
  confidence_score: number | null;
  confidence_status: ConfidenceStatus | null;
  confidence_breakdown: ConfidenceBreakdown | null;
  confidence_reasons: string[];
  risk_score: number | null;
  risk_level: RiskLevel | null;
  referral_status: ReferralStatus | null;
  recommendation: string;
}

export interface ScreeningSummary {
  id: number;
  patient_id: number;
  screened_at: string;
  confidence_status: ConfidenceStatus | null;
  risk_level: RiskLevel | null;
}

export interface Referral {
  id: number;
  patient_id: number;
  screening_id: number;
  phc: string;
  priority: string;
  reason: string;
  status: ReferralStatus;
  generated_at: string;
}

export interface StatusCount {
  status: string;
  count: number;
}

export interface VillageSummary {
  village: string;
  total_screenings: number;
  high_risk_count: number;
  needs_review_count: number;
  average_confidence_score: number;
}

export interface DashboardSummary {
  total_screenings: number;
  screenings_by_confidence_status: StatusCount[];
  screenings_by_risk_level: StatusCount[];
  pending_referrals_count: number;
  village_summaries: VillageSummary[];
}

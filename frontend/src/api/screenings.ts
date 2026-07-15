import { axiosInstance } from "./axios";
import type { ScreeningResult } from "@/lib/types";

/** Matches app.schemas.screening.ScreeningCreate exactly. */
export interface SubmitScreeningPayload {
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

export async function submitScreening(payload: SubmitScreeningPayload): Promise<ScreeningResult> {
  const response = await axiosInstance.post<ScreeningResult>("/screenings", payload);
  return response.data;
}

export async function getScreeningResult(screeningId: number): Promise<ScreeningResult> {
  const response = await axiosInstance.get<ScreeningResult>(`/screenings/${screeningId}`);
  return response.data;
}

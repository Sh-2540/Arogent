import { axiosInstance } from "./axios";
import type { Patient, PatientSummary } from "@/lib/types";

/**
 * Matches app.schemas.patient.PatientCreate exactly. "Address" and
 * "family_history_diabetes" are intentionally NOT here — the backend
 * Patient model doesn't have either field (family history is captured
 * per-screening, not as a patient demographic). See the Module 7
 * deliverables report for this gap.
 */
export interface RegisterPatientPayload {
  full_name: string;
  age: number;
  gender: string;
  village: string;
  phone_number?: string | null;
  date_of_birth?: string | null; // ISO date string, e.g. "1968-03-14"
}

export async function registerPatient(payload: RegisterPatientPayload): Promise<Patient> {
  const response = await axiosInstance.post<Patient>("/patients", payload);
  return response.data;
}

export async function searchPatients(params: { name?: string; village?: string }): Promise<PatientSummary[]> {
  const response = await axiosInstance.get<PatientSummary[]>("/patients", { params });
  return response.data;
}

export async function getPatient(patientId: number): Promise<Patient> {
  const response = await axiosInstance.get<Patient>(`/patients/${patientId}`);
  return response.data;
}

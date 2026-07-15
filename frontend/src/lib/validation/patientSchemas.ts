import { z } from "zod";

/**
 * Mirrors app.schemas.patient.PatientCreate exactly — see api/patients.ts
 * for the note on why "address" and "family_history_diabetes" aren't here.
 */
export const patientSchema = z.object({
  full_name: z.string().min(1, "Full name is required").max(150, "Full name is too long"),
  age: z.coerce
    .number({ message: "Age is required" })
    .int("Age must be a whole number")
    .min(0, "Age cannot be negative")
    .max(120, "Please check this age"),
  gender: z.string().min(1, "Please select a gender"),
  village: z.string().min(1, "Village is required").max(120, "Village name is too long"),
  phone_number: z
    .string()
    .regex(/^[6-9]\d{9}$/, "Enter a valid 10-digit mobile number")
    .optional()
    .or(z.literal("")),
  date_of_birth: z.string().optional().or(z.literal("")),
});

export type PatientFormValues = z.infer<typeof patientSchema>;
export type PatientFormInput = z.input<typeof patientSchema>;

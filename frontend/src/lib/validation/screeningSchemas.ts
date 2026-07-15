import { z } from "zod";

/** Mirrors app.schemas.screening.ScreeningCreate exactly, including the
 * backend's own bounds (gt 0/le 1000 for glucose, gt 0/le 100 for BMI). */
export const screeningSchema = z.object({
  patient_id: z.coerce.number({ message: "Select a patient first" }).int().positive(),
  blood_glucose_mg_dl: z.coerce
    .number({ message: "Blood glucose is required" })
    .gt(0, "Enter a glucose reading greater than 0")
    .max(1000, "Please check this reading"),
  bmi: z.coerce
    .number({ message: "BMI is required" })
    .gt(0, "Enter a BMI greater than 0")
    .max(100, "Please check this value"),
  family_history_diabetes: z.boolean(),
  physical_activity_level: z.enum(["LOW", "MODERATE", "HIGH"], {
    message: "Select a physical activity level",
  }),
  symptoms: z.array(z.string()),
  village_at_screening: z.string().min(1, "Village is required"),
  latitude: z.number().optional(),
  longitude: z.number().optional(),
});

export type ScreeningFormValues = z.infer<typeof screeningSchema>;
export type ScreeningFormInput = z.input<typeof screeningSchema>;

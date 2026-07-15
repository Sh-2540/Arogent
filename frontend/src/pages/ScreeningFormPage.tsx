import { useState } from "react";
import { useForm, Controller } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { MapPin } from "lucide-react";
import { AppShell } from "@/components/layout/AppShell";
import { Card } from "@/components/ui/Card";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";
import { Button } from "@/components/ui/button";
import { FormField } from "@/components/ui/FormField";
import { ErrorBanner } from "@/components/ui/ErrorBanner";
import { PatientSearchSelect } from "@/components/patients/PatientSearchSelect";
import { submitScreening } from "@/api/screenings";
import { ApiError } from "@/api/axios";
import { screeningSchema, type ScreeningFormInput } from "@/lib/validation/screeningSchemas";
import { SYMPTOM_OPTIONS } from "@/lib/symptoms";
import type { PatientSummary } from "@/lib/types";

function calculateBmi(heightCm: number, weightKg: number): number | null {
  if (heightCm <= 0 || weightKg <= 0) return null;
  const heightM = heightCm / 100;
  return Math.round((weightKg / (heightM * heightM)) * 10) / 10;
}

export function ScreeningFormPage() {
  const navigate = useNavigate();
  const [selectedPatient, setSelectedPatient] = useState<PatientSummary | null>(null);
  const [heightCm, setHeightCm] = useState("");
  const [weightKg, setWeightKg] = useState("");

  const {
    register,
    handleSubmit,
    control,
    setValue,
    formState: { errors },
  } = useForm<ScreeningFormInput>({
    resolver: zodResolver(screeningSchema),
    defaultValues: { family_history_diabetes: false, symptoms: [] },
  });

  const mutation = useMutation({
    mutationFn: submitScreening,
    onSuccess: (result) => {
      navigate(`/screening/${result.id}/result`);
    },
  });

  function handlePatientSelect(patient: PatientSummary | null) {
    setSelectedPatient(patient);
    setValue("patient_id", patient?.id ?? (undefined as unknown as number), { shouldValidate: true });
    if (patient) {
      setValue("village_at_screening", patient.village, { shouldValidate: true });
    }
  }

  function handleHeightWeightChange(newHeight: string, newWeight: string) {
    setHeightCm(newHeight);
    setWeightKg(newWeight);
    const computed = calculateBmi(Number(newHeight), Number(newWeight));
    if (computed !== null) {
      setValue("bmi", computed, { shouldValidate: true });
    }
  }

  function handleUseCurrentLocation() {
    if (!navigator.geolocation) return;
    navigator.geolocation.getCurrentPosition(
      (position) => {
        setValue("latitude", position.coords.latitude);
        setValue("longitude", position.coords.longitude);
      },
      () => {
        // Geolocation is optional — Arogent Verify's Geographic Consistency
        // signal already handles missing GPS gracefully (checks by village
        // name only), so a denied/failed permission is not an error state.
      }
    );
  }

  const apiError = mutation.error instanceof ApiError ? mutation.error.message : null;
  const networkError =
    mutation.error && !(mutation.error instanceof ApiError)
      ? "Unable to reach the server. Check your connection and try again."
      : null;

  return (
    <AppShell pageTitle="New Screening">
      <div className="max-w-lg space-y-4">
        <Card>
          <FormField label="Patient" htmlFor="patient-search" error={errors.patient_id?.message} required>
            <PatientSearchSelect selected={selectedPatient} onSelect={handlePatientSelect} />
          </FormField>
        </Card>

        {selectedPatient && (
          <Card>
            <form
              onSubmit={handleSubmit((values) => mutation.mutate(screeningSchema.parse(values)))}
              noValidate
              className="space-y-4"
            >
              <div className="grid grid-cols-2 gap-4">
                <FormField label="Height (cm)" htmlFor="height_cm">
                  <Input
                    id="height_cm"
                    type="number"
                    min={0}
                    value={heightCm}
                    onChange={(e) => handleHeightWeightChange(e.target.value, weightKg)}
                  />
                </FormField>
                <FormField label="Weight (kg)" htmlFor="weight_kg">
                  <Input
                    id="weight_kg"
                    type="number"
                    min={0}
                    value={weightKg}
                    onChange={(e) => handleHeightWeightChange(heightCm, e.target.value)}
                  />
                </FormField>
              </div>

              <FormField label="BMI" htmlFor="bmi" error={errors.bmi?.message} required>
                <Input id="bmi" type="number" step="0.1" min={0} max={100} aria-invalid={!!errors.bmi} {...register("bmi")} />
              </FormField>

              <FormField label="Blood glucose (mg/dL)" htmlFor="blood_glucose_mg_dl" error={errors.blood_glucose_mg_dl?.message} required>
                <Input
                  id="blood_glucose_mg_dl"
                  type="number"
                  step="0.1"
                  min={0}
                  max={1000}
                  aria-invalid={!!errors.blood_glucose_mg_dl}
                  {...register("blood_glucose_mg_dl")}
                />
              </FormField>

              <FormField label="Physical activity level" htmlFor="physical_activity_level" error={errors.physical_activity_level?.message} required>
                <Select id="physical_activity_level" defaultValue="" aria-invalid={!!errors.physical_activity_level} {...register("physical_activity_level")}>
                  <option value="" disabled>
                    Select activity level
                  </option>
                  <option value="LOW">Low</option>
                  <option value="MODERATE">Moderate</option>
                  <option value="HIGH">High</option>
                </Select>
              </FormField>

              <div className="flex items-center gap-2">
                <Checkbox id="family_history_diabetes" {...register("family_history_diabetes")} />
                <label htmlFor="family_history_diabetes" className="text-sm text-neutral-700">
                  Family history of diabetes
                </label>
              </div>

              <div>
                <span className="mb-1.5 block text-sm font-medium text-neutral-700">Symptoms</span>
                <Controller
                  name="symptoms"
                  control={control}
                  render={({ field }) => (
                    <div className="space-y-2">
                      {SYMPTOM_OPTIONS.map((symptom) => (
                        <div key={symptom.value} className="flex items-center gap-2">
                          <Checkbox
                            id={`symptom-${symptom.value}`}
                            checked={field.value?.includes(symptom.value) ?? false}
                            onChange={(e) => {
                              const current = field.value ?? [];
                              field.onChange(
                                e.target.checked
                                  ? [...current, symptom.value]
                                  : current.filter((s: string) => s !== symptom.value)
                              );
                            }}
                          />
                          <label htmlFor={`symptom-${symptom.value}`} className="text-sm text-neutral-700">
                            {symptom.label}
                          </label>
                        </div>
                      ))}
                    </div>
                  )}
                />
              </div>

              <FormField label="Village" htmlFor="village_at_screening" error={errors.village_at_screening?.message} required>
                <Input id="village_at_screening" aria-invalid={!!errors.village_at_screening} {...register("village_at_screening")} />
              </FormField>

              <button
                type="button"
                onClick={handleUseCurrentLocation}
                className="flex items-center gap-1.5 text-sm font-medium text-primary-600 hover:text-primary-700"
              >
                <MapPin className="h-3.5 w-3.5" aria-hidden="true" />
                Use current location (optional)
              </button>

              {(apiError || networkError) && <ErrorBanner message={apiError ?? networkError ?? ""} />}

              <Button type="submit" className="w-full" loading={mutation.isPending}>
                {mutation.isPending ? "Submitting…" : "Submit screening"}
              </Button>
            </form>
          </Card>
        )}
      </div>
    </AppShell>
  );
}

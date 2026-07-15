import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation } from "@tanstack/react-query";
import { CheckCircle2 } from "lucide-react";
import { AppShell } from "@/components/layout/AppShell";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { FormField } from "@/components/ui/FormField";
import { ErrorBanner } from "@/components/ui/ErrorBanner";
import { Card } from "@/components/ui/Card";
import { registerPatient } from "@/api/patients";
import { ApiError } from "@/api/axios";
import { patientSchema, type PatientFormInput } from "@/lib/validation/patientSchemas";
import type { Patient } from "@/lib/types";

function calculateAge(dateOfBirth: string): number | null {
  const dob = new Date(dateOfBirth);
  if (Number.isNaN(dob.getTime())) return null;
  const today = new Date();
  let age = today.getFullYear() - dob.getFullYear();
  const hasHadBirthdayThisYear =
    today.getMonth() > dob.getMonth() || (today.getMonth() === dob.getMonth() && today.getDate() >= dob.getDate());
  if (!hasHadBirthdayThisYear) age--;
  return age;
}

export function RegisterPatientPage() {
  const {
    register,
    handleSubmit,
    watch,
    setValue,
    reset,
    formState: { errors },
  } = useForm<PatientFormInput>({ resolver: zodResolver(patientSchema) });

  const dateOfBirth = watch("date_of_birth");

  const mutation = useMutation<Patient, unknown, PatientFormInput>({
    mutationFn: (values) =>
      registerPatient({
        full_name: values.full_name,
        age: Number(values.age),
        gender: values.gender,
        village: values.village,
        phone_number: values.phone_number || null,
        date_of_birth: values.date_of_birth || null,
      }),
  });

  function handleDateOfBirthChange(e: React.ChangeEvent<HTMLInputElement>) {
    const value = e.target.value;
    setValue("date_of_birth", value);
    const computedAge = value ? calculateAge(value) : null;
    if (computedAge !== null && computedAge >= 0) {
      setValue("age", computedAge, { shouldValidate: true });
    }
  }

  const apiError = mutation.error instanceof ApiError ? mutation.error.message : null;
  const networkError = mutation.error && !(mutation.error instanceof ApiError)
    ? "Unable to reach the server. Check your connection and try again."
    : null;

  return (
    <AppShell pageTitle="Register Patient">
      <div className="max-w-lg">
        {mutation.isSuccess ? (
          <Card className="flex flex-col items-center py-10 text-center">
            <div className="mb-3 flex h-12 w-12 items-center justify-center rounded-full bg-success-50 text-success-600">
              <CheckCircle2 className="h-6 w-6" aria-hidden="true" />
            </div>
            <h2 className="font-display text-lg font-semibold text-neutral-900">Patient registered</h2>
            <p className="mt-1 text-sm text-neutral-500">
              {mutation.data.full_name} has been added — Patient ID #{mutation.data.id}.
            </p>
            <Button
              variant="secondary"
              className="mt-5"
              onClick={() => {
                reset();
                mutation.reset();
              }}
            >
              Register another patient
            </Button>
          </Card>
        ) : (
          <Card>
            <form onSubmit={handleSubmit((values) => mutation.mutate(values))} noValidate className="space-y-4">
              <FormField label="Full name" htmlFor="full_name" error={errors.full_name?.message} required>
                <Input id="full_name" aria-invalid={!!errors.full_name} {...register("full_name")} />
              </FormField>

              <div className="grid grid-cols-2 gap-4">
                <FormField label="Date of birth" htmlFor="date_of_birth" error={errors.date_of_birth?.message}>
                  <Input
                    id="date_of_birth"
                    type="date"
                    max={new Date().toISOString().split("T")[0]}
                    value={dateOfBirth ?? ""}
                    onChange={handleDateOfBirthChange}
                  />
                </FormField>

                <FormField label="Age" htmlFor="age" error={errors.age?.message} required>
                  <Input id="age" type="number" min={0} max={120} aria-invalid={!!errors.age} {...register("age")} />
                </FormField>
              </div>

              <FormField label="Gender" htmlFor="gender" error={errors.gender?.message} required>
                <Select id="gender" defaultValue="" aria-invalid={!!errors.gender} {...register("gender")}>
                  <option value="" disabled>
                    Select gender
                  </option>
                  <option value="Female">Female</option>
                  <option value="Male">Male</option>
                  <option value="Other">Other</option>
                </Select>
              </FormField>

              <FormField label="Mobile number" htmlFor="phone_number" error={errors.phone_number?.message}>
                <Input
                  id="phone_number"
                  type="tel"
                  inputMode="numeric"
                  placeholder="10-digit mobile number"
                  aria-invalid={!!errors.phone_number}
                  {...register("phone_number")}
                />
              </FormField>

              <FormField label="Village" htmlFor="village" error={errors.village?.message} required>
                <Input id="village" aria-invalid={!!errors.village} {...register("village")} />
              </FormField>

              {(apiError || networkError) && <ErrorBanner message={apiError ?? networkError ?? ""} />}

              <Button type="submit" className="w-full" loading={mutation.isPending}>
                {mutation.isPending ? "Registering…" : "Register patient"}
              </Button>
            </form>
          </Card>
        )}
      </div>
    </AppShell>
  );
}

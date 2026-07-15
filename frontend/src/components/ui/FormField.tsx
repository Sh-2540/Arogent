import type { ReactNode } from "react";
import { Label } from "./label";

interface FormFieldProps {
  label: string;
  htmlFor: string;
  error?: string;
  required?: boolean;
  children: ReactNode;
}

/** Standardizes label + control + inline validation error across every
 * form in the app — every field in Login and Register Patient goes
 * through this, so error styling/spacing never has to be reinvented. */
export function FormField({ label, htmlFor, error, required, children }: FormFieldProps) {
  return (
    <div>
      <Label htmlFor={htmlFor}>
        {label}
        {required && <span className="ml-0.5 text-danger-600">*</span>}
      </Label>
      {children}
      {error && (
        <p id={`${htmlFor}-error`} role="alert" className="mt-1 text-xs text-danger-600">
          {error}
        </p>
      )}
    </div>
  );
}

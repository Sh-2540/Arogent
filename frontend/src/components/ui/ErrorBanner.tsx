import { AlertCircle } from "lucide-react";

/** Errors state what went wrong plainly, in the interface's voice — never
 * an apology, never vague. Used for both form-level and page-level errors. */
export function ErrorBanner({ message }: { message: string }) {
  return (
    <div className="flex items-start gap-2.5 rounded-lg bg-danger-50 px-4 py-3 text-sm text-danger-700 ring-1 ring-inset ring-danger-100">
      <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
      <span>{message}</span>
    </div>
  );
}

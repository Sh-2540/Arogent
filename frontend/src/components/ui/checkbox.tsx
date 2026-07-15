import * as React from "react";
import { Check } from "lucide-react";
import { cn } from "@/lib/utils";

export interface CheckboxProps extends Omit<React.ComponentProps<"input">, "type"> {}

export const Checkbox = React.forwardRef<HTMLInputElement, CheckboxProps>(
  ({ className, id, ...props }, ref) => {
    return (
      <span className="relative inline-flex h-4.5 w-4.5 shrink-0 items-center justify-center">
        <input
          ref={ref}
          id={id}
          type="checkbox"
          className={cn(
            "peer h-4.5 w-4.5 shrink-0 appearance-none rounded border border-neutral-300 bg-white",
            "checked:border-primary-600 checked:bg-primary-600",
            "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-600 focus-visible:ring-offset-1",
            "disabled:cursor-not-allowed disabled:opacity-50",
            className
          )}
          {...props}
        />
        <Check
          className="pointer-events-none absolute h-3 w-3 text-white opacity-0 peer-checked:opacity-100"
          aria-hidden="true"
        />
      </span>
    );
  }
);
Checkbox.displayName = "Checkbox";

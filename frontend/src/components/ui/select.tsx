import * as React from "react";
import { ChevronDown } from "lucide-react";
import { cn } from "@/lib/utils";

/**
 * A styled native <select>, not a Radix-based custom dropdown — deliberately
 * simpler and more accessible out of the box (native keyboard/screen-reader
 * support) than building a custom listbox, which matters more than visual
 * customization for a healthcare tool used in the field.
 */
export const Select = React.forwardRef<HTMLSelectElement, React.ComponentProps<"select">>(
  ({ className, children, ...props }, ref) => (
    <div className="relative">
      <select
        ref={ref}
        className={cn(
          "flex h-10 w-full appearance-none rounded-lg border border-neutral-300 bg-white px-3 py-2 pr-9 text-sm text-neutral-900",
          "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-600 focus-visible:ring-offset-1",
          "disabled:cursor-not-allowed disabled:opacity-50",
          "aria-invalid:border-danger-600 aria-invalid:ring-danger-100",
          className
        )}
        {...props}
      >
        {children}
      </select>
      <ChevronDown
        className="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-neutral-400"
        aria-hidden="true"
      />
    </div>
  )
);
Select.displayName = "Select";

import * as React from "react";
import { cn } from "@/lib/utils";

/**
 * Hand-built in shadcn/ui's exact convention (forwardRef, cn() merging,
 * same prop shape) rather than CLI-generated — the shadcn CLI needs
 * ui.shadcn.com, which isn't reachable in this environment. Functionally
 * and visually equivalent for a plain input; genuinely noting the
 * provenance rather than implying it came from the CLI.
 */
export const Input = React.forwardRef<HTMLInputElement, React.ComponentProps<"input">>(
  ({ className, type, ...props }, ref) => {
    return (
      <input
        type={type}
        ref={ref}
        className={cn(
          "flex h-10 w-full rounded-lg border border-neutral-300 bg-white px-3 py-2 text-sm text-neutral-900",
          "placeholder:text-neutral-400",
          "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-600 focus-visible:ring-offset-1",
          "disabled:cursor-not-allowed disabled:opacity-50",
          "aria-invalid:border-danger-600 aria-invalid:ring-danger-100",
          className
        )}
        {...props}
      />
    );
  }
);
Input.displayName = "Input";

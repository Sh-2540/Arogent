import type { ReactNode } from "react";
import { Inbox } from "lucide-react";

interface EmptyStateProps {
  title: string;
  description?: string;
  icon?: ReactNode;
  action?: ReactNode;
}

/** An empty screen is an invitation to act, not a dead end — always pairs
 * a plain-language explanation with something the person can do next. */
export function EmptyState({ title, description, icon, action }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-neutral-300 bg-neutral-50 px-6 py-12 text-center">
      <div className="mb-3 text-neutral-500">{icon ?? <Inbox className="h-8 w-8" />}</div>
      <h3 className="font-display text-base font-semibold text-neutral-700">{title}</h3>
      {description && <p className="mt-1 max-w-sm text-sm text-neutral-500">{description}</p>}
      {action && <div className="mt-4">{action}</div>}
    </div>
  );
}

import { Construction } from "lucide-react";
import { AppShell } from "@/components/layout/AppShell";
import { EmptyState } from "@/components/ui/EmptyState";

/**
 * Explicitly labeled placeholder — per the project's "never invent
 * functionality" rule. This exists only so login can be demonstrated for
 * PHC Officer and District Officer roles in Module 7, before their real
 * screens (Referrals in Module 8, Dashboard in Module 9) are built.
 */
export function PlaceholderPage({ pageTitle, moduleName }: { pageTitle: string; moduleName: string }) {
  return (
    <AppShell pageTitle={pageTitle}>
      <EmptyState
        icon={<Construction className="h-8 w-8" />}
        title={`${pageTitle} — coming in ${moduleName}`}
        description="This screen hasn't been built yet. You're logged in correctly, but there's nothing here to show until this module is implemented."
      />
    </AppShell>
  );
}

import { useState, type ReactNode } from "react";
import { Sidebar } from "./Sidebar";
import { TopBar } from "./TopBar";
import { useAuth } from "@/hooks/useAuth";

interface AppShellProps {
  pageTitle: string;
  children: ReactNode;
}

/** The layout every authenticated screen (Modules 7-9) renders inside —
 * Sidebar + TopBar are assembled once here, not re-implemented per screen.
 * Below the md breakpoint, Sidebar becomes a toggleable overlay drawer;
 * AppShell owns that open/close state since both TopBar (trigger) and
 * Sidebar (content) need to share it. */
export function AppShell({ pageTitle, children }: AppShellProps) {
  const { user } = useAuth();
  const [mobileNavOpen, setMobileNavOpen] = useState(false);

  if (!user) return null; // ProtectedRoute (Module 7) handles the redirect; this is just a safety net

  return (
    <div className="flex h-screen bg-neutral-50">
      <Sidebar role={user.role} mobileOpen={mobileNavOpen} onMobileClose={() => setMobileNavOpen(false)} />
      <div className="flex flex-1 flex-col overflow-hidden">
        <TopBar pageTitle={pageTitle} onMenuClick={() => setMobileNavOpen(true)} />
        <main className="flex-1 overflow-y-auto px-4 py-6 sm:px-8 sm:py-8">
          <div className="mx-auto max-w-5xl">{children}</div>
        </main>
      </div>
    </div>
  );
}

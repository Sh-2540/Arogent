import { NavLink } from "react-router-dom";
import { UserPlus, Stethoscope, ClipboardList, LayoutDashboard, Activity, X } from "lucide-react";
import { cn } from "@/lib/utils";
import { UserRole } from "@/lib/constants";
import type { UserRole as UserRoleType } from "@/lib/constants";

interface NavItem {
  to: string;
  label: string;
  icon: React.ReactNode;
}

const NAV_BY_ROLE: Record<UserRoleType, NavItem[]> = {
  [UserRole.ASHA]: [
    { to: "/patients/register", label: "Register Patient", icon: <UserPlus className="h-4 w-4" aria-hidden="true" /> },
    { to: "/screening/new", label: "New Screening", icon: <Stethoscope className="h-4 w-4" aria-hidden="true" /> },
  ],
  [UserRole.PHC_OFFICER]: [
    { to: "/referrals", label: "Referrals", icon: <ClipboardList className="h-4 w-4" aria-hidden="true" /> },
  ],
  [UserRole.DISTRICT_OFFICER]: [
    { to: "/dashboard", label: "District Dashboard", icon: <LayoutDashboard className="h-4 w-4" aria-hidden="true" /> },
  ],
};

interface SidebarProps {
  role: UserRoleType;
  /** Controls the mobile overlay drawer — desktop (md+) always shows the
   * sidebar regardless of this prop. AppShell owns the open/close state. */
  mobileOpen?: boolean;
  onMobileClose?: () => void;
}

export function Sidebar({ role, mobileOpen = false, onMobileClose }: SidebarProps) {
  const items = NAV_BY_ROLE[role] ?? [];

  const content = (
    <>
      <div className="flex items-center justify-between gap-2 px-5 py-5">
        <div className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary-600 text-white">
            <Activity className="h-4.5 w-4.5" aria-hidden="true" />
          </div>
          <span className="font-display text-lg font-semibold text-neutral-900">Arogent</span>
        </div>
        {/* Close button only ever renders in the mobile overlay */}
        {onMobileClose && (
          <button
            onClick={onMobileClose}
            className="rounded-lg p-1.5 text-neutral-500 hover:bg-neutral-100 md:hidden"
            aria-label="Close navigation menu"
          >
            <X className="h-4.5 w-4.5" aria-hidden="true" />
          </button>
        )}
      </div>

      <nav className="flex flex-1 flex-col gap-1 px-3">
        {items.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            onClick={onMobileClose}
            className={({ isActive }) =>
              cn(
                "flex items-center gap-2.5 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                isActive
                  ? "bg-primary-50 text-primary-700"
                  : "text-neutral-600 hover:bg-neutral-100 hover:text-neutral-900"
              )
            }
          >
            {item.icon}
            {item.label}
          </NavLink>
        ))}
      </nav>
    </>
  );

  return (
    <>
      {/* Desktop: static sidebar, always visible at md+ */}
      <aside className="hidden h-screen w-60 shrink-0 flex-col border-r border-neutral-200 bg-white md:flex">
        {content}
      </aside>

      {/* Mobile: overlay drawer — always mounted (not conditionally rendered)
       * so the slide-in/fade transitions below actually have something to
       * animate between; pointer-events-none when closed keeps it from
       * intercepting clicks or being tab-focusable while hidden. */}
      <div
        className={cn(
          "fixed inset-0 z-40 md:hidden",
          mobileOpen ? "pointer-events-auto" : "pointer-events-none"
        )}
        aria-hidden={!mobileOpen}
      >
        <div
          className={cn(
            "absolute inset-0 bg-neutral-900/40 transition-opacity duration-200 ease-out",
            mobileOpen ? "opacity-100" : "opacity-0"
          )}
          onClick={onMobileClose}
        />
        <aside
          className={cn(
            "relative flex h-screen w-64 flex-col bg-white shadow-lg transition-transform duration-200 ease-out",
            mobileOpen ? "translate-x-0" : "-translate-x-full"
          )}
        >
          {content}
        </aside>
      </div>
    </>
  );
}

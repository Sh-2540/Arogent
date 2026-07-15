import { LogOut, Menu } from "lucide-react";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { useAuth } from "@/hooks/useAuth";

const ROLE_LABEL: Record<string, string> = {
  ASHA: "ASHA Worker",
  PHC_OFFICER: "PHC Officer",
  DISTRICT_OFFICER: "District Officer",
};

export function TopBar({ pageTitle, onMenuClick }: { pageTitle: string; onMenuClick?: () => void }) {
  const { user, logout } = useAuth();

  return (
    <header className="flex h-16 items-center justify-between border-b border-neutral-200 bg-white px-4 sm:px-6">
      <div className="flex items-center gap-3">
        {onMenuClick && (
          <button
            onClick={onMenuClick}
            className="rounded-lg p-1.5 text-neutral-500 hover:bg-neutral-100 md:hidden"
            aria-label="Open navigation menu"
          >
            <Menu className="h-5 w-5" aria-hidden="true" />
          </button>
        )}
        <h1 className="font-display text-lg font-semibold text-neutral-900 sm:text-xl">{pageTitle}</h1>
      </div>

      {user && (
        <div className="flex items-center gap-3">
          <div className="hidden text-right sm:block">
            <p className="text-sm font-medium text-neutral-900">{user.full_name}</p>
            <StatusBadge tone="primary" className="mt-0.5">
              {ROLE_LABEL[user.role] ?? user.role}
            </StatusBadge>
          </div>
          <button
            onClick={logout}
            className="flex h-9 w-9 items-center justify-center rounded-lg text-neutral-500 hover:bg-neutral-100 hover:text-neutral-700"
            aria-label="Log out"
            title="Log out"
          >
            <LogOut className="h-4.5 w-4.5" aria-hidden="true" />
          </button>
        </div>
      )}
    </header>
  );
}

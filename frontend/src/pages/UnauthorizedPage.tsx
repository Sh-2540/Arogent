import { ShieldAlert } from "lucide-react";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/hooks/useAuth";

export function UnauthorizedPage() {
  const { logout } = useAuth();

  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-3 px-4 text-center">
      <ShieldAlert className="h-10 w-10 text-danger-600" aria-hidden="true" />
      <h1 className="font-display text-lg font-semibold text-neutral-900">You don't have access to this page</h1>
      <p className="max-w-sm text-sm text-neutral-500">
        Your account role doesn't have permission to view this screen. If you think this is a mistake, contact your
        district administrator.
      </p>
      <Link to="/">
        <Button variant="secondary" className="mt-2">
          Go to my home page
        </Button>
      </Link>
      <button onClick={logout} className="text-sm text-neutral-400 hover:text-neutral-600">
        Log out
      </button>
    </div>
  );
}

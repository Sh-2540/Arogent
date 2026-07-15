import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation } from "@tanstack/react-query";
import { useNavigate, useLocation, Navigate } from "react-router-dom";
import { Activity } from "lucide-react";
import { Input } from "@/components/ui/input";
import { PasswordInput } from "@/components/ui/PasswordInput";
import { Button } from "@/components/ui/button";
import { FormField } from "@/components/ui/FormField";
import { ErrorBanner } from "@/components/ui/ErrorBanner";
import { useAuth } from "@/hooks/useAuth";
import { loginSchema, type LoginFormValues } from "@/lib/validation/authSchemas";
import { ApiError } from "@/api/axios";
import { UserRole } from "@/lib/constants";

const ROLE_LANDING_ROUTE: Record<string, string> = {
  [UserRole.ASHA]: "/patients/register",
  [UserRole.PHC_OFFICER]: "/referrals",
  [UserRole.DISTRICT_OFFICER]: "/dashboard",
};

export function LoginPage() {
  const { login, isAuthenticated, user } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormValues>({ resolver: zodResolver(loginSchema) });

  const loginMutation = useMutation({
    mutationFn: (values: LoginFormValues) => login(values.username, values.password),
    onSuccess: () => {
      const from = (location.state as { from?: Location })?.from?.pathname;
      navigate(from ?? "/", { replace: true });
    },
  });

  // Already logged in (e.g. navigated back to /login manually) — bounce
  // straight to their landing route instead of showing the form again.
  if (isAuthenticated && user) {
    return <Navigate to={ROLE_LANDING_ROUTE[user.role] ?? "/"} replace />;
  }

  const apiError = loginMutation.error instanceof ApiError ? loginMutation.error.message : null;
  const networkError =
    loginMutation.error && !(loginMutation.error instanceof ApiError)
      ? "Unable to reach the server. Check your connection and try again."
      : null;

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-primary-50 via-white to-primary-100 px-4">
      <div className="w-full max-w-sm">
        <div className="mb-8 flex flex-col items-center">
          <div className="mb-3 flex h-12 w-12 items-center justify-center rounded-xl bg-primary-600 text-white">
            <Activity className="h-6 w-6" aria-hidden="true" />
          </div>
          <h1 className="font-display text-2xl font-semibold text-neutral-900">Arogent</h1>
          <p className="mt-1 text-sm text-neutral-500">Confidence-driven primary care intelligence</p>
        </div>

        <div className="rounded-xl border border-neutral-200 bg-white p-6 shadow-sm">
          <h2 className="font-display mb-4 text-lg font-semibold text-neutral-900">Sign in</h2>

          <form
            onSubmit={handleSubmit((values) => loginMutation.mutate(values))}
            noValidate
            className="space-y-4"
          >
            <FormField label="Username" htmlFor="username" error={errors.username?.message} required>
              <Input
                id="username"
                autoComplete="username"
                aria-invalid={!!errors.username}
                aria-describedby={errors.username ? "username-error" : undefined}
                {...register("username")}
              />
            </FormField>

            <FormField label="Password" htmlFor="password" error={errors.password?.message} required>
              <PasswordInput
                id="password"
                autoComplete="current-password"
                aria-invalid={!!errors.password}
                aria-describedby={errors.password ? "password-error" : undefined}
                {...register("password")}
              />
            </FormField>

            {(apiError || networkError) && <ErrorBanner message={apiError ?? networkError ?? ""} />}

            <Button type="submit" className="w-full" loading={loginMutation.isPending}>
              {loginMutation.isPending ? "Signing in…" : "Sign in"}
            </Button>
          </form>
        </div>
      </div>
    </div>
  );
}

import { Suspense, lazy } from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import { LoginPage } from "@/pages/LoginPage";
import { RegisterPatientPage } from "@/pages/RegisterPatientPage";
import { ScreeningFormPage } from "@/pages/ScreeningFormPage";
import { ScreeningResultPage } from "@/pages/ScreeningResultPage";
import { PlaceholderPage } from "@/pages/PlaceholderPage";
import { UnauthorizedPage } from "@/pages/UnauthorizedPage";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { LoadingState } from "@/components/ui/LoadingState";
import { useAuth } from "@/hooks/useAuth";
import { UserRole } from "@/lib/constants";

// Lazy-loaded: DashboardPage pulls in Recharts, the single largest
// dependency in the app (confirmed via the build's bundle-size warning in
// Module 9). ASHA and PHC Officer users never load this chunk at all.
const DashboardPage = lazy(() => import("@/pages/DashboardPage").then((m) => ({ default: m.DashboardPage })));

const ROLE_LANDING_ROUTE: Record<string, string> = {
  [UserRole.ASHA]: "/patients/register",
  [UserRole.PHC_OFFICER]: "/referrals",
  [UserRole.DISTRICT_OFFICER]: "/dashboard",
};

function RoleBasedRedirect() {
  const { user } = useAuth();
  if (!user) return <Navigate to="/login" replace />;
  return <Navigate to={ROLE_LANDING_ROUTE[user.role] ?? "/login"} replace />;
}

function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/unauthorized" element={<UnauthorizedPage />} />

      <Route
        path="/patients/register"
        element={
          <ProtectedRoute allowedRoles={[UserRole.ASHA]}>
            <RegisterPatientPage />
          </ProtectedRoute>
        }
      />

      <Route
        path="/screening/new"
        element={
          <ProtectedRoute allowedRoles={[UserRole.ASHA]}>
            <ScreeningFormPage />
          </ProtectedRoute>
        }
      />

      <Route
        path="/screening/:screeningId/result"
        element={
          <ProtectedRoute allowedRoles={[UserRole.ASHA]}>
            <ScreeningResultPage />
          </ProtectedRoute>
        }
      />

      <Route
        path="/referrals"
        element={
          <ProtectedRoute allowedRoles={[UserRole.PHC_OFFICER]}>
            <PlaceholderPage pageTitle="Referrals" moduleName="Module 8" />
          </ProtectedRoute>
        }
      />

      <Route
        path="/dashboard"
        element={
          <ProtectedRoute allowedRoles={[UserRole.DISTRICT_OFFICER]}>
            <Suspense fallback={<div className="flex min-h-screen items-center justify-center"><LoadingState label="Loading dashboard…" /></div>}>
              <DashboardPage />
            </Suspense>
          </ProtectedRoute>
        }
      />

      <Route
        path="/"
        element={
          <ProtectedRoute>
            <RoleBasedRedirect />
          </ProtectedRoute>
        }
      />

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default App;

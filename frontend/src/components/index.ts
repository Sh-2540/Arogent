/**
 * Central export point for all design-system components. Modules 7-9
 * should import from "@/components" rather than reaching into individual
 * files — keeps import lines short and means a component's internal file
 * location can change without touching every screen that uses it.
 */

// Layout
export { AppShell } from "./layout/AppShell";
export { TopBar } from "./layout/TopBar";
export { Sidebar } from "./layout/Sidebar";

// UI primitives
export { Card } from "./ui/Card";
export { MetricCard } from "./ui/MetricCard";
export { SectionHeader } from "./ui/SectionHeader";
export { EmptyState } from "./ui/EmptyState";
export { LoadingState } from "./ui/LoadingState";
export { ErrorBanner } from "./ui/ErrorBanner";
export { ConfirmationDialog } from "./ui/ConfirmationDialog";
export { PatientInfoCard } from "./ui/PatientInfoCard";
export { Input } from "./ui/input";
export { Label } from "./ui/label";
export { Button, type ButtonProps } from "./ui/button";
export { Select } from "./ui/select";
export { PasswordInput } from "./ui/PasswordInput";
export { FormField } from "./ui/FormField";

// Auth
export { ProtectedRoute } from "./auth/ProtectedRoute";

// Badges
export { StatusBadge, type BadgeTone } from "./ui/StatusBadge";
export { ConfidenceBadge } from "./ui/ConfidenceBadge";
export { RiskBadge } from "./ui/RiskBadge";
export { ReferralBadge } from "./ui/ReferralBadge";

// Signature element
export { ConfidenceFingerprint } from "./ui/ConfidenceFingerprint";

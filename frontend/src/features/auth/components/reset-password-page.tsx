import { ResetPasswordForm } from "@/features/auth/components/reset-password-form";

export function ResetPasswordPage() {
  return (
    <div className="w-full max-w-sm">
      <h1 className="mb-1 font-display text-2xl font-semibold">Choose a new password</h1>
      <p className="mb-6 text-sm text-ink-muted">Make it something you haven&apos;t used here before.</p>
      <ResetPasswordForm />
    </div>
  );
}

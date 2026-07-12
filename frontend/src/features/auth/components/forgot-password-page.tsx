import { ForgotPasswordForm } from "@/features/auth/components/forgot-password-form";

export function ForgotPasswordPage() {
  return (
    <div className="w-full max-w-sm">
      <h1 className="mb-1 font-display text-2xl font-semibold">Reset your password</h1>
      <p className="mb-6 text-sm text-ink-muted">
        Enter the email on your account and we&apos;ll send a reset link.
      </p>
      <ForgotPasswordForm />
    </div>
  );
}

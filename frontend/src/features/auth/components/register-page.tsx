import { RegisterForm } from "@/features/auth/components/register-form";

export function RegisterPage() {
  return (
    <div className="w-full max-w-sm">
      <h1 className="mb-1 font-display text-2xl font-semibold">Create your account</h1>
      <p className="mb-6 text-sm text-ink-muted">
        Free to start. No credit card, no algorithm left unvisualized.
      </p>
      <RegisterForm />
    </div>
  );
}

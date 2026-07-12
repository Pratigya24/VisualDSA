import { LoginForm } from "@/features/auth/components/login-form";

export function LoginPage() {
  return (
    <div className="w-full max-w-sm">
      <h1 className="mb-1 font-display text-2xl font-semibold">Welcome back</h1>
      <p className="mb-6 text-sm text-ink-muted">Sign in to keep tracing where you left off.</p>
      <LoginForm />
    </div>
  );
}

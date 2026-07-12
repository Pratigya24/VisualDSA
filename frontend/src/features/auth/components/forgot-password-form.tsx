import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { Link } from "react-router-dom";

import { useForgotPassword } from "@/features/auth/hooks/use-password-reset";
import { forgotPasswordSchema, type ForgotPasswordFormValues } from "@/features/auth/utils/validation";
import { Button } from "@/shared/components/button";
import { Input } from "@/shared/components/input";
import { Label } from "@/shared/components/label";

export function ForgotPasswordForm() {
  const forgotPassword = useForgotPassword();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ForgotPasswordFormValues>({ resolver: zodResolver(forgotPasswordSchema) });

  const onSubmit = handleSubmit((values) => {
    forgotPassword.mutate(values);
  });

  if (forgotPassword.isSuccess) {
    return (
      <p role="status" className="text-sm text-ink-muted">
        If an account exists for that email, a reset link is on its way. Check your inbox.
      </p>
    );
  }

  return (
    <form onSubmit={onSubmit} noValidate className="space-y-4">
      <div>
        <Label htmlFor="email">Email</Label>
        <Input
          id="email"
          type="email"
          autoComplete="email"
          error={errors.email?.message}
          {...register("email")}
        />
      </div>

      <Button type="submit" className="w-full" disabled={forgotPassword.isPending}>
        {forgotPassword.isPending ? "Sending…" : "Send reset link"}
      </Button>

      <p className="text-center text-sm text-ink-muted">
        <Link to="/login" className="font-medium text-trace hover:underline">
          Back to sign in
        </Link>
      </p>
    </form>
  );
}

import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { Link, useSearchParams } from "react-router-dom";

import { useResetPassword } from "@/features/auth/hooks/use-password-reset";
import { resetPasswordSchema, type ResetPasswordFormValues } from "@/features/auth/utils/validation";
import { Button } from "@/shared/components/button";
import { Input } from "@/shared/components/input";
import { Label } from "@/shared/components/label";
import { ApiError } from "@/services/api-client";

export function ResetPasswordForm() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token");
  const resetPassword = useResetPassword();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ResetPasswordFormValues>({ resolver: zodResolver(resetPasswordSchema) });

  if (!token) {
    return (
      <p role="alert" className="text-sm text-signal-danger">
        This reset link is missing its token. Request a new one from the{" "}
        <Link to="/forgot-password" className="font-medium text-trace hover:underline">
          forgot password
        </Link>{" "}
        page.
      </p>
    );
  }

  if (resetPassword.isSuccess) {
    return (
      <div className="space-y-3">
        <p role="status" className="text-sm text-signal-success">
          Your password has been reset.
        </p>
        <Link to="/login" className="text-sm font-medium text-trace hover:underline">
          Continue to sign in
        </Link>
      </div>
    );
  }

  const onSubmit = handleSubmit((values) => {
    resetPassword.mutate({ token, newPassword: values.newPassword });
  });

  return (
    <form onSubmit={onSubmit} noValidate className="space-y-4">
      <div>
        <Label htmlFor="newPassword">New password</Label>
        <Input
          id="newPassword"
          type="password"
          autoComplete="new-password"
          error={errors.newPassword?.message}
          {...register("newPassword")}
        />
        <p className="mt-1 text-xs text-ink-faint">
          At least 8 characters, with a letter and a digit.
        </p>
      </div>

      {resetPassword.isError && (
        <p role="alert" className="text-sm text-signal-danger">
          {resetPassword.error instanceof ApiError
            ? resetPassword.error.message
            : "This link may have expired. Request a new one."}
        </p>
      )}

      <Button type="submit" className="w-full" disabled={resetPassword.isPending}>
        {resetPassword.isPending ? "Resetting…" : "Reset password"}
      </Button>
    </form>
  );
}

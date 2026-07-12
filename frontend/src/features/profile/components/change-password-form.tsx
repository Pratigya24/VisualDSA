import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";

import { useChangePassword } from "@/features/profile/hooks/use-profile";
import {
  changePasswordFormSchema,
  type ChangePasswordFormValues,
} from "@/features/profile/utils/validation";
import { Button } from "@/shared/components/button";
import { Input } from "@/shared/components/input";
import { Label } from "@/shared/components/label";
import { ApiError } from "@/services/api-client";

export function ChangePasswordForm() {
  const changePassword = useChangePassword();

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<ChangePasswordFormValues>({ resolver: zodResolver(changePasswordFormSchema) });

  const onSubmit = handleSubmit((values) => {
    changePassword.mutate(
      { currentPassword: values.currentPassword, newPassword: values.newPassword },
      { onSuccess: () => reset() },
    );
  });

  return (
    <form onSubmit={onSubmit} className="space-y-4">
      <div>
        <Label htmlFor="currentPassword">Current password</Label>
        <Input
          id="currentPassword"
          type="password"
          autoComplete="current-password"
          error={errors.currentPassword?.message}
          {...register("currentPassword")}
        />
      </div>
      <div>
        <Label htmlFor="newPassword">New password</Label>
        <Input
          id="newPassword"
          type="password"
          autoComplete="new-password"
          error={errors.newPassword?.message}
          {...register("newPassword")}
        />
      </div>
      <div>
        <Label htmlFor="confirmPassword">Confirm new password</Label>
        <Input
          id="confirmPassword"
          type="password"
          autoComplete="new-password"
          error={errors.confirmPassword?.message}
          {...register("confirmPassword")}
        />
      </div>

      {changePassword.isError && (
        <p role="alert" className="text-sm text-signal-danger">
          {changePassword.error instanceof ApiError
            ? changePassword.error.message
            : "Something went wrong. Try again."}
        </p>
      )}
      {changePassword.isSuccess && (
        <p role="status" className="text-sm text-signal-success">
          Password updated.
        </p>
      )}

      <Button type="submit" size="sm" disabled={changePassword.isPending}>
        {changePassword.isPending ? "Updating…" : "Update password"}
      </Button>
    </form>
  );
}

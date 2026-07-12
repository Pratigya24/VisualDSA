import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { Link, useNavigate } from "react-router-dom";

import { GoogleAuthButton } from "@/features/auth/components/google-auth-button";
import { useRegister } from "@/features/auth/hooks/use-register";
import { registerSchema, type RegisterFormValues } from "@/features/auth/utils/validation";
import { Button } from "@/shared/components/button";
import { Input } from "@/shared/components/input";
import { Label } from "@/shared/components/label";
import { ApiError } from "@/services/api-client";

export function RegisterForm() {
  const navigate = useNavigate();
  const registerMutation = useRegister();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterFormValues>({ resolver: zodResolver(registerSchema) });

  const onSubmit = handleSubmit((values) => {
    registerMutation.mutate(values, {
      onSuccess: () => navigate("/app", { replace: true }),
    });
  });

  return (
    <form onSubmit={onSubmit} noValidate className="space-y-4">
      <div>
        <Label htmlFor="displayName">Name</Label>
        <Input
          id="displayName"
          autoComplete="name"
          error={errors.displayName?.message}
          {...register("displayName")}
        />
      </div>

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

      <div>
        <Label htmlFor="password">Password</Label>
        <Input
          id="password"
          type="password"
          autoComplete="new-password"
          error={errors.password?.message}
          {...register("password")}
        />
        <p className="mt-1 text-xs text-ink-faint">
          At least 8 characters, with a letter and a digit.
        </p>
      </div>

      {registerMutation.isError && (
        <p role="alert" className="text-sm text-signal-danger">
          {registerMutation.error instanceof ApiError
            ? registerMutation.error.message
            : "Something went wrong. Try again."}
        </p>
      )}

      <Button type="submit" className="w-full" disabled={registerMutation.isPending}>
        {registerMutation.isPending ? "Creating account…" : "Create account"}
      </Button>

      <div className="relative py-2 text-center text-xs text-ink-faint">
        <span className="relative z-10 bg-canvas px-2">or</span>
        <div className="absolute inset-x-0 top-1/2 h-px -translate-y-1/2 bg-canvas-border" />
      </div>

      <GoogleAuthButton />

      <p className="text-center text-sm text-ink-muted">
        Already have an account?{" "}
        <Link to="/login" className="font-medium text-trace hover:underline">
          Sign in
        </Link>
      </p>
    </form>
  );
}

import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { Link, useNavigate, useLocation } from "react-router-dom";

import { useLogin } from "@/features/auth/hooks/use-login";
import { GoogleAuthButton } from "@/features/auth/components/google-auth-button";
import { loginSchema, type LoginFormValues } from "@/features/auth/utils/validation";
import { Button } from "@/shared/components/button";
import { Input } from "@/shared/components/input";
import { Label } from "@/shared/components/label";
import { ApiError } from "@/services/api-client";

export function LoginForm() {
  const navigate = useNavigate();
  const location = useLocation();
  const login = useLogin();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormValues>({ resolver: zodResolver(loginSchema) });

  const redirectTo = (location.state as { from?: string } | null)?.from ?? "/app";

  const onSubmit = handleSubmit((values) => {
    login.mutate(values, {
      onSuccess: () => navigate(redirectTo, { replace: true }),
    });
  });

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

      <div>
        <div className="mb-1.5 flex items-center justify-between">
          <Label htmlFor="password" className="mb-0">
            Password
          </Label>
          <Link to="/forgot-password" className="text-xs text-trace hover:underline">
            Forgot password?
          </Link>
        </div>
        <Input
          id="password"
          type="password"
          autoComplete="current-password"
          error={errors.password?.message}
          {...register("password")}
        />
      </div>

      {login.isError && (
        <p role="alert" className="text-sm text-signal-danger">
          {login.error instanceof ApiError
            ? login.error.message
            : "Something went wrong. Try again."}
        </p>
      )}

      <Button type="submit" className="w-full" disabled={login.isPending}>
        {login.isPending ? "Signing in…" : "Sign in"}
      </Button>

      <div className="relative py-2 text-center text-xs text-ink-faint">
        <span className="relative z-10 bg-canvas px-2">or</span>
        <div className="absolute inset-x-0 top-1/2 h-px -translate-y-1/2 bg-canvas-border" />
      </div>

      <GoogleAuthButton />

      <p className="text-center text-sm text-ink-muted">
        Don&apos;t have an account?{" "}
        <Link to="/register" className="font-medium text-trace hover:underline">
          Create one
        </Link>
      </p>
    </form>
  );
}

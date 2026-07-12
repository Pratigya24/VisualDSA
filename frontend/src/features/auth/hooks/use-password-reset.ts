import { useMutation } from "@tanstack/react-query";

import { requestPasswordReset, resetPassword } from "@/features/auth/api/auth-api";
import type { ForgotPasswordPayload, ResetPasswordPayload } from "@/features/auth/types";

export function useForgotPassword() {
  return useMutation({
    mutationFn: (payload: ForgotPasswordPayload) => requestPasswordReset(payload),
  });
}

export function useResetPassword() {
  return useMutation({
    mutationFn: (payload: ResetPasswordPayload) => resetPassword(payload),
  });
}

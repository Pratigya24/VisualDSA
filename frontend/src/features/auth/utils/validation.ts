import { z } from "zod";

// Mirrors backend/app/schemas/auth.py exactly, so client-side validation
// never rejects (or accepts) something the API would decide differently —
// see RegisterRequest / ResetPasswordRequest password_has_letter_and_digit.
const passwordSchema = z
  .string()
  .min(8, "Password must be at least 8 characters")
  .max(128, "Password must be at most 128 characters")
  .refine((value) => /[a-zA-Z]/.test(value), "Password must contain at least one letter")
  .refine((value) => /\d/.test(value), "Password must contain at least one digit");

export const loginSchema = z.object({
  email: z.string().email("Enter a valid email address"),
  password: z.string().min(1, "Password is required"),
});
export type LoginFormValues = z.infer<typeof loginSchema>;

export const registerSchema = z.object({
  displayName: z.string().min(1, "Name is required").max(80, "Name must be at most 80 characters"),
  email: z.string().email("Enter a valid email address"),
  password: passwordSchema,
});
export type RegisterFormValues = z.infer<typeof registerSchema>;

export const forgotPasswordSchema = z.object({
  email: z.string().email("Enter a valid email address"),
});
export type ForgotPasswordFormValues = z.infer<typeof forgotPasswordSchema>;

export const resetPasswordSchema = z.object({
  newPassword: passwordSchema,
});
export type ResetPasswordFormValues = z.infer<typeof resetPasswordSchema>;

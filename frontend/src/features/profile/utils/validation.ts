import { z } from "zod";

export const profileFormSchema = z.object({
  displayName: z.string().min(1, "Name is required").max(80, "Name must be at most 80 characters"),
});
export type ProfileFormValues = z.infer<typeof profileFormSchema>;

const passwordSchema = z
  .string()
  .min(8, "Password must be at least 8 characters")
  .max(128, "Password must be at most 128 characters")
  .refine((value) => /[a-zA-Z]/.test(value), "Password must contain at least one letter")
  .refine((value) => /\d/.test(value), "Password must contain at least one digit");

export const changePasswordFormSchema = z
  .object({
    currentPassword: z.string().min(1, "Current password is required"),
    newPassword: passwordSchema,
    confirmPassword: z.string(),
  })
  .refine((data) => data.newPassword === data.confirmPassword, {
    message: "Passwords do not match",
    path: ["confirmPassword"],
  });
export type ChangePasswordFormValues = z.infer<typeof changePasswordFormSchema>;

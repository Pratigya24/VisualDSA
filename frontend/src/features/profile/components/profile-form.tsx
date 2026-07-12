import { zodResolver } from "@hookform/resolvers/zod";
import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";

import { useCurrentUser } from "@/features/auth/hooks/use-current-user";
import { useUpdateProfile } from "@/features/profile/hooks/use-profile";
import { profileFormSchema, type ProfileFormValues } from "@/features/profile/utils/validation";
import { Button } from "@/shared/components/button";
import { Input } from "@/shared/components/input";
import { Label } from "@/shared/components/label";

export function ProfileForm() {
  const { data: user } = useCurrentUser();
  const updateProfile = useUpdateProfile();
  const [savedMessage, setSavedMessage] = useState(false);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isDirty },
  } = useForm<ProfileFormValues>({
    resolver: zodResolver(profileFormSchema),
    values: user ? { displayName: user.displayName } : undefined,
  });

  useEffect(() => {
    if (savedMessage) {
      const timeout = setTimeout(() => setSavedMessage(false), 2500);
      return () => clearTimeout(timeout);
    }
  }, [savedMessage]);

  const onSubmit = handleSubmit((values) => {
    updateProfile.mutate(
      { displayName: values.displayName },
      {
        onSuccess: () => {
          setSavedMessage(true);
          reset(values);
        },
      },
    );
  });

  if (!user) return null;

  return (
    <form onSubmit={onSubmit} className="space-y-4">
      <div>
        <Label htmlFor="email">Email</Label>
        <Input id="email" value={user.email} disabled />
      </div>
      <div>
        <Label htmlFor="displayName">Display name</Label>
        <Input id="displayName" error={errors.displayName?.message} {...register("displayName")} />
      </div>
      <div className="flex items-center gap-3">
        <Button type="submit" size="sm" disabled={!isDirty || updateProfile.isPending}>
          {updateProfile.isPending ? "Saving…" : "Save changes"}
        </Button>
        {savedMessage && <span className="text-xs text-signal-success">Saved</span>}
      </div>
    </form>
  );
}

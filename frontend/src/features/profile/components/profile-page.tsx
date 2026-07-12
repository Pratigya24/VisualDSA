import { useCurrentUser } from "@/features/auth/hooks/use-current-user";
import { useDashboard } from "@/features/dashboard/hooks/use-dashboard";
import { ChangePasswordForm } from "@/features/profile/components/change-password-form";
import { ProfileForm } from "@/features/profile/components/profile-form";

export function ProfilePage() {
  const { data: user } = useCurrentUser();
  const { data: dashboard } = useDashboard();

  const initials = user?.displayName
    .split(" ")
    .map((part) => part[0])
    .slice(0, 2)
    .join("")
    .toUpperCase();

  return (
    <main className="mx-auto max-w-2xl px-6 py-8">
      <h1 className="mb-6 font-display text-2xl font-semibold">Profile & Settings</h1>

      <div className="mb-8 flex items-center gap-4">
        <div className="flex h-16 w-16 items-center justify-center overflow-hidden rounded-full bg-trace/20 text-lg font-semibold text-trace-strong">
          {user?.avatarUrl ? (
            <img src={user.avatarUrl} alt="" className="h-full w-full object-cover" />
          ) : (
            initials
          )}
        </div>
        <div className="flex gap-6 text-sm">
          <div>
            <p className="text-lg font-semibold text-ink">{dashboard?.totalSolved ?? "—"}</p>
            <p className="text-ink-muted">Solved</p>
          </div>
          <div>
            <p className="text-lg font-semibold text-ink">{user?.streakCount ?? "—"}</p>
            <p className="text-ink-muted">Day streak</p>
          </div>
        </div>
      </div>

      <section className="glass-surface mb-6 rounded-lg p-5">
        <h2 className="mb-4 text-sm font-medium text-ink-muted">Account</h2>
        <ProfileForm />
      </section>

      <section className="glass-surface rounded-lg p-5">
        <h2 className="mb-4 text-sm font-medium text-ink-muted">Change password</h2>
        <ChangePasswordForm />
      </section>
    </main>
  );
}

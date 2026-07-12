import * as DropdownMenu from "@radix-ui/react-dropdown-menu";
import { LogOut, User as UserIcon } from "lucide-react";
import { useNavigate } from "react-router-dom";

import { useCurrentUser } from "@/features/auth/hooks/use-current-user";
import { useLogout } from "@/features/auth/hooks/use-logout";

export function UserMenu() {
  const { data: user, isLoading } = useCurrentUser();
  const logout = useLogout();
  const navigate = useNavigate();

  if (isLoading || !user) {
    return <div className="h-8 w-8 animate-pulse-trace rounded-full bg-canvas-overlay" aria-hidden />;
  }

  const initials = user.displayName
    .split(" ")
    .map((part) => part[0])
    .slice(0, 2)
    .join("")
    .toUpperCase();

  return (
    <DropdownMenu.Root>
      <DropdownMenu.Trigger asChild>
        <button
          type="button"
          className="flex h-8 w-8 items-center justify-center overflow-hidden rounded-full bg-trace/20 text-xs font-semibold text-trace-strong"
          aria-label={`Account menu for ${user.displayName}`}
        >
          {user.avatarUrl ? (
            <img src={user.avatarUrl} alt="" className="h-full w-full object-cover" />
          ) : (
            initials
          )}
        </button>
      </DropdownMenu.Trigger>
      <DropdownMenu.Portal>
        <DropdownMenu.Content
          align="end"
          sideOffset={8}
          className="glass-surface z-50 min-w-[200px] rounded-md p-1 text-sm"
        >
          <div className="px-3 py-2">
            <p className="truncate font-medium text-ink">{user.displayName}</p>
            <p className="truncate text-xs text-ink-muted">{user.email}</p>
          </div>
          <DropdownMenu.Separator className="my-1 h-px bg-canvas-border" />
          <DropdownMenu.Item
            className="flex cursor-pointer items-center gap-2 rounded-sm px-3 py-2 text-ink-muted outline-none data-[highlighted]:bg-canvas-overlay data-[highlighted]:text-ink"
            onSelect={() => navigate("/app/profile")}
          >
            <UserIcon className="h-4 w-4" aria-hidden />
            Profile
          </DropdownMenu.Item>
          <DropdownMenu.Item
            className="flex cursor-pointer items-center gap-2 rounded-sm px-3 py-2 text-signal-danger outline-none data-[highlighted]:bg-canvas-overlay"
            onSelect={() => logout.mutate()}
          >
            <LogOut className="h-4 w-4" aria-hidden />
            {logout.isPending ? "Signing out…" : "Sign out"}
          </DropdownMenu.Item>
        </DropdownMenu.Content>
      </DropdownMenu.Portal>
    </DropdownMenu.Root>
  );
}

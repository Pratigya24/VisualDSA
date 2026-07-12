import { Bookmark, LayoutDashboard, type LucideIcon, Map, NotebookPen, PanelLeftClose, PanelLeftOpen } from "lucide-react";
import { NavLink, Outlet } from "react-router-dom";

import { UserMenu } from "@/features/auth/components/user-menu";
import { Button } from "@/shared/components/button";
import { useUIStore } from "@/store/ui-store";
import { cn } from "@/shared/utils/cn";

interface NavItem {
  to: string;
  label: string;
  icon: LucideIcon;
  end?: boolean;
}

// Grows as each feature module ships (Problems catalog in Module 3, AI Mentor
// in Module 6, ...) — the shell itself never changes to accommodate a new
// entry, only this list does.
const NAV_ITEMS: NavItem[] = [
  { to: "/app", label: "Dashboard", icon: LayoutDashboard, end: true },
  { to: "/app/roadmap", label: "Roadmap", icon: Map },
  { to: "/app/bookmarks", label: "Bookmarks", icon: Bookmark },
  { to: "/app/notes", label: "Notes", icon: NotebookPen },
];

/**
 * Shell for every authenticated route. Feature pages render into <Outlet/>;
 * this layout owns only the persistent chrome (sidebar + topbar), never
 * feature-specific content.
 */
export function AppLayout() {
  const isSidebarCollapsed = useUIStore((state) => state.isSidebarCollapsed);
  const toggleSidebar = useUIStore((state) => state.toggleSidebar);

  return (
    <div className="flex min-h-screen bg-canvas">
      <aside
        className={cn(
          "flex flex-col border-r border-canvas-border bg-canvas-raised transition-[width] duration-200",
          isSidebarCollapsed ? "w-16" : "w-64",
        )}
        aria-label="Primary navigation"
      >
        <div className="flex h-14 items-center justify-between border-b border-canvas-border px-4">
          {!isSidebarCollapsed && (
            <span className="font-display text-sm font-semibold tracking-tight">VisualDSA AI</span>
          )}
          <Button
            variant="ghost"
            size="icon"
            onClick={toggleSidebar}
            aria-label={isSidebarCollapsed ? "Expand sidebar" : "Collapse sidebar"}
          >
            {isSidebarCollapsed ? (
              <PanelLeftOpen className="h-4 w-4" aria-hidden />
            ) : (
              <PanelLeftClose className="h-4 w-4" aria-hidden />
            )}
          </Button>
        </div>
        <nav className="flex-1 space-y-1 px-2 py-3">
          {NAV_ITEMS.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) =>
                cn(
                  "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                  isActive
                    ? "bg-trace/15 text-trace-strong"
                    : "text-ink-muted hover:bg-canvas-overlay hover:text-ink",
                )
              }
            >
              <item.icon className="h-4 w-4 shrink-0" aria-hidden />
              {!isSidebarCollapsed && <span>{item.label}</span>}
            </NavLink>
          ))}
        </nav>
      </aside>

      <div className="flex flex-1 flex-col">
        <header className="flex h-14 items-center justify-end border-b border-canvas-border px-6">
          <UserMenu />
        </header>
        <div className="flex-1">
          <Outlet />
        </div>
      </div>
    </div>
  );
}

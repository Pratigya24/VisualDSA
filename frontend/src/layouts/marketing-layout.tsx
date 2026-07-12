import { Link, Outlet } from "react-router-dom";

import { Button } from "@/shared/components/button";

export function MarketingLayout() {
  return (
    <div className="flex min-h-screen flex-col bg-canvas">
      <header className="flex h-16 items-center justify-between border-b border-canvas-border px-6 md:px-10">
        <Link to="/" className="font-display text-base font-semibold tracking-tight">
          VisualDSA AI
        </Link>
        <div className="flex items-center gap-3">
          <Button asChild variant="ghost" size="sm">
            <Link to="/login">Log in</Link>
          </Button>
          <Button asChild variant="primary" size="sm">
            <Link to="/register">Get started</Link>
          </Button>
        </div>
      </header>
      <div className="flex-1">
        <Outlet />
      </div>
    </div>
  );
}

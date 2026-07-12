import { Outlet } from "react-router-dom";

export function AuthLayout() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-canvas px-4">
      <div className="w-full max-w-sm">
        <div className="mb-8 flex items-center justify-center gap-2">
          <span className="h-2 w-2 rounded-full bg-trace" aria-hidden />
          <span className="font-display text-base font-semibold tracking-tight">VisualDSA AI</span>
        </div>
        <div className="glass-surface rounded-lg p-6">
          <Outlet />
        </div>
      </div>
    </div>
  );
}

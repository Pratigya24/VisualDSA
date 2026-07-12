import { Loader2 } from "lucide-react";
import { Navigate, Outlet, useLocation } from "react-router-dom";

import { useAuthSessionStore } from "@/features/auth/store/auth-session-store";

/**
 * Gates every route nested under it on `useAuthSessionStore().status`.
 *
 * - "idle" / "loading": the silent-refresh bootstrap (see
 *   use-auth-bootstrap.ts) hasn't resolved yet — render a full-screen
 *   loading state rather than flashing the login page for users who do
 *   have a valid session.
 * - "unauthenticated": redirect to /login, remembering the attempted
 *   location so LoginForm can send the user back afterwards.
 * - "authenticated": render the protected subtree via <Outlet/>.
 */
export function ProtectedRoute() {
  const status = useAuthSessionStore((state) => state.status);
  const location = useLocation();

  if (status === "idle" || status === "loading") {
    return (
      <div className="flex min-h-screen items-center justify-center" role="status" aria-live="polite">
        <Loader2 className="h-6 w-6 animate-spin text-trace" aria-hidden />
        <span className="sr-only">Checking your session…</span>
      </div>
    );
  }

  if (status === "unauthenticated") {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  }

  return <Outlet />;
}

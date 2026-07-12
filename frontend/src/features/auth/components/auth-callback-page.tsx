import { useEffect, useRef } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";

import { setAccessToken } from "@/services/api-client";
import { useAuthSessionStore } from "@/features/auth/store/auth-session-store";

/**
 * Landing point for GET /api/v1/auth/google/callback's redirect. The backend
 * has already set the httpOnly refresh cookie; this page's only job is to
 * pick the short-lived access_token out of the query string, put it in
 * memory, and hand off to the authenticated shell. The token never touches
 * storage, and the query param is stripped as soon as we navigate away.
 *
 * Token application and the resulting navigation happen inside a single
 * effect, in order, via an imperative `navigate()` call — deliberately not
 * via a render-returned <Navigate>, whose own effect could otherwise fire
 * before this component's effect and race the token being set.
 */
export function AuthCallbackPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const setStatus = useAuthSessionStore((state) => state.setStatus);
  const handled = useRef(false);

  useEffect(() => {
    if (handled.current) return;
    handled.current = true;

    const token = searchParams.get("access_token");
    if (token) {
      setAccessToken(token);
      setStatus("authenticated");
      navigate("/app", { replace: true });
    } else {
      setStatus("unauthenticated");
      navigate("/login", { replace: true, state: { error: "Google sign-in did not complete." } });
    }
  }, [searchParams, setStatus, navigate]);

  return (
    <p role="status" className="p-6 text-sm text-ink-muted">
      Finishing sign-in…
    </p>
  );
}

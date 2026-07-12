import { useEffect, useRef } from "react";

import { refreshSession } from "@/features/auth/api/auth-api";
import { useAuthSessionStore } from "@/features/auth/store/auth-session-store";

/**
 * Runs once when the app shell mounts. The access token is memory-only and
 * does not survive a page reload, but the refresh token is an httpOnly
 * cookie the browser sends automatically — so on load we attempt one silent
 * `/auth/refresh` call to find out whether this browser already has a valid
 * session, without ever asking the user to log in again unnecessarily.
 */
export function useAuthBootstrap(): void {
  const setStatus = useAuthSessionStore((state) => state.setStatus);
  const hasRun = useRef(false);

  useEffect(() => {
    if (hasRun.current) return;
    hasRun.current = true;

    setStatus("loading");
    refreshSession()
      .then(() => setStatus("authenticated"))
      .catch(() => setStatus("unauthenticated"));
  }, [setStatus]);
}

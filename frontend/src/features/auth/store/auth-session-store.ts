import { create } from "zustand";

/**
 * Holds only the *session bootstrap* status for this tab — not the user
 * object itself. The user object is server data and lives in the
 * `['auth', 'me']` TanStack Query cache (see use-current-user.ts), per the
 * State Management Strategy (architecture §13): server data is never
 * duplicated into Zustand.
 *
 * This store exists because "do we have a valid session yet" is genuinely
 * client/tab-local state: the access token lives only in memory (see
 * api-client.ts) and is lost on every page reload, so on mount the app must
 * attempt a silent refresh against the httpOnly cookie before it knows
 * whether to render the authenticated shell or the marketing/auth shell.
 * `ProtectedRoute` and the router read `status`, not any query, to avoid a
 * flash of the wrong shell while that refresh is in flight.
 */
export type AuthStatus = "idle" | "loading" | "authenticated" | "unauthenticated";

interface AuthSessionState {
  status: AuthStatus;
  setStatus: (status: AuthStatus) => void;
}

export const useAuthSessionStore = create<AuthSessionState>((set) => ({
  status: "idle",
  setStatus: (status) => set({ status }),
}));

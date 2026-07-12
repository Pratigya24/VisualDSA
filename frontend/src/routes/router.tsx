import { createBrowserRouter, Navigate } from "react-router-dom";

import { AppLayout } from "@/layouts/app-layout";
import { AuthLayout } from "@/layouts/auth-layout";
import { MarketingLayout } from "@/layouts/marketing-layout";
import { SystemStatusPage } from "@/features/system-status/components/system-status-page";
import { AuthCallbackPage } from "@/features/auth/components/auth-callback-page";
import { ForgotPasswordPage } from "@/features/auth/components/forgot-password-page";
import { LoginPage } from "@/features/auth/components/login-page";
import { ProtectedRoute } from "@/features/auth/components/protected-route";
import { RegisterPage } from "@/features/auth/components/register-page";
import { ResetPasswordPage } from "@/features/auth/components/reset-password-page";
import { DashboardPage } from "@/features/dashboard/components/dashboard-page";
import { RoadmapPage } from "@/features/roadmap/components/roadmap-page";
import { TopicDetailPage } from "@/features/roadmap/components/topic-detail-page";
import { NotesPage } from "@/features/notes/components/notes-page";
import { BookmarksPage } from "@/features/bookmarks/components/bookmarks-page";
import { ProfilePage } from "@/features/profile/components/profile-page";

/**
 * Route tree.
 *
 * Auth routes live under AuthLayout. Everything under /app is gated by
 * ProtectedRoute, which reads session status from useAuthSessionStore.
 * Each feature module adds its own children under "/app" without touching
 * the guard or the shell — Module 3/4 (problem detail + visualizer) will
 * add "/app/problems/:slug" here the same way.
 */
export const router = createBrowserRouter([
  {
    element: <MarketingLayout />,
    children: [{ path: "/", element: <SystemStatusPage /> }],
  },
  {
    element: <AuthLayout />,
    children: [
      { path: "/login", element: <LoginPage /> },
      { path: "/register", element: <RegisterPage /> },
      { path: "/forgot-password", element: <ForgotPasswordPage /> },
      { path: "/reset-password", element: <ResetPasswordPage /> },
    ],
  },
  { path: "/auth/callback", element: <AuthCallbackPage /> },
  {
    element: <ProtectedRoute />,
    children: [
      {
        element: <AppLayout />,
        path: "/app",
        children: [
          { index: true, element: <DashboardPage /> },
          { path: "roadmap", element: <RoadmapPage /> },
          { path: "roadmap/:slug", element: <TopicDetailPage /> },
          { path: "notes", element: <NotesPage /> },
          { path: "bookmarks", element: <BookmarksPage /> },
          { path: "profile", element: <ProfilePage /> },
          { path: "*", element: <Navigate to="/app" replace /> },
        ],
      },
    ],
  },
]);

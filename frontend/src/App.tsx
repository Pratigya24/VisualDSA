import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { RouterProvider } from "react-router-dom";

import { useAuthBootstrap } from "@/features/auth/hooks/use-auth-bootstrap";
import { router } from "@/routes/router";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30_000,
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

function AuthBootstrapGate() {
  // Attempts a silent token refresh once on load, before the router renders
  // any route that depends on knowing the session state (ProtectedRoute).
  useAuthBootstrap();
  return <RouterProvider router={router} />;
}

export function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthBootstrapGate />
    </QueryClientProvider>
  );
}

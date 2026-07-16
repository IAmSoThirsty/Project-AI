import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useState } from "react";
import { RouterProvider, createBrowserRouter } from "react-router-dom";

import { ControlCenterShell } from "./app-shell";
import { AuthGate, AuthProvider, EntryRedirect } from "./auth-context";
import { AuditRoute } from "./routes/AuditRoute";
import { AdministrationRoute } from "./routes/AdministrationRoute";
import { AtlasReplayRoute } from "./routes/AtlasReplayRoute";
import { AtlasProjectionsRoute } from "./routes/AtlasProjectionsRoute";
import { RecoveryRoute, SetupRoute, SignInRoute } from "./routes/AuthRoutes";
import { CommandCenterRoute } from "./routes/CommandCenterRoute";
import { EvidenceRoute } from "./routes/EvidenceRoute";
import { RouteError } from "./routes/RouteError";
import { PreferencesRoute } from "./routes/PreferencesRoute";
import { SecurityRoute } from "./routes/SecurityRoute";
import { SwrRoute } from "./routes/SwrRoute";
import { TaarRoute } from "./routes/TaarRoute";
import {
  GovernanceCatalogRoute,
  SecurityCatalogRoute,
  SimulationCatalogRoute,
  SystemHealthRoute,
  WorkQueueRoute,
} from "./routes/ProductRoutes";

function createControlCenterRouter() {
  return createBrowserRouter([
    { path: "/sign-in", element: <SignInRoute />, errorElement: <RouteError /> },
    { path: "/setup", element: <SetupRoute />, errorElement: <RouteError /> },
    { path: "/recover", element: <RecoveryRoute />, errorElement: <RouteError /> },
    {
      path: "/",
      element: <AuthGate><ControlCenterShell /></AuthGate>,
      errorElement: <RouteError />,
      children: [
        { index: true, element: <EntryRedirect /> },
        { path: "command-center", element: <CommandCenterRoute /> },
        { path: "evidence", element: <EvidenceRoute /> },
        { path: "evidence/audit", element: <AuditRoute /> },
        { path: "profile/security", element: <SecurityRoute /> },
        { path: "profile/preferences", element: <PreferencesRoute /> },
        { path: "administration/accounts", element: <AdministrationRoute /> },
        { path: "inbox", element: <WorkQueueRoute mode="inbox" /> },
        { path: "requests", element: <WorkQueueRoute mode="requests" /> },
        { path: "governance", element: <GovernanceCatalogRoute /> },
        { path: "security", element: <SecurityCatalogRoute /> },
        { path: "simulations", element: <SimulationCatalogRoute /> },
        { path: "simulations/swr", element: <SwrRoute /> },
        { path: "simulations/atlas-replay", element: <AtlasReplayRoute /> },
        { path: "simulations/atlas-projections", element: <AtlasProjectionsRoute /> },
        { path: "simulations/taar", element: <TaarRoute /> },
        { path: "system/health", element: <SystemHealthRoute /> },
      ],
    },
  ]);
}

export function ControlCenterApp() {
  const [router] = useState(createControlCenterRouter);
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: { retry: 1, staleTime: 15_000, refetchOnWindowFocus: false },
        },
      }),
  );
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider><RouterProvider router={router} /></AuthProvider>
    </QueryClientProvider>
  );
}

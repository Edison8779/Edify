/**
 * Edify Admin — Application Router.
 *
 * Defines all admin routes. Protected routes will be wrapped
 * with an auth guard in Phase 2.
 */

import { createBrowserRouter } from "react-router-dom";

// Placeholder pages — built in Phase 4 (React Admin Web V1)
// import { DashboardPage } from "../features/dashboard/DashboardPage";
// import { LoginPage } from "../features/auth/LoginPage";
// import { SongsPage } from "../features/songs/SongsPage";
// import { AuditLogsPage } from "../features/audit/AuditLogsPage";

export const router = createBrowserRouter([
  {
    path: "/",
    // element: <RootLayout />,
    children: [
      {
        index: true,
        // element: <DashboardPage />,
      },
    ],
  },
  {
    path: "/login",
    // element: <LoginPage />,
  },
]);

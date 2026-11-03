import type { ReactNode } from "react";
import { Navigate, Route, Routes } from "react-router";
import { useAuth } from "./lib/auth";
import { Layout } from "./components/Layout";
import { Loading } from "./components/ui";
import { LoginPage } from "./pages/Login";
import { RegisterPage } from "./pages/Register";
import { DashboardPage } from "./pages/Dashboard";
import { TillPage } from "./pages/Till";
import { LibraryPage } from "./pages/Library";
import { BooksPage } from "./pages/Books";
import { CustomersPage } from "./pages/Customers";
import { SalesPage } from "./pages/Sales";
import { SettingsPage } from "./pages/Settings";
import { UsersPage } from "./pages/Users";
import { AccountPage } from "./pages/Account";

function RequireStaff({ children }: { children: ReactNode }) {
  const { isStaff } = useAuth();
  return isStaff ? children : <Navigate to="/" replace />;
}

function RequireAdmin({ children }: { children: ReactNode }) {
  const { isAdmin } = useAuth();
  return isAdmin ? children : <Navigate to="/" replace />;
}

export function App() {
  const { user, loading, isStaff } = useAuth();

  if (loading) {
    return (
      <div className="center-screen">
        <Loading label="Opening the shop…" />
      </div>
    );
  }

  if (!user) {
    return (
      <Routes>
        <Route path="/register" element={<RegisterPage />} />
        <Route path="*" element={<LoginPage />} />
      </Routes>
    );
  }

  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={isStaff ? <DashboardPage /> : <AccountPage />} />
        <Route path="till" element={<RequireStaff><TillPage /></RequireStaff>} />
        <Route path="library" element={<RequireStaff><LibraryPage /></RequireStaff>} />
        <Route path="books" element={<RequireStaff><BooksPage /></RequireStaff>} />
        <Route path="customers" element={<RequireStaff><CustomersPage /></RequireStaff>} />
        <Route path="sales" element={<RequireStaff><SalesPage /></RequireStaff>} />
        <Route path="settings" element={<RequireStaff><SettingsPage /></RequireStaff>} />
        <Route path="users" element={<RequireAdmin><UsersPage /></RequireAdmin>} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}
